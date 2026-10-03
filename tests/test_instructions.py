from wattson_core.ai.instructions import WattsonInstructions


def test_wattson_instructions_exist():
    instructions = WattsonInstructions()

    assert isinstance(instructions.rules, list)


def test_wattson_instructions_require_clarity():
    instructions = WattsonInstructions()

    assert "responder com clareza" in instructions.rules


def test_wattson_instructions_require_honesty():
    instructions = WattsonInstructions()

    assert "não inventar informações" in instructions.rules


def test_wattson_instructions_can_add_rule():
    instructions = WattsonInstructions()

    instructions.add_rule("ser objetivo")

    assert "ser objetivo" in instructions.rules
