import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_max_output_tokens: int = int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "350"))
    openai_embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    openai_embedding_dimensions: Optional[int] = (
        int(os.getenv("OPENAI_EMBEDDING_DIMENSIONS")) if os.getenv("OPENAI_EMBEDDING_DIMENSIONS") else None
    )
    qdrant_url: Optional[str] = os.getenv("QDRANT_URL")
    qdrant_api_key: Optional[str] = os.getenv("QDRANT_API_KEY")
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "engineering-products")
    qdrant_vector_name: Optional[str] = os.getenv("QDRANT_VECTOR_NAME") or None
    qdrant_score_threshold: float = float(os.getenv("QDRANT_SCORE_THRESHOLD", "0.35"))
    qdrant_allow_fallback: bool = os.getenv("QDRANT_ALLOW_FALLBACK", "false").lower() == "true"
    rag_max_context_chars: int = int(os.getenv("RAG_MAX_CONTEXT_CHARS", "12000"))
    langsmith_tracing: bool = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
    langsmith_api_key: Optional[str] = os.getenv("LANGSMITH_API_KEY")
    langsmith_project: str = os.getenv("LANGSMITH_PROJECT", "engineering-products-rag")
    supabase_url: Optional[str] = os.getenv("SUPABASE_URL")
    supabase_storage_bucket: Optional[str] = os.getenv("SUPABASE_STORAGE_BUCKET")
    supabase_document_bucket: Optional[str] = os.getenv("SUPABASE_DOCUMENT_BUCKET")
    lead_notification_email: str = os.getenv("LEAD_NOTIFICATION_EMAIL", "shelar.dipak@gmail.com")
    smtp_host: Optional[str] = os.getenv("SMTP_HOST")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: Optional[str] = os.getenv("SMTP_USERNAME")
    smtp_app_password: Optional[str] = os.getenv("SMTP_APP_PASSWORD") or os.getenv("SMTP_PASSWORD")
    smtp_from_email: Optional[str] = os.getenv("SMTP_FROM_EMAIL") or os.getenv("SMTP_USERNAME")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    smtp_use_ssl: bool = os.getenv("SMTP_USE_SSL", "false").lower() == "true"


settings = Settings()
