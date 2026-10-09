from unittest.mock import MagicMock

from src.capabilities.memory import MemoryStore
from src.config import config
from src.models.model_client import (
    ModelClientError,
    ModelNotFoundError,
    OllamaConnectionError,
)
from src.services.ai_service import AIService, clear_saved_preferences, generate_response


def test_config_loading():
    assert config.ollama_base_url is not None
    assert config.model_name is not None
    assert isinstance(config.ollama_base_url, str)
    assert isinstance(config.model_name, str)


def test_empty_input_validation():
    mock_client = MagicMock()
    service = AIService(model_client=mock_client)

    response_empty = service.process_message("")
    assert response_empty.success is False
    assert "Please enter a message" in response_empty.content
    assert mock_client.generate.call_count == 0

    response_spaces = service.process_message("   ")
    assert response_spaces.success is False
    assert mock_client.generate.call_count == 0


def test_successful_response_generation(tmp_path):
    mock_client = MagicMock()
    mock_client.generate.return_value = "Hello! I am an AI assistant."
    service = AIService(
        model_client=mock_client,
        memory_store=MemoryStore(tmp_path / "memory.json"),
    )

    result_text = generate_response("Hello, AI", service=service)

    assert result_text == "Hello! I am an AI assistant."
    prompt = mock_client.generate.call_args.args[0]
    assert "Hello, AI" in prompt
    assert "None provided" in prompt


def test_preferences_are_included_in_model_prompt(tmp_path):
    mock_client = MagicMock()
    mock_client.generate.return_value = "A vegetarian recipe."
    service = AIService(
        model_client=mock_client,
        memory_store=MemoryStore(tmp_path / "memory.json"),
    )

    result = service.process_message("potatoes, onions", "vegetarian")

    assert result.success is True
    prompt = mock_client.generate.call_args.args[0]
    assert "potatoes, onions" in prompt
    assert "vegetarian" in prompt


def test_preferences_are_saved_and_reused(tmp_path):
    memory = MemoryStore(tmp_path / "memory.json")
    first_client = MagicMock()
    first_client.generate.return_value = "A vegetarian recipe."
    first_service = AIService(model_client=first_client, memory_store=memory)

    first_service.process_message("potatoes", "vegetarian")

    second_client = MagicMock()
    second_client.generate.return_value = "Another vegetarian recipe."
    second_service = AIService(model_client=second_client, memory_store=memory)
    second_service.process_message("lentils")

    prompt = second_client.generate.call_args.args[0]
    assert "vegetarian" in prompt


def test_saved_preferences_can_be_cleared(tmp_path, monkeypatch):
    memory = MemoryStore(tmp_path / "memory.json")
    memory.save_preferences("vegetarian")
    monkeypatch.setenv("MEMORY_FILE", str(memory.path))

    assert clear_saved_preferences() == "Saved dietary preferences cleared."
    assert memory.get_preferences() == ""


def test_ollama_connection_error_handling():
    mock_client = MagicMock()
    mock_client.generate.side_effect = OllamaConnectionError(
        "Connection refused at http://localhost:11434"
    )
    service = AIService(model_client=mock_client)

    response = service.process_message("Test message")

    assert response.success is False
    assert "Could not connect to Ollama" in response.content
    assert "Connection refused" in response.error_message


def test_model_not_found_error_handling():
    mock_client = MagicMock()
    mock_client.generate.side_effect = ModelNotFoundError(
        "Model llama3.2 not found locally"
    )
    service = AIService(model_client=mock_client)

    response = service.process_message("Test message")

    assert response.success is False
    assert "configured AI model is unavailable" in response.content
    assert "llama3.2 not found" in response.error_message


def test_empty_model_response_is_handled_as_an_error():
    mock_client = MagicMock()
    mock_client.generate.side_effect = ModelClientError(
        "The model returned an empty response."
    )
    service = AIService(model_client=mock_client)

    response = service.process_message("potatoes")

    assert response.success is False
    assert "communication error" in response.content
