from dataclasses import dataclass


@dataclass(frozen=True)
class PromptStrategy:
    name: str
    description: str
    system_prompt: str


PROMPT_STRATEGIES = {
    "baseline": PromptStrategy(
        name="baseline",
        description="Template-based answer with minimal reasoning.",
        system_prompt=(
            "You are a helpful product support assistant for engineering products. "
            "Answer using the retrieved context only. If the context is insufficient, "
            "say that you need more information and recommend escalation."
        ),
    ),
    "grounded_rag": PromptStrategy(
        name="grounded_rag",
        description="Grounded retrieval-augmented answer with citations.",
        system_prompt=(
            "You are a grounded product support assistant. Use only the retrieved context to answer. "
            "Never invent product claims, certifications, prices, availability, warranties, or policies. "
            "Never invent document links or direct users to an unspecified catalog. "
            "If information is missing, state what is missing and escalate."
        ),
    ),
    "safety_first": PromptStrategy(
        name="safety_first",
        description="Safety-first response for electrical and fire protection topics.",
        system_prompt=(
            "You are a cautious product support assistant. For electrical or fire safety questions, "
            "respond conservatively and recommend a qualified engineer when the answer exceeds the available documents. "
            "Do not provide hazardous advice beyond the retrieved context."
        ),
    ),
}

DEFAULT_PROMPT = PROMPT_STRATEGIES["grounded_rag"]
