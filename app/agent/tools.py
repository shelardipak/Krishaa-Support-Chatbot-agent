from __future__ import annotations

from typing import Any, Dict, List

from app.agent.safety import safety_check
from app.retrieval.qdrant_client import QdrantClientAdapter
from app.schemas import RetrievalItem


class ProductRetrievalTool:
    name = "product_retrieval"
    description = "Retrieve relevant product knowledge from Qdrant for a user question."

    def __init__(self, client: QdrantClientAdapter | None = None):
        self.client = client or QdrantClientAdapter()

    def run(self, query: str, vendor: str | None = None, limit: int = 3) -> List[RetrievalItem]:
        return self.client.search(query=query, limit=limit, vendor=vendor)


class EscalationTool:
    name = "contact_support"
    description = "Escalate unresolved, sensitive, or safety-critical cases to support."

    def run(self, reason: str) -> Dict[str, Any]:
        return {
            "status": "escalated",
            "message": "I cannot confidently answer from the available product documentation. Please contact a qualified support engineer.",
            "reason": reason,
        }


class SourceFormatterTool:
    name = "format_sources"
    description = "Formats retrieved source metadata for display in the answer."

    def run(self, items: List[RetrievalItem]) -> List[Dict[str, Any]]:
        formatted = []
        for item in items:
            entry = {
                "vendor": item.vendor,
                "source_file": item.source_file,
                "page_number": item.page_number,
            }
            if item.image_url:
                entry["image_url"] = item.image_url
            formatted.append(entry)
        return formatted


def route_tool(user_message: str, retrieval_items: List[RetrievalItem]) -> str:
    safety = safety_check(user_message)
    if not safety.is_safe:
        return EscalationTool().name

    if not retrieval_items:
        return EscalationTool().name

    if len(retrieval_items) == 0:
        return EscalationTool().name

    return ProductRetrievalTool().name
