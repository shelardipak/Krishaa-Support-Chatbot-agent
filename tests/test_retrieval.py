from types import SimpleNamespace

from app.retrieval.qdrant_client import QdrantClientAdapter


def test_fallback_retrieval_returns_vendor_results():
    client = QdrantClientAdapter(use_remote=False, allow_fallback=True)
    results = client.search("CharCoat fire protection", limit=3)
    assert len(results) > 0
    assert any(item.vendor == "CharCoat" for item in results)


def test_query_is_embedded_before_qdrant_similarity_search():
    class FakeEmbeddings:
        def __init__(self):
            self.query = None
            self.calls = 0

        def embed_query(self, query):
            self.query = query
            self.calls += 1
            return [0.1, 0.2, 0.3]

    class FakeQdrantClient:
        def __init__(self):
            self.arguments = None

        def query_points(self, **kwargs):
            self.arguments = kwargs
            return SimpleNamespace(
                points=[
                    SimpleNamespace(
                        score=0.82,
                        payload={
                            "vendor": "CharCoat",
                            "text": "CharCoat CC is a water-based intumescent cable coating.",
                            "source_file": "CharCoat CC TDS.pdf",
                            "page_number": 1,
                        },
                    )
                ]
            )

    adapter = QdrantClientAdapter(use_remote=False, allow_fallback=False)
    adapter.embeddings = FakeEmbeddings()
    adapter.client = FakeQdrantClient()

    results = adapter.search("What are the benefits of CharCoat CC?", limit=3)
    adapter.search("What are the benefits of CharCoat CC?", limit=3)

    assert adapter.embeddings.query == "What are the benefits of CharCoat CC?"
    assert adapter.embeddings.calls == 1
    assert adapter.client.arguments["query"] == [0.1, 0.2, 0.3]
    assert adapter.client.arguments["collection_name"] == adapter.collection
    assert adapter.client.arguments["score_threshold"] == 0.35
    assert results[0].vendor == "CharCoat"
    assert results[0].score == 0.82
