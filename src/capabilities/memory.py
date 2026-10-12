"""Atomic JSON preference storage for one local user, not a shared account store."""

import json
import os
import tempfile
from pathlib import Path
from threading import RLock

from src.config import PROJECT_ROOT
from src.schemas.responses import MAX_PREFERENCES_LENGTH

_MEMORY_LOCK = RLock()


class MemoryStoreError(Exception):
    """A preference operation could not safely complete."""


class MemoryReadError(MemoryStoreError):
    """Saved preferences exist but could not be read or validated."""


class MemoryWriteError(MemoryStoreError):
    """Preferences could not be saved or removed."""


class MemoryStore:
    """Missing file means no preferences; broken/unreadable data is an error."""

    def __init__(self, path: str | Path | None = None) -> None:
        configured = path if path is not None else os.getenv(
            "MEMORY_FILE", "data/user_memory.json"
        )
        candidate = Path(configured)
        self.path = candidate if candidate.is_absolute() else PROJECT_ROOT / candidate

    def get_preferences(self) -> str:
        with _MEMORY_LOCK:
            try:
                data = json.loads(self.path.read_text(encoding="utf-8-sig"))
            except FileNotFoundError:
                return ""
            except (OSError, ValueError) as err:
                raise MemoryReadError("Cannot read saved dietary preferences.") from err

            if not isinstance(data, dict) or not isinstance(
                data.get("dietary_preferences"), str
            ):
                raise MemoryReadError("Saved dietary preferences have an invalid format.")
            preferences = data["dietary_preferences"].strip()
            if len(preferences) > MAX_PREFERENCES_LENGTH:
                raise MemoryReadError("Saved dietary preferences exceed the size limit.")
            return preferences

    def save_preferences(self, preferences: str) -> None:
        if not isinstance(preferences, str):
            raise ValueError("Dietary preferences must be text.")
        cleaned = preferences.strip()
        if not cleaned or len(cleaned) > MAX_PREFERENCES_LENGTH:
            raise ValueError("Use 1–1000 characters, or explicitly clear preferences.")

        with _MEMORY_LOCK:
            temporary_path = None
            try:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile(
                    mode="w", encoding="utf-8", dir=self.path.parent,
                    prefix=f".{self.path.name}.", suffix=".tmp", delete=False,
                ) as temporary:
                    temporary_path = Path(temporary.name)
                    json.dump(
                        {"dietary_preferences": cleaned},
                        temporary, ensure_ascii=False, indent=2,
                    )
                    temporary.write("\n")
                    temporary.flush()
                    os.fsync(temporary.fileno())
                os.replace(temporary_path, self.path)
            except OSError as err:
                raise MemoryWriteError("Cannot save dietary preferences.") from err
            finally:
                if temporary_path is not None:
                    try:
                        temporary_path.unlink(missing_ok=True)
                    except OSError:
                        # Do not replace the actionable save error with a cleanup error.
                        pass

    def clear_preferences(self) -> None:
        with _MEMORY_LOCK:
            try:
                self.path.unlink(missing_ok=True)
            except OSError as err:
                raise MemoryWriteError("Cannot clear saved dietary preferences.") from err
