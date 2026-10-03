import pytest

from wattson_core.ai.engine import AIEngine
from wattson_core.ai.errors import AIProviderError
from wattson_core.ai.providers.ollama import WattsonProvider


def test_provider_connection_error_is_controlled(monkeypatch):
    def fake_post(url, json, timeout):
        raise ConnectionError("Ollama indisponível.")

    monkeypatch.setattr(
        "wattson_core.ai.providers.ollama.requests.post",
        fake_post,
    )

    engine = AIEngine(WattsonProvider())

    with pytest.raises(AIProviderError):
        engine.generate("Teste de conexão")


def test_provider_invalid_response_is_controlled(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {}

    def fake_post(url, json, timeout):
        return FakeResponse()

    monkeypatch.setattr(
        "wattson_core.ai.providers.ollama.requests.post",
        fake_post,
    )

    engine = AIEngine(WattsonProvider())

    with pytest.raises(AIProviderError):
        engine.generate("Teste de resposta inválida")
