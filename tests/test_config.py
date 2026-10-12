import pytest

from src.config import Config


def test_lightweight_default(monkeypatch):
    monkeypatch.delenv("MODEL_NAME", raising=False)
    monkeypatch.delenv("OLLAMA_TIMEOUT_SECONDS", raising=False)
    assert Config().model_name == "llama3.2"
    assert Config().timeout_seconds == 120


def test_environment_is_read_when_config_is_constructed(monkeypatch):
    monkeypatch.setenv("MODEL_NAME", "custom-model")
    monkeypatch.setenv("OLLAMA_TIMEOUT_SECONDS", "30")
    first = Config()
    monkeypatch.setenv("MODEL_NAME", "another-model")
    assert first.model_name == "custom-model"
    assert Config().model_name == "another-model"
    assert first.timeout_seconds == 30


@pytest.mark.parametrize("value", ["0", "-1", "nan", "inf", "-inf", "", "not-a-number"])
def test_invalid_timeout_fails_clearly(monkeypatch, value):
    monkeypatch.setenv("OLLAMA_TIMEOUT_SECONDS", value)
    with pytest.raises(ValueError, match="OLLAMA_TIMEOUT_SECONDS"):
        Config()


def test_base_url_default_and_environment_override(monkeypatch):
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    monkeypatch.setenv("OLLAMA_TIMEOUT_SECONDS", "0.5")
    first = Config()
    assert first.ollama_base_url == "http://localhost:11434"
    assert first.timeout_seconds == 0.5
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://example.invalid:1234")
    assert Config().ollama_base_url == "http://example.invalid:1234"
    assert first.ollama_base_url == "http://localhost:11434"
