from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from app.agent.lead_capture import LeadCaptureState


@dataclass
class ConversationTurn:
    role: str
    content: str


@dataclass
class ConversationMemory:
    turns: List[ConversationTurn] = field(default_factory=list)
    lead_capture: Optional[LeadCaptureState] = None

    def add_turn(self, role: str, content: str) -> None:
        self.turns.append(ConversationTurn(role=role, content=content))

    def reset(self) -> None:
        self.turns.clear()
        self.lead_capture = None

    def summary(self) -> Optional[str]:
        if not self.turns:
            return None
        return " | ".join(f"{t.role}: {t.content}" for t in self.turns[-4:])
