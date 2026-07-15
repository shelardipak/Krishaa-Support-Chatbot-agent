import re
from app.schemas import SafetyResult


PRODUCT_KEYWORDS = ["raychem", "charcoat", "mennekes", "cable", "accessory", "joint", "termination", "insulation", "fire", "plug", "socket"]


def safety_check(user_message: str) -> SafetyResult:
    text = (user_message or "").strip().lower()

    if not text:
        return SafetyResult(is_safe=False, is_product_relevant=False, reason="Empty input")

    unsafe_patterns = [
        "bypass", "hack", "explosive", "kill", "attack", "illegal", "steal", "poison"
    ]
    if any(pattern in text for pattern in unsafe_patterns):
        return SafetyResult(
            is_safe=False,
            is_product_relevant=False,
            reason="The request appears unsafe or policy-violating.",
            redirect_message="I can only help with safe product-support questions about engineering products.",
        )

    is_product_relevant = any(keyword in text for keyword in PRODUCT_KEYWORDS)
    if not is_product_relevant:
        return SafetyResult(
            is_safe=True,
            is_product_relevant=False,
            reason="The request does not appear to be about supported engineering products.",
            redirect_message="Please ask about Raychem, CharCoat, or Mennekes products, and I can help with product support questions.",
        )

    return SafetyResult(is_safe=True, is_product_relevant=True, reason="Product-related support request.")
