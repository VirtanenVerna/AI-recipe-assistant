import json
from unittest.mock import MagicMock, patch

import pytest

from src.capabilities.memory import MemoryStore, MemoryWriteError
from src.models.model_client import (
    ModelClientError, ModelNotFoundError, ModelTimeoutError, OllamaConnectionError,
)
from src.services.ai_service import AIService, generate_response


@pytest.fixture
def service():
    client = MagicMock()
    client.generate.return_value = "A simple recipe."
    return AIService(client, MemoryStore())


@pytest.mark.parametrize("ingredients,wishes", [
    ("", ""), ("   ", ""), (None, ""), (42, ""),
    ("x" * 4001, ""), ("rice", "x" * 1001), ("rice", None),
])
def test_invalid_input_is_rejected_before_disk_or_model(service, ingredients, wishes):
    service.memory_store = MagicMock()
    result = service.process_message(ingredients, wishes)
    assert not result.success
    service.model_client.generate.assert_not_called()
    service.memory_store.get_preferences.assert_not_called()
    service.memory_store.save_preferences.assert_not_called()


def test_response_and_prompt_fields(service):
    assert generate_response(" rice ", " two servings ", service) == "A simple recipe."
    prompt = service.model_client.generate.call_args.args[0]
    data = json.loads(prompt.split("\n\n", 1)[1])
    assert data == {
        "ingredients": "rice", "meal_preferences": "two servings",
        "dietary_preferences": "",
    }


def test_temporary_wishes_never_replace_saved_restrictions(service):
    assert service.save_preferences("no peanuts").success
    before = service.memory_store.path.read_bytes()
    assert service.process_message("rice", "under 30 minutes").success
    prompt = service.model_client.generate.call_args.args[0]
    assert "no peanuts" in prompt and "under 30 minutes" in prompt
    assert service.memory_store.path.read_bytes() == before


def test_saved_preferences_survive_new_service_instance(service):
    service.save_preferences("vegetarian")
    second = AIService(service.model_client, MemoryStore())
    assert second.process_message("lentils").success
    assert "vegetarian" in second.model_client.generate.call_args.args[0]


def test_generation_without_save_creates_no_file(service):
    assert service.process_message("rice", "vegan").success
    assert not service.memory_store.path.exists()


@pytest.mark.parametrize("error,expected", [
    (OllamaConnectionError("offline"), "Could not connect"),
    (ModelNotFoundError("missing"), "model is unavailable"),
    (ModelTimeoutError("timeout"), "took too long"),
    (ModelClientError("bad result"), "usable recipe"),
    (RuntimeError("unexpected"), "application error"),
])
def test_model_errors_preserve_preferences(service, error, expected):
    service.save_preferences("vegetarian")
    before = service.memory_store.path.read_bytes()
    service.model_client.generate.side_effect = error
    result = service.process_message("rice", "two servings")
    assert not result.success
    assert expected in result.content
    assert service.memory_store.path.read_bytes() == before


@pytest.mark.parametrize("content", ["", "   ", None])
def test_unusable_model_text_is_not_success(service, content):
    service.model_client.generate.return_value = content
    assert not service.process_message("rice").success


def test_unreadable_memory_blocks_generation_even_with_meal_wishes(service):
    service.memory_store.path.write_text("[]", encoding="utf-8")
    result = service.process_message("rice", "under 30 minutes")
    assert not result.success
    assert "could not be read" in result.content
    service.model_client.generate.assert_not_called()
    assert service.memory_store.path.read_text() == "[]"


@pytest.mark.parametrize("preferences", ["", "   ", None, 7, "x" * 1001])
def test_invalid_save_preserves_existing_preferences(service, preferences):
    service.save_preferences("vegetarian")
    before = service.memory_store.path.read_bytes()
    assert not service.save_preferences(preferences).success
    assert service.memory_store.path.read_bytes() == before


def test_memory_write_failure_is_a_friendly_response(service, monkeypatch):
    service.save_preferences("vegetarian")
    def fail(_):
        raise MemoryWriteError("read only")
    monkeypatch.setattr(service.memory_store, "save_preferences", fail)
    result = service.save_preferences("vegan")
    assert not result.success
    assert "could not be saved" in result.content
    assert service.memory_store.get_preferences() == "vegetarian"


def test_explicit_save_load_reuse_and_forget(service):
    assert service.load_preferences().content == ""
    assert service.save_preferences("  no peanuts  ").success
    second = AIService(service.model_client, MemoryStore())
    assert second.load_preferences().content == "no peanuts"
    assert second.process_message("rice", "include peanuts").success
    prompt = second.model_client.generate.call_args.args[0]
    data = json.loads(prompt.split("\n\n", 1)[1])
    assert data["dietary_preferences"] == "no peanuts"
    assert data["meal_preferences"] == "include peanuts"
    assert second.load_preferences().content == "no peanuts"
    assert second.clear_preferences().success
    assert second.clear_preferences().success
    assert service.load_preferences().content == ""
    assert service.process_message("rice").success
    data = json.loads(service.model_client.generate.call_args.args[0].split("\n\n", 1)[1])
    assert data["dietary_preferences"] == ""
    assert not service.memory_store.path.exists()


@pytest.mark.parametrize("raw", ["[]", "null", "{", "{}"])
def test_broken_memory_load_and_generation_fail_until_explicit_recovery(service, raw):
    service.memory_store.path.write_text(raw, encoding="utf-8")
    assert not service.load_preferences().success
    assert not service.process_message("rice", "vegan").success
    service.model_client.generate.assert_not_called()
    assert service.memory_store.path.read_text(encoding="utf-8") == raw
    assert service.save_preferences("no dairy").success
    assert service.load_preferences().content == "no dairy"
    assert service.process_message("rice").success


def test_failed_forget_retains_active_preferences(service):
    service.save_preferences("no dairy")
    with patch.object(type(service.memory_store.path), "unlink", side_effect=PermissionError("denied")):
        result = service.clear_preferences()
    assert not result.success
    assert "still active" in result.content
    assert service.load_preferences().content == "no dairy"


@pytest.mark.parametrize("ingredients,wishes", [("x" * 4001, ""), ("rice", "x" * 1001)])
def test_limits_precede_disk_access_and_lazy_client_construction(ingredients, wishes):
    memory = MagicMock()
    service = AIService(memory_store=memory)
    with patch("src.services.ai_service.OllamaModelClient") as constructor:
        assert not service.process_message(ingredients, wishes).success
        constructor.assert_not_called()
    assert memory.mock_calls == []


@pytest.mark.parametrize("value", ["", " ", None, 42, "x" * 1001])
def test_invalid_save_does_not_attempt_io(value):
    memory = MagicMock()
    assert not AIService(memory_store=memory).save_preferences(value).success
    assert memory.mock_calls == []


def test_exact_input_limits_are_accepted(service):
    assert service.save_preferences("s" * 1000).success
    assert service.process_message("i" * 4000, "w" * 1000).success
    data = json.loads(service.model_client.generate.call_args.args[0].split("\n\n", 1)[1])
    assert data == {"ingredients": "i" * 4000, "meal_preferences": "w" * 1000,
                    "dietary_preferences": "s" * 1000}


@pytest.mark.parametrize("error", [ModelClientError("invalid"), ModelTimeoutError("slow")])
def test_model_failure_without_saved_preferences_creates_no_file(service, error):
    service.model_client.generate.side_effect = error
    assert not service.process_message("rice", "vegan").success
    assert not service.memory_store.path.exists()
