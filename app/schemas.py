from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SafetyResult:
    is_safe: bool
    is_product_relevant: bool
    reason: str = ""
    redirect_message: Optional[str] = None


@dataclass
class RetrievalItem:
    vendor: str
    text: str
    source_file: Optional[str] = None
    source_url: Optional[str] = None
    page_number: Optional[int] = None
    chunk_type: Optional[str] = None
    image_url: Optional[str] = None
    score: float = 0.0


@dataclass
class AgentResponse:
    answer: str
    sources: List[RetrievalItem] = field(default_factory=list)
    escalation_required: bool = False
    confidence: str = "medium"
    trace_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "answer": self.answer,
            "sources": [
                {
                    "vendor": item.vendor,
                    "source_file": item.source_file,
                    "source_url": item.source_url,
                    "page_number": item.page_number,
                    "image_url": item.image_url,
                    "text": item.text,
                }
                for item in self.sources
            ],
            "escalation_required": self.escalation_required,
            "confidence": self.confidence,
            "trace_id": self.trace_id,
        }
