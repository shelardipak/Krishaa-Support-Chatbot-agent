from __future__ import annotations

import uuid
from typing import Callable, Dict, List, Optional

from app.agent.judge import judge_context
from app.agent.lead_capture import LeadCaptureState, detect_protected_request, is_valid_contact_number, is_valid_email
from app.agent.memory import ConversationMemory
from app.agent.prompts import DEFAULT_PROMPT
from app.agent.response_builder import build_response
from app.agent.safety import safety_check
from app.agent.tools import EscalationTool, ProductRetrievalTool, SourceFormatterTool, route_tool
from app.logging_config import get_logger
from app.notifications.email import LeadEmailNotifier
from app.retrieval.qdrant_client import QdrantClientAdapter
from app.schemas import AgentResponse, RetrievalItem

logger = get_logger("rag_agent")


class RAGAgent:
    def __init__(self, memory: ConversationMemory | None = None, email_notifier: LeadEmailNotifier | None = None):
        self.memory = memory or ConversationMemory()
        self.email_notifier = email_notifier or LeadEmailNotifier()
        self.retriever = QdrantClientAdapter()
        self.product_tool = ProductRetrievalTool(self.retriever)
        self.escalation_tool = EscalationTool()
        self.formatter_tool = SourceFormatterTool()

    def chat(
        self,
        user_message: str,
        vendor: str | None = None,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Dict[str, object]:
        def report(value: float, description: str) -> None:
            if progress_callback:
                progress_callback(value, description)

        report(0.08, "Checking your question")
        self.memory.add_turn("user", user_message)

        if self.memory.lead_capture:
            report(0.55, "Processing your contact details")
            return self._handle_lead_capture(user_message, report)

        requested_item = detect_protected_request(user_message)
        if requested_item:
            self.memory.lead_capture = LeadCaptureState(
                requested_item=requested_item,
                original_request=user_message.strip(),
            )
            return self._lead_response(
                "Before I can help with your request for "
                f"**{requested_item}**, I need a few contact details. We will use them to follow up on this request.\n\n"
                "Please complete the contact form below with your **Full Name**, **Email Address**, "
                "**Contact Number**, and **Company Name**.",
                report,
            )

        safety = safety_check(user_message)
        if not safety.is_safe:
            report(0.72, "Preparing a safe response")
            response = build_response(user_message, [], trace_id=str(uuid.uuid4())[:8])
            self.memory.add_turn("assistant", response.answer)
            report(1.0, "Response ready")
            return response.to_dict()

        report(0.24, "Searching product documentation")
        retrieval_items = self.product_tool.run(user_message, vendor=vendor, limit=3)
        report(0.55, f"Reviewing {len(retrieval_items)} relevant document chunks")
        tool_name = route_tool(user_message, retrieval_items)
        if tool_name == self.escalation_tool.name:
            report(0.72, "Preparing a grounded response")
            response = build_response(user_message, retrieval_items, trace_id=str(uuid.uuid4())[:8])
            self.memory.add_turn("assistant", response.answer)
            report(1.0, "Response ready")
            return response.to_dict()

        sufficient, reason = judge_context(retrieval_items, user_message)
        if not sufficient:
            report(0.72, "Preparing a grounded response")
            response = build_response(user_message, retrieval_items, trace_id=str(uuid.uuid4())[:8])
            self.memory.add_turn("assistant", response.answer)
            report(1.0, "Response ready")
            return response.to_dict()

        selected_prompt = DEFAULT_PROMPT
        report(0.72, "Generating an answer from retrieved context")
        response = build_response(user_message, retrieval_items, trace_id=str(uuid.uuid4())[:8])
        self.memory.add_turn("assistant", response.answer)
        report(1.0, "Response ready")
        return response.to_dict()

    def submit_lead_form(
        self,
        full_name: str,
        email: str,
        contact_number: str,
        company_name: str,
    ) -> Dict[str, object]:
        report = lambda _value, _description: None
        lead = self.memory.lead_capture
        if lead is None:
            return self._lead_response(
                "There is no active document or pricing request. Please ask for the item you need first.",
                report,
            )

        values = {
            "full_name": (full_name or "").strip(),
            "email": (email or "").strip(),
            "contact_number": (contact_number or "").strip(),
            "company_name": (company_name or "").strip(),
        }
        errors = []
        if len(values["full_name"]) < 2 or any(character.isdigit() for character in values["full_name"]):
            errors.append("Enter a valid full name using letters.")
        if not is_valid_email(values["email"]):
            errors.append("Enter a valid email address, such as `name@company.com`.")
        if not is_valid_contact_number(values["contact_number"]):
            errors.append("Enter a valid contact number containing 7 to 15 digits.")
        if len(values["company_name"]) < 2:
            errors.append("Enter a valid company name.")

        if errors:
            return self._lead_response(
                "Please correct the following:\n\n- " + "\n- ".join(errors),
                report,
            )

        lead.full_name = values["full_name"]
        lead.email = values["email"]
        lead.contact_number = values["contact_number"]
        lead.company_name = values["company_name"]
        return self._submit_lead(lead, report)

    def start_help_request(self) -> Dict[str, object]:
        report = lambda _value, _description: None
        if self.memory.lead_capture is not None:
            return self._lead_response(
                "A contact form is already open for your current request. Complete it or select **Cancel** before starting another request.",
                report,
            )

        self.memory.lead_capture = LeadCaptureState(
            requested_item="general technical support",
            original_request="Ad hoc help request opened from the chatbot header",
        )
        return self._lead_response(
            "Please complete the contact form below and our technical support team will contact you shortly.",
            report,
        )

    def _handle_lead_capture(self, user_message: str, report: Callable[[float, str], None]) -> Dict[str, object]:
        lead = self.memory.lead_capture
        if lead is None:
            raise RuntimeError("Lead capture state is unavailable")

        value = (user_message or "").strip()
        if value.lower() in {"cancel", "cancel request", "stop"}:
            self.memory.lead_capture = None
            return self._lead_response(
                "Your request has been cancelled. How else can I help?",
                report,
            )

        if lead.is_complete:
            return self._submit_lead(lead, report)

        if lead.next_field == "full_name":
            if len(value) < 2 or any(character.isdigit() for character in value):
                return self._lead_response(
                    "Please enter a valid full name using letters.",
                    report,
                )
            lead.full_name = value
            return self._lead_response(
                "**2 of 4 — Email Address**\n\nPlease enter your email address.",
                report,
            )

        if lead.next_field == "email":
            if not is_valid_email(value):
                return self._lead_response(
                    "That email address does not appear valid. Please enter an address such as `name@company.com`.",
                    report,
                )
            lead.email = value
            return self._lead_response(
                "**3 of 4 — Contact Number**\n\nPlease enter your contact number, including the country code if applicable.",
                report,
            )

        if lead.next_field == "contact_number":
            if not is_valid_contact_number(value):
                return self._lead_response(
                    "Please enter a valid contact number containing 7 to 15 digits.",
                    report,
                )
            lead.contact_number = value
            return self._lead_response(
                "**4 of 4 — Company Name**\n\nPlease enter your company name.",
                report,
            )

        if len(value) < 2:
            return self._lead_response(
                "Please enter a valid company name.",
                report,
            )
        lead.company_name = value
        return self._submit_lead(lead, report)

    def _submit_lead(self, lead: LeadCaptureState, report: Callable[[float, str], None]) -> Dict[str, object]:
        report(0.78, "Submitting your support request")
        try:
            self.email_notifier.send(lead)
        except Exception:
            logger.exception("Lead notification email failed", extra={"event": "lead_email_failed"})
            return self._lead_response(
                "I couldn't submit your request right now. Your details have not been discarded. "
                "Please type **retry** in a moment, or **cancel** to stop.",
                report,
            )

        requested_item = lead.requested_item
        self.memory.lead_capture = None
        logger.info("Lead notification email sent", extra={"event": "lead_email_sent", "requested_item": requested_item})
        return self._lead_response(
            "Thank you. Your contact information and request for "
            f"**{requested_item}** have been submitted to our technical support team. "
            "We will contact you shortly with the requested details.",
            report,
        )

    def _lead_response(self, answer: str, report: Callable[[float, str], None]) -> Dict[str, object]:
        response = AgentResponse(
            answer=answer,
            sources=[],
            escalation_required=True,
            confidence="low",
            trace_id=str(uuid.uuid4())[:8],
        )
        self.memory.add_turn("assistant", answer)
        report(1.0, "Response ready")
        return response.to_dict()

    def reset(self) -> None:
        self.memory.reset()
