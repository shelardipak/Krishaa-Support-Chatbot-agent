from app.schemas import RetrievalItem


def judge_context(retrieval_items: list[RetrievalItem], user_message: str) -> tuple[bool, str]:
    if not retrieval_items:
        return False, "No retrieved context was available."
    if len(retrieval_items) == 1 and retrieval_items[0].text and len(retrieval_items[0].text) < 30:
        return False, "The retrieved context was too sparse to answer confidently."
    return True, "Retrieved context is sufficient for a grounded answer."
