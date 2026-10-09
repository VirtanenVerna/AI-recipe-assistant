"""Small JSON-backed memory for the local, single-user recipe assistant."""

from __future__ import annotations

import json
import os
from pathlib import Path


class MemoryStore:
    """Persist the user's dietary preferences between application runs."""

    def __init__(self, path: str | Path | None = None) -> None:
        configured_path = path or os.getenv("MEMORY_FILE", "data/user_memory.json")
        self.path = Path(configured_path)

    def get_preferences(self) -> str:
        """Return saved dietary preferences, or an empty string if none exist."""

        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return ""

        preferences = data.get("dietary_preferences", "")
        return preferences.strip() if isinstance(preferences, str) else ""

    def save_preferences(self, preferences: str) -> None:
        """Save non-empty dietary preferences, creating the parent directory."""

        cleaned_preferences = preferences.strip()
        if not cleaned_preferences:
            return

        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"dietary_preferences": cleaned_preferences}
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def clear_preferences(self) -> None:
        """Remove saved dietary preferences from local memory."""

        try:
            self.path.unlink()
        except FileNotFoundError:
            pass
