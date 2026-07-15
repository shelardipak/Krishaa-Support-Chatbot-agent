from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


PROTECTED_REQUEST_PATTERNS = (
    (re.compile(r"\b(?:product\s+|technical\s+|dimensional\s+|ga\s+)?drawings?\b", re.IGNORECASE), "product drawings"),
    (re.compile(r"\b(?:product\s+)?data\s*sheets?\b|\bdatasheets?\b|\btds\b", re.IGNORECASE), "product data sheets"),
    (re.compile(r"\b(?:product\s+)?installation\s+(?:manuals?|instructions?|guides?)\b", re.IGNORECASE), "product installation manuals"),
    (re.compile(r"\b(?:detailed\s+|type\s+)?test\s+reports?\b", re.IGNORECASE), "detailed test reports"),
    (re.compile(r"\b(?:product\s+)?(?:pricing|prices?|quotation|quote|cost)\b", re.IGNORECASE), "product pricing details"),
)

EMAIL_PATTERN = re.compile(r"^[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?(?:\.[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?)+$", re.IGNORECASE)


def detect_protected_request(message: str) -> Optional[str]:
    normalized = (message or "").strip()
    for pattern, request_type in PROTECTED_REQUEST_PATTERNS:
        if pattern.search(normalized):
            return request_type
    return None


def is_valid_email(value: str) -> bool:
    return bool(EMAIL_PATTERN.fullmatch((value or "").strip()))


def is_valid_contact_number(value: str) -> bool:
    value = (value or "").strip()
    if not re.fullmatch(r"[+\d][\d\s().-]*", value):
        return False
    digit_count = sum(character.isdigit() for character in value)
    return 7 <= digit_count <= 15


@dataclass
class LeadCaptureState:
    requested_item: str
    original_request: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    contact_number: Optional[str] = None
    company_name: Optional[str] = None

    @property
    def is_complete(self) -> bool:
        return all((self.full_name, self.email, self.contact_number, self.company_name))

    @property
    def next_field(self) -> str:
        if not self.full_name:
            return "full_name"
        if not self.email:
            return "email"
        if not self.contact_number:
            return "contact_number"
        return "company_name"

