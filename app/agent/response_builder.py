from __future__ import annotations

from functools import lru_cache

from app.agent.prompts import DEFAULT_PROMPT
from app.agent.safety import safety_check
from app.config import settings
from app.schemas import AgentResponse, RetrievalItem

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
except Exception:  # pragma: no cover - optional dependency path
    ChatOpenAI = None
    ChatPromptTemplate = None


def _build_context(retrieval_items: list[RetrievalItem], max_chars: int) -> str:
    context_sections = []
    remaining = max(max_chars, 0)
    for index, item in enumerate(retrieval_items, 1):
        metadata = [f"Vendor: {item.vendor}"]
        if item.source_file:
            metadata.append(f"Document: {item.source_file}")
        if item.page_number is not None:
            metadata.append(f"Page: {item.page_number}")
        if item.source_url:
            metadata.append(f"Document URL: {item.source_url}")

        prefix = f"[Retrieved context {index}]\n" + "\n".join(metadata) + "\nContent: "
        available_text = max(remaining - len(prefix), 0)
        if available_text <= 0:
            break
        text = item.text[:available_text]
        context_sections.append(prefix + text)
        remaining -= len(prefix) + len(text) + 2
        if remaining <= 0:
            break
    return "\n\n".join(context_sections)


@lru_cache(maxsize=4)
def _get_llm_chain(model: str, max_output_tokens: int, api_key: str):
    llm = ChatOpenAI(
        model=model,
        temperature=0,
        max_tokens=max_output_tokens,
        api_key=api_key,
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", DEFAULT_PROMPT.system_prompt),
            (
                "human",
                "Question: {question}\nContext:\n{context}\n"
                "Respond briefly and safely. Do not invent links or claim that a comprehensive catalog is available. "
                "Do not add a Sources or References section; the application adds verified document links separately. "
                "If the retrieved context is insufficient, state exactly what information is missing and recommend support.",
            ),
        ]
    )
    return prompt | llm


@lru_cache(maxsize=128)
def _invoke_llm(
    user_message: str,
    context: str,
    model: str,
    max_output_tokens: int,
    api_key: str,
) -> str:
    chain = _get_llm_chain(model, max_output_tokens, api_key)
    result = chain.invoke({"question": user_message, "context": context})
    return getattr(result, "content", str(result))


def _llm_answer(user_message: str, retrieval_items: list[RetrievalItem]) -> str | None:
    if not settings.openai_api_key or ChatOpenAI is None or ChatPromptTemplate is None:
        return None
    try:
        context = _build_context(retrieval_items, settings.rag_max_context_chars)
        return _invoke_llm(
            user_message,
            context,
            settings.openai_model,
            settings.openai_max_output_tokens,
            settings.openai_api_key,
        )
    except Exception:
        return None


def build_response(user_message: str, retrieval_items: list[RetrievalItem], trace_id: str | None = None) -> AgentResponse:
    safety = safety_check(user_message)
    if not safety.is_safe:
        return AgentResponse(
            answer=safety.redirect_message or "I can only assist with supported engineering product questions.",
            sources=[],
            escalation_required=True,
            confidence="low",
            trace_id=trace_id,
        )

    if not retrieval_items:
        if not safety.is_product_relevant:
            return AgentResponse(
                answer=safety.redirect_message
                or "Please ask about Raychem, CharCoat, or Mennekes products and support topics.",
                sources=[],
                escalation_required=True,
                confidence="low",
                trace_id=trace_id,
            )
        escalation = EscalationTool().run("No relevant retrieval context found")
        return AgentResponse(
            answer=escalation["message"],
            sources=[],
            escalation_required=True,
            confidence="low",
            trace_id=trace_id,
        )

    llm_answer = _llm_answer(user_message, retrieval_items)
    if llm_answer:
        answer = llm_answer
    else:
        context_text = "\n".join(item.text for item in retrieval_items)
        answer = (
            f"Based on the available product documentation, I can share that {context_text}. "
            f"Please contact support if you need a more specific recommendation."
        )

    return AgentResponse(
        answer=answer,
        sources=retrieval_items,
        escalation_required=False,
        confidence="high",
        trace_id=trace_id,
    )
