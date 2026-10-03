from wattson_core.ai.context import ConversationContext


def test_context_stores_messages_in_order():
    context = ConversationContext()

    context.add("Olá, Wattson")
    context.add("Como você está?")

    assert context.messages == [
        "Olá, Wattson",
        "Como você está?",
    ]


def test_context_returns_messages_in_order():
    context = ConversationContext()

    context.add("Primeira mensagem")
    context.add("Segunda mensagem")

    assert context.get_messages() == [
        "Primeira mensagem",
        "Segunda mensagem",
    ]


def test_context_can_be_cleared():
    context = ConversationContext()

    context.add("Mensagem antiga")
    context.add("Outra mensagem")

    context.clear()

    assert context.get_messages() == []


def test_new_context_starts_empty():
    context = ConversationContext()

    assert context.get_messages() == []
