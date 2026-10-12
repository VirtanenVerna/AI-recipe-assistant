import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx
import ollama
import pytest

from src.models.model_client import (
    ModelClientError, ModelNotFoundError, ModelTimeoutError,
    OllamaConnectionError, OllamaModelClient,
)


@pytest.fixture
def adapter():
    with patch("src.models.model_client.ollama.Client") as constructor:
        sdk = MagicMock()
        constructor.return_value = sdk
        yield OllamaModelClient(model_name="test-model"), sdk


@pytest.mark.parametrize("response", [
    {"message": {"content": " recipe "}},
    SimpleNamespace(message=SimpleNamespace(content=" recipe "), done_reason="stop"),
])
def test_dict_and_object_responses(adapter, response):
    client, sdk = adapter
    sdk.chat.return_value = response
    assert client.generate("rice") == "recipe"


@pytest.mark.parametrize("response", [
    None, {}, {"message": None}, {"message": {}},
    {"message": {"content": ""}}, {"message": {"content": "  "}},
    {"message": {"content": 123}}, object(),
    {"message": {"content": None}}, {"message": []},
    SimpleNamespace(message=None),
    SimpleNamespace(message=SimpleNamespace(content="  ")),
    SimpleNamespace(message=SimpleNamespace(content=["recipe"])),
])
def test_empty_or_malformed_sdk_result_is_an_error(adapter, response):
    client, sdk = adapter
    sdk.chat.return_value = response
    with pytest.raises(ModelClientError):
        client.generate("rice")


@pytest.mark.parametrize("response", [
    {"message": {"content": "Bake until..."}, "done_reason": "length"},
    SimpleNamespace(message=SimpleNamespace(content="Bake until..."), done_reason="length"),
])
def test_truncated_recipe_is_not_a_success(adapter, response):
    client, sdk = adapter
    sdk.chat.return_value = response
    with pytest.raises(ModelClientError, match="cut off"):
        client.generate("rice")


@pytest.mark.parametrize("error,expected", [
    (httpx.ReadTimeout("slow"), ModelTimeoutError),
    (httpx.ConnectTimeout("slow"), ModelTimeoutError),
    (httpx.WriteTimeout("slow"), ModelTimeoutError),
    (httpx.PoolTimeout("busy"), ModelTimeoutError),
    (httpx.ConnectError("offline"), OllamaConnectionError),
    (httpx.ReadError("disconnected"), OllamaConnectionError),
    (httpx.WriteError("disconnected"), OllamaConnectionError),
    (ConnectionError("offline"), OllamaConnectionError),
    (ollama.ResponseError("missing", status_code=404), ModelNotFoundError),
    (ollama.ResponseError("runner not found", status_code=500), ModelClientError),
    (RuntimeError("404 text is not HTTP status"), ModelClientError),
])
def test_errors_are_classified_by_type_and_status(adapter, error, expected):
    client, sdk = adapter
    sdk.chat.side_effect = error
    with pytest.raises(expected) as caught:
        client.generate("rice")
    assert type(caught.value) is expected


def test_actual_sdk_payload_and_timeout_without_a_server():
    requests = []
    def respond(request):
        requests.append(json.loads(request.content))
        assert request.extensions["timeout"]["read"] == 3
        return httpx.Response(200, json={
            "model": "test-model", "message": {"role": "assistant", "content": "recipe"},
            "done": True, "done_reason": "stop",
        })
    sdk = ollama.Client(host="http://127.0.0.1:11434", timeout=3,
                        transport=httpx.MockTransport(respond))
    with patch("src.models.model_client.ollama.Client", return_value=sdk) as factory:
        client = OllamaModelClient(model_name="test-model", timeout_seconds=3)
    timeout = factory.call_args.kwargs["timeout"]
    assert timeout.read == 3 and timeout.connect == 3
    try:
        assert client.generate("rice") == "recipe"
    finally:
        client.close()
    body = requests[0]
    assert body["think"] is False
    assert body["model"] == "test-model"
    assert [m["role"] for m in body["messages"]] == ["system", "user"]
    assert body["messages"][1]["content"] == "rice"
    assert body["options"]["num_ctx"] == 4096
    assert body["options"]["num_predict"] == 1024


@pytest.mark.parametrize("status,payload,expected", [
    (404, {"error": "missing model"}, ModelNotFoundError),
    (500, {"error": "runner failed"}, ModelClientError),
    (401, {"error": "unauthorized"}, ModelClientError),
    (200, None, ModelClientError),
    (200, [], ModelClientError),
    (200, {}, ModelClientError),
    (200, {"message": None}, ModelClientError),
    (200, {"message": {"role": "assistant", "content": ""}}, ModelClientError),
    (200, {"message": {"role": "assistant", "content": 42}}, ModelClientError),
    (200, {"message": {"role": "assistant", "content": "partial"},
           "done_reason": "length"}, ModelClientError),
])
def test_real_sdk_rejects_http_errors_and_unusable_payloads(status, payload, expected):
    def respond(request):
        assert request.url.path == "/api/chat"
        return httpx.Response(status, content=json.dumps(payload),
                              headers={"content-type": "application/json"})

    sdk = ollama.Client(host="http://ollama.invalid", transport=httpx.MockTransport(respond))
    with patch("src.models.model_client.ollama.Client", return_value=sdk):
        client = OllamaModelClient(model_name="test-model")
    try:
        with pytest.raises(expected) as caught:
            client.generate("rice")
        assert type(caught.value) is expected
    finally:
        client.close()


def test_real_sdk_malformed_json_is_model_error():
    sdk = ollama.Client(host="http://ollama.invalid", transport=httpx.MockTransport(
        lambda request: httpx.Response(200, content=b"{broken json")
    ))
    with patch("src.models.model_client.ollama.Client", return_value=sdk):
        client = OllamaModelClient()
    try:
        with pytest.raises(ModelClientError):
            client.generate("rice")
    finally:
        client.close()


@pytest.mark.parametrize("error,expected", [
    (httpx.ReadTimeout("slow"), ModelTimeoutError),
    (httpx.ConnectError("offline"), OllamaConnectionError),
])
def test_real_sdk_transport_failures(error, expected):
    def fail(request):
        raise error

    sdk = ollama.Client(host="http://ollama.invalid", transport=httpx.MockTransport(fail))
    with patch("src.models.model_client.ollama.Client", return_value=sdk):
        client = OllamaModelClient()
    try:
        with pytest.raises(expected):
            client.generate("rice")
    finally:
        client.close()


def test_client_caps_connect_timeout_and_uses_config_defaults(monkeypatch):
    from src.models.model_client import config

    monkeypatch.setattr(config, "ollama_base_url", "http://ollama.invalid")
    monkeypatch.setattr(config, "model_name", "isolated-model")
    monkeypatch.setattr(config, "timeout_seconds", 60)
    with patch("src.models.model_client.ollama.Client") as factory:
        client = OllamaModelClient()
    assert factory.call_args.kwargs["host"] == "http://ollama.invalid"
    timeout = factory.call_args.kwargs["timeout"]
    assert timeout.read == 60
    assert timeout.connect == 10
    assert client.model_name == "isolated-model"
