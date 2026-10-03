from wattson_core.ai.engine import AIEngine


class FakeProvider:
    def generate(self, prompt: str) -> str:
        return f"resposta: {prompt}"


def test_ai_engine_sends_prompt_to_provider():
    engine = AIEngine(FakeProvider())

    result = engine.generate("Olá, Wattson")

    assert result == "resposta: Olá, Wattson"
