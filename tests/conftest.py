"""Never let tests read or write the user's actual preference file."""
import pytest


@pytest.fixture(autouse=True)
def isolated_memory(tmp_path, monkeypatch):
    monkeypatch.setenv("MEMORY_FILE", str(tmp_path / "user_memory.json"))
