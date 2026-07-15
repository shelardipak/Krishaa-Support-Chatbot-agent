import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class FeedbackStore:
    def __init__(self, path: Optional[str] = None):
        self.path = Path(path or os.getenv("FEEDBACK_PATH", "feedback.jsonl"))
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, *, feedback: str, answer_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "feedback": feedback,
            "answer_id": answer_id,
            "reason": reason or "",
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")
        return entry

    def read_all(self) -> List[Dict[str, Any]]:
        if not self.path.exists():
            return []
        records = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records
