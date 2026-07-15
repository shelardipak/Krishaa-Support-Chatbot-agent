from app.agent.graph import RAGAgent
from app.agent import response_builder
from app.config import settings
from app.retrieval.qdrant_client import QdrantClientAdapter
from app.ui import gradio_app
from app.ui.gradio_app import respond


def test_agent_returns_grounded_answer_for_supported_product_question(monkeypatch):
    monkeypatch.setattr(response_builder, "_llm_answer", lambda *_: "Grounded test answer")
    agent = RAGAgent()
    agent.product_tool.client = QdrantClientAdapter(use_remote=False, allow_fallback=True)
    progress_events = []
    response = agent.chat(
        "Tell me about Raychem cable accessories",
        progress_callback=lambda value, description: progress_events.append((value, description)),
    )
    assert response["answer"]
    assert response["sources"]
    assert response["escalation_required"] is False
    assert progress_events[0] == (0.08, "Checking your question")
    assert any("Searching product documentation" in description for _, description in progress_events)
    assert progress_events[-1] == (1.0, "Response ready")


def test_ui_response_helper_does_not_embed_a_default_image(monkeypatch):
    class FakeAgent:
        def chat(self, message, vendor=None):
            return {
                "answer": "Grounded answer without an image.",
                "sources": [{"vendor": "Raychem", "image_url": None}],
            }

    monkeypatch.setattr(gradio_app, "agent", FakeAgent())
    history, answer, image_url, _ = gradio_app.respond("Tell me about Raychem cable accessories", [])
    assert history
    assert answer
    assert image_url is None
    assert "![Relevant product image]" not in history[-1][1]


def test_ui_response_helper_adds_verified_reference_links(monkeypatch):
    class FakeAgent:
        def chat(self, message, vendor=None):
            return {
                "answer": "The retrieved documentation contains the requested specification.",
                "sources": [
                    {
                        "vendor": "Raychem",
                        "source_file": "Product catalog.pdf",
                        "source_url": "https://example.com/product-catalog.pdf",
                        "page_number": 7,
                        "image_url": None,
                        "text": "Specification details",
                    }
                ],
            }

    monkeypatch.setattr(gradio_app, "agent", FakeAgent())
    history, _, _, _ = gradio_app.respond("Show the specification", [])

    assert "[Product catalog.pdf, page 7](https://example.com/product-catalog.pdf)" in history[-1][1]


def test_retriever_builds_public_document_url_from_source_path(monkeypatch):
    monkeypatch.setattr(settings, "supabase_url", "https://example.supabase.co")
    monkeypatch.setattr(settings, "supabase_document_bucket", "product-documents")
    client = QdrantClientAdapter(use_remote=False)

    url = client._normalize_source_url(
        {
            "source_file": "Link box.pdf",
            "source_path": "knowledge/Raychem Catalogues/Link box.pdf",
        }
    )

    assert url == (
        "https://example.supabase.co/storage/v1/object/public/product-documents/"
        "knowledge/Raychem%20Catalogues/Link%20box.pdf"
    )


def test_irrelevant_question_with_no_semantic_matches_shows_no_sources_or_image(monkeypatch):
    agent = RAGAgent()

    class EmptyRetriever:
        def search(self, *args, **kwargs):
            return []

    agent.product_tool.client = EmptyRetriever()
    result = agent.chat("What is the FIFA World Cup?")

    assert result["sources"] == []
    assert result["escalation_required"] is True
    assert "Raychem, CharCoat, or Mennekes" in result["answer"]

    class FakeAgent:
        def chat(self, message, vendor=None):
            return {
                "answer": "Please ask a supported product question.",
                "sources": [
                    {
                        "vendor": "Raychem",
                        "image_url": "https://example.com/unrelated.png",
                        "source_url": "https://example.com/unrelated.pdf",
                    }
                ],
                "escalation_required": True,
                "confidence": "low",
            }

    monkeypatch.setattr(gradio_app, "agent", FakeAgent())
    history, _, image_url, _ = gradio_app.respond("What is the FIFA World Cup?", [])

    assert image_url is None
    assert "unrelated.png" not in history[-1][1]
    assert "unrelated.pdf" not in history[-1][1]


def test_semantic_product_match_is_answered_without_keyword_gate(monkeypatch):
    from app.schemas import RetrievalItem

    monkeypatch.setattr(response_builder, "_llm_answer", lambda *_: "Screened coupling connector details")
    agent = RAGAgent()

    class CouplingRetriever:
        def search(self, *args, **kwargs):
            return [
                RetrievalItem(
                    vendor="raychem",
                    text="RSTI-CC-58 is an 800 A screened coupling connector rated up to 24 kV.",
                    source_file="RSTI Coupling.pdf",
                    page_number=3,
                    score=0.66,
                )
            ]

    agent.product_tool.client = CouplingRetriever()
    result = agent.chat("Tell me something about Screened Coupling connector")

    assert result["answer"] == "Screened coupling connector details"
    assert len(result["sources"]) == 1
    assert result["escalation_required"] is False
