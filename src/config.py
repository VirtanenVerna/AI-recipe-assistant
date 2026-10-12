"""Local runtime settings; shell variables override the project .env file."""

import math
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def _timeout_seconds() -> float:
    try:
        value = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))
    except ValueError as err:
        raise ValueError("OLLAMA_TIMEOUT_SECONDS must be a positive number.") from err
    if not math.isfinite(value) or value <= 0:
        raise ValueError("OLLAMA_TIMEOUT_SECONDS must be a positive finite number.")
    return value


@dataclass
class Config:
    """Read settings at construction, so tests can isolate their environment."""

    ollama_base_url: str = field(
        default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )
    model_name: str = field(default_factory=lambda: os.getenv("MODEL_NAME", "llama3.2"))
    timeout_seconds: float = field(default_factory=_timeout_seconds)


config = Config()
