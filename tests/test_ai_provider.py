from wattson_core.ai.interface import AIProvider


def test_ai_provider_defines_generate_contract():
    assert hasattr(AIProvider, "generate")
