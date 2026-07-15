from functools import lru_cache
from typing import List, Optional
from urllib.parse import quote

from app.config import settings
from app.logging_config import get_logger
from app.schemas import RetrievalItem

logger = get_logger("qdrant_retrieval")


class QdrantClientAdapter:
    """Embed user queries and retrieve semantically similar Qdrant points.

    The query embedding model must match the model used to create the vectors
    stored in the collection. Deterministic fallback data is opt-in and intended
    only for tests or demos.
    """

    def __init__(self, *, use_remote: Optional[bool] = None, allow_fallback: Optional[bool] = None):
        self.collection = settings.qdrant_collection
        self.client = None
        self.embeddings = None
        self._allow_fallback = settings.qdrant_allow_fallback if allow_fallback is None else allow_fallback
        configured = bool(settings.qdrant_url and settings.qdrant_api_key and settings.openai_api_key)
        self._use_remote = configured if use_remote is None else use_remote
        if self._use_remote:
            try:
                from langchain_openai import OpenAIEmbeddings
                from qdrant_client import QdrantClient

                self.client = QdrantClient(
                    url=settings.qdrant_url,
                    api_key=settings.qdrant_api_key,
                    timeout=10,
                    check_compatibility=False,
                )
                self.embeddings = OpenAIEmbeddings(
                    model=settings.openai_embedding_model,
                    dimensions=settings.openai_embedding_dimensions,
                    api_key=settings.openai_api_key,
                )
            except Exception:
                logger.exception("Failed to initialize vector retrieval")
                self.client = None
                self.embeddings = None
                self._use_remote = False

    def _normalize_image_url(self, payload: dict) -> Optional[str]:
        image_url = payload.get("image_url") or payload.get("image") or None
        if not image_url:
            return None
        if image_url.startswith(("http://", "https://")):
            return image_url
        if settings.supabase_url and settings.supabase_storage_bucket:
            return f"{settings.supabase_url}/storage/v1/object/public/{settings.supabase_storage_bucket}/{image_url.lstrip('/')}"
        return image_url

    def _normalize_source_url(self, payload: dict) -> Optional[str]:
        for field in ("source_url", "document_url", "file_url", "public_url", "url"):
            value = payload.get(field)
            if isinstance(value, str) and value.startswith(("http://", "https://")):
                return value

        source_file = payload.get("source_file")
        if isinstance(source_file, str) and source_file.startswith(("http://", "https://")):
            return source_file

        # Older Qdrant chunks store only the document path. When the source
        # PDFs are mirrored to a public Supabase bucket, turn that path into a
        # stable link that the UI can include in its References section.
        if settings.supabase_url and settings.supabase_document_bucket:
            source_path = next(
                (
                    payload.get(field)
                    for field in ("document_storage_path", "source_storage_path", "source_path")
                    if isinstance(payload.get(field), str) and payload.get(field).strip()
                ),
                None,
            )
            if source_path is None and isinstance(source_file, str) and source_file.strip():
                source_path = source_file
            if source_path:
                encoded_path = quote(source_path.lstrip("/"), safe="/")
                bucket = quote(settings.supabase_document_bucket.strip("/"), safe="")
                return f"{settings.supabase_url.rstrip('/')}/storage/v1/object/public/{bucket}/{encoded_path}"
        return None

    def _fallback_payload(self, query: str, vendor: Optional[str], limit: int) -> List[dict]:
        vendor_filter = (vendor or "").lower()
        query_lower = query.lower()
        payload = []

        if "charcoat" in query_lower:
            payload.append(
                {
                    "vendor": "CharCoat",
                    "text": "CharCoat fire protection products include intumescent coatings and fireproofing systems suitable for structural protection.",
                    "source_file": "CharCoat CTI TDS.pdf",
                    "source_url": None,
                    "page_number": 3,
                    "chunk_type": "product",
                    "image_url": None,
                }
            )
        elif "mennekes" in query_lower:
            payload.append(
                {
                    "vendor": "Mennekes",
                    "text": "Mennekes industrial plugs and sockets offer robust connection solutions for industrial power applications.",
                    "source_file": "Mennekes product sheet.pdf",
                    "source_url": None,
                    "page_number": 2,
                    "chunk_type": "product",
                    "image_url": None,
                }
            )
        else:
            payload.append(
                {
                    "vendor": "Raychem",
                    "text": "Raychem cable accessories include joints and terminations designed for electrical insulation and cable protection.",
                    "source_file": "Raychem cable accessories.pdf",
                    "source_url": None,
                    "page_number": 1,
                    "chunk_type": "product",
                    "image_url": None,
                }
            )

        filtered = []
        for entry in payload[:limit]:
            if vendor_filter and entry["vendor"].lower() != vendor_filter:
                continue
            filtered.append(entry)
        return filtered

    @lru_cache(maxsize=128)
    def _embed_query(self, query: str) -> tuple[float, ...]:
        """Cache embeddings for repeated support questions within this process."""
        if self.embeddings is None:
            return ()
        return tuple(self.embeddings.embed_query(query))

    def search(self, query: str, limit: int = 3, vendor: Optional[str] = None) -> List[RetrievalItem]:
        if self.client and self.embeddings:
            try:
                from qdrant_client.models import Filter, FieldCondition, MatchValue

                filters = []
                vendor_filter = (vendor or "").strip()
                if vendor_filter:
                    filters.append(FieldCondition(key="vendor", match=MatchValue(value=vendor_filter)))
                query_filter = Filter(must=filters) if filters else None
                query_vector = list(self._embed_query(query))
                response = self.client.query_points(
                    collection_name=self.collection,
                    query=query_vector,
                    using=settings.qdrant_vector_name,
                    query_filter=query_filter,
                    limit=limit,
                    with_payload=True,
                    with_vectors=False,
                    score_threshold=settings.qdrant_score_threshold,
                )
                results = []
                for point in response.points:
                    payload = point.payload or {}
                    text = payload.get("text") or payload.get("content") or ""
                    if not text:
                        continue
                    results.append(
                        RetrievalItem(
                            vendor=str(payload.get("vendor") or payload.get("vendor_name") or "Unknown"),
                            text=str(payload.get("text") or payload.get("content") or ""),
                            source_file=payload.get("source_file"),
                            source_url=self._normalize_source_url(payload),
                            page_number=payload.get("page_number"),
                            chunk_type=payload.get("chunk_type"),
                            image_url=self._normalize_image_url(payload),
                            score=float(point.score),
                        )
                    )
                return results
            except Exception:
                logger.exception("Vector retrieval failed; no fallback context will be used unless explicitly enabled")

        if not self._allow_fallback:
            return []

        logger.warning("Using deterministic fallback retrieval data")
        fallback_payload = self._fallback_payload(query=query, vendor=vendor, limit=limit)
        results = []
        for entry in fallback_payload:
            results.append(
                RetrievalItem(
                    vendor=entry["vendor"],
                    text=entry["text"],
                    source_file=entry.get("source_file"),
                    source_url=entry.get("source_url"),
                    page_number=entry.get("page_number"),
                    chunk_type=entry.get("chunk_type"),
                    image_url=entry.get("image_url"),
                    score=0.95,
                )
            )
        return results
