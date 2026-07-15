import os
from typing import Optional

from app.config import settings
from app.logging_config import get_logger

logger = get_logger("langsmith")


def get_trace_id() -> Optional[str]:
    if not settings.langsmith_tracing:
        return None
    return "trace-" + os.urandom(4).hex()


def log_trace(event: str, detail: str) -> None:
    if settings.langsmith_tracing:
        logger.info("langsmith_event=%s detail=%s", event, detail)
