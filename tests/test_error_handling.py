import pytest

from wattson_core.ai.engine import AIEngine
from wattson_core.ai.errors import AIProviderError


def test_ai_engine_converts_provider_failure():
    class FailingProvider:
        def generate(self, prompt: str) -> str:
            raise RuntimeError("Provider indisponível.")

    engine = AIEngine(FailingProvider())

    with pytest.raises(AIProviderError):
        engine.generate("Teste")


def test_ai_engine_rejects_invalid_prompt():
    engine = AIEngine(lambda prompt: "resposta")

    with pytest.raises(TypeError):
        engine.generate(None)
