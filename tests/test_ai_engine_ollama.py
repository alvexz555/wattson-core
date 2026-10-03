from wattson_core.ai.engine import AIEngine
from wattson_core.ai.providers.ollama import WattsonProvider


def test_ai_engine_uses_dolphin_provider():
    provider = WattsonProvider()
    engine = AIEngine(provider)

    response = engine.generate(
        "Responda apenas com: AIEngine conectado ao Dolphin."
    )

    assert isinstance(response, str)
    assert response.strip()
