from wattson_core.ai.session import Session


def test_session_has_id_and_context():
    session = Session()

    assert session.id
    assert session.context is not None


def test_sessions_have_unique_ids():
    first = Session()
    second = Session()

    assert first.id != second.id


def test_sessions_have_independent_contexts():
    first = Session()
    second = Session()

    first.context.add("Mensagem da primeira sessão.")

    assert "Mensagem da primeira sessão." in first.context.messages
    assert "Mensagem da primeira sessão." not in second.context.messages


def test_session_can_clear_context():
    session = Session()

    session.context.add("Mensagem temporária.")

    session.clear_context()

    assert session.context.messages == []


def test_session_can_be_closed():
    session = Session()

    assert session.active is True

    session.close()

    assert session.active is False


def test_closed_session_rejects_context_changes():
    session = Session()

    session.close()

    try:
        session.add_message("Mensagem depois do encerramento.")
        assert False, "Sessão encerrada aceitou alteração de contexto."
    except RuntimeError:
        pass
