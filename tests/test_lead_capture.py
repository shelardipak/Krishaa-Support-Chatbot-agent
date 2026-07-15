import pytest

from app.agent.graph import RAGAgent
from app.agent.lead_capture import detect_protected_request, is_valid_contact_number, is_valid_email


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("Please send the product drawing for this connector", "product drawings"),
        ("I need the product data sheet", "product data sheets"),
        ("Can I get the installation manual?", "product installation manuals"),
        ("Share the detailed test report", "detailed test reports"),
        ("What is the product pricing?", "product pricing details"),
    ],
)
def test_protected_request_detection(message, expected):
    assert detect_protected_request(message) == expected


def test_unprotected_product_question_does_not_trigger_lead_capture():
    assert detect_protected_request("What voltage is the connector rated for?") is None


def test_email_and_contact_validation():
    assert is_valid_email("engineer@example.com") is True
    assert is_valid_email("engineer@") is False
    assert is_valid_contact_number("+91 98765 43210") is True
    assert is_valid_contact_number("12-34") is False


class RecordingNotifier:
    def __init__(self):
        self.leads = []

    def send(self, lead):
        self.leads.append(lead)


class FailingRetriever:
    def search(self, *args, **kwargs):
        raise AssertionError("Retrieval must not run during lead capture")


def test_lead_capture_gates_retrieval_and_sends_complete_lead():
    notifier = RecordingNotifier()
    agent = RAGAgent(email_notifier=notifier)
    agent.product_tool.client = FailingRetriever()

    first = agent.chat("Please send the Raychem product data sheet")
    assert "Full Name" in first["answer"]
    assert first["sources"] == []
    assert first["escalation_required"] is True

    assert "Email Address" in agent.chat("Dipak Shelar")["answer"]
    invalid_email = agent.chat("not-an-email")
    assert "does not appear valid" in invalid_email["answer"]
    assert "Contact Number" in agent.chat("dipak@example.com")["answer"]

    invalid_contact = agent.chat("1234")
    assert "7 to 15 digits" in invalid_contact["answer"]
    assert "Company Name" in agent.chat("+91 98765 43210")["answer"]

    completed = agent.chat("Krishaa Engineers")
    assert "contact you shortly" in completed["answer"]
    assert completed["sources"] == []
    assert len(notifier.leads) == 1

    lead = notifier.leads[0]
    assert lead.full_name == "Dipak Shelar"
    assert lead.email == "dipak@example.com"
    assert lead.contact_number == "+91 98765 43210"
    assert lead.company_name == "Krishaa Engineers"
    assert lead.requested_item == "product data sheets"
    assert "Raychem" in lead.original_request
    assert agent.memory.lead_capture is None


def test_full_lead_form_validates_and_submits_all_fields_together():
    notifier = RecordingNotifier()
    agent = RAGAgent(email_notifier=notifier)
    agent.chat("Please provide a detailed test report")

    invalid = agent.submit_lead_form(
        full_name="Dipak Shelar",
        email="invalid-email",
        contact_number="1234",
        company_name="Krishaa Engineers",
    )

    assert "valid email address" in invalid["answer"]
    assert "7 to 15 digits" in invalid["answer"]
    assert notifier.leads == []
    assert agent.memory.lead_capture is not None

    completed = agent.submit_lead_form(
        full_name="Dipak Shelar",
        email="dipak@example.com",
        contact_number="+91 98765 43210",
        company_name="Krishaa Engineers",
    )

    assert "contact you shortly" in completed["answer"]
    assert len(notifier.leads) == 1
    assert agent.memory.lead_capture is None


class RetryNotifier:
    def __init__(self):
        self.attempts = 0

    def send(self, lead):
        self.attempts += 1
        if self.attempts == 1:
            raise RuntimeError("temporary email failure")


def test_failed_email_can_be_retried_without_reentering_details():
    notifier = RetryNotifier()
    agent = RAGAgent(email_notifier=notifier)

    agent.chat("I need product pricing details")
    agent.chat("Dipak Shelar")
    agent.chat("dipak@example.com")
    agent.chat("+91 98765 43210")
    failed = agent.chat("Krishaa Engineers")

    assert "type **retry**" in failed["answer"]
    completed = agent.chat("retry")
    assert "contact you shortly" in completed["answer"]
    assert notifier.attempts == 2


def test_lead_capture_can_be_cancelled():
    agent = RAGAgent(email_notifier=RecordingNotifier())
    agent.chat("Please send the installation manual")

    cancelled = agent.chat("cancel")

    assert "cancelled" in cancelled["answer"]
    assert agent.memory.lead_capture is None


def test_header_help_request_opens_and_submits_general_support_form():
    notifier = RecordingNotifier()
    agent = RAGAgent(email_notifier=notifier)

    opened = agent.start_help_request()
    assert "contact form" in opened["answer"]
    assert agent.memory.lead_capture is not None
    assert agent.memory.lead_capture.requested_item == "general technical support"

    completed = agent.submit_lead_form(
        full_name="Dipak Shelar",
        email="dipak@example.com",
        contact_number="+91 98765 43210",
        company_name="Krishaa Engineers",
    )

    assert "contact you shortly" in completed["answer"]
    assert len(notifier.leads) == 1
    assert notifier.leads[0].requested_item == "general technical support"
    assert agent.memory.lead_capture is None


def test_header_help_does_not_replace_an_existing_request():
    agent = RAGAgent(email_notifier=RecordingNotifier())
    agent.chat("Please send a product drawing")

    response = agent.start_help_request()

    assert "already open" in response["answer"]
    assert agent.memory.lead_capture.requested_item == "product drawings"
