from __future__ import annotations

from pathlib import Path


class PromptManager:
    def __init__(self, prompt_dir: Path | None = None):
        self.prompt_dir = prompt_dir or Path(__file__).resolve().parent / "prompt_templates"

    def get_prompt(self, prompt_name: str) -> str:
        prompt_path = self.prompt_dir / f"{prompt_name}.txt"
        if not prompt_path.exists():
            raise ValueError(f"Prompt '{prompt_name}' not found in {self.prompt_dir}")

        return prompt_path.read_text(encoding="utf-8").strip()
