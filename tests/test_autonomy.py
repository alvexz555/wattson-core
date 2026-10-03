from wattson_core.ai.conversation import ConversationAI
from wattson_core.ai.context import ConversationContext
from wattson_core.ai.engine import AIEngine
from wattson_core.core.orchestrator import Orchestrator


def test_wattson_can_process_a_task_through_the_full_stack():
    class FakeProvider:
        def generate(self, prompt: str) -> str:
            return "Tarefa recebida e processada."

    engine = AIEngine(FakeProvider())
    context = ConversationContext()
    conversation = ConversationAI(engine, context)
    orchestrator = Orchestrator(conversation)

    result = orchestrator.handle("Analise esta tarefa.")

    assert result == "Tarefa recebida e processada."
    assert "Analise esta tarefa." in context.messages


def test_wattson_can_continue_a_task_using_previous_context():
    class FakeProvider:
        def __init__(self):
            self.prompts = []

        def generate(self, prompt: str) -> str:
            self.prompts.append(prompt)

            if len(self.prompts) == 1:
                return "Primeira etapa concluída."

            return "Segunda etapa concluída."

    engine = AIEngine(FakeProvider())
    context = ConversationContext()
    conversation = ConversationAI(engine, context)
    orchestrator = Orchestrator(conversation)

    first = orchestrator.handle("Comece a tarefa.")
    second = orchestrator.handle("Continue a tarefa.")

    assert first == "Primeira etapa concluída."
    assert second == "Segunda etapa concluída."

    assert "Comece a tarefa." in context.messages
    assert "Continue a tarefa." in context.messages


def test_wattson_keeps_different_tasks_isolated():
    class FakeProvider:
        def __init__(self):
            self.prompts = []

        def generate(self, prompt: str) -> str:
            self.prompts.append(prompt)
            return "resposta"

    engine = AIEngine(FakeProvider())

    first_context = ConversationContext()
    second_context = ConversationContext()

    first_conversation = ConversationAI(engine, first_context)
    second_conversation = ConversationAI(engine, second_context)

    first_orchestrator = Orchestrator(first_conversation)
    second_orchestrator = Orchestrator(second_conversation)

    first_orchestrator.handle("Tarefa A: analisar um arquivo.")
    second_orchestrator.handle("Tarefa B: pesquisar um assunto.")

    assert "Tarefa A: analisar um arquivo." in first_context.messages
    assert "Tarefa A: analisar um arquivo." not in second_context.messages

    assert "Tarefa B: pesquisar um assunto." in second_context.messages
    assert "Tarefa B: pesquisar um assunto." not in first_context.messages


def test_wattson_does_not_claim_success_when_provider_fails():
    import pytest

    class FailingProvider:
        def generate(self, prompt: str) -> str:
            raise RuntimeError("Falha real no provider.")

    engine = AIEngine(FailingProvider())
    context = ConversationContext()
    conversation = ConversationAI(engine, context)
    orchestrator = Orchestrator(conversation)

    with pytest.raises(Exception):
        orchestrator.handle("Execute esta tarefa.")

    assert "Execute esta tarefa." in context.messages


def test_wattson_uses_previous_task_result_in_next_step():
    class TaskAwareProvider:
        def __init__(self):
            self.prompts = []

        def generate(self, prompt: str) -> str:
            self.prompts.append(prompt)

            if "Resultado da primeira etapa: arquivo analisado." in prompt:
                return "Segunda etapa recebeu o resultado anterior."

            return "Resultado da primeira etapa: arquivo analisado."

    engine = AIEngine(TaskAwareProvider())
    context = ConversationContext()
    conversation = ConversationAI(engine, context)
    orchestrator = Orchestrator(conversation)

    first = orchestrator.handle("Primeira etapa: analise o arquivo.")
    second = orchestrator.handle("Segunda etapa: continue usando o resultado anterior.")

    assert first == "Resultado da primeira etapa: arquivo analisado."
    assert second == "Segunda etapa recebeu o resultado anterior."

    assert "Primeira etapa: analise o arquivo." in context.messages
    assert "Segunda etapa: continue usando o resultado anterior." in context.messages


def test_wattson_can_recognize_task_completion():
    class CompletionAwareProvider:
        def generate(self, prompt: str) -> str:
            if "concluída" in prompt.lower():
                return "A tarefa está concluída."
            return "Tarefa executada com sucesso."

    engine = AIEngine(CompletionAwareProvider())
    context = ConversationContext()
    conversation = ConversationAI(engine, context)
    orchestrator = Orchestrator(conversation)

    first = orchestrator.handle("Execute a tarefa.")
    second = orchestrator.handle("A tarefa foi concluída?")

    assert first == "Tarefa executada com sucesso."
    assert second == "A tarefa está concluída."


def test_wattson_can_continue_after_completed_step():
    class CompletionProvider:
        def __init__(self):
            self.prompts = []

        def generate(self, prompt: str) -> str:
            self.prompts.append(prompt)

            if len(self.prompts) == 1:
                return "Etapa concluída: arquivo analisado."

            if "Etapa concluída: arquivo analisado." in prompt:
                return "Próxima etapa iniciada com base no resultado anterior."

            return "Contexto insuficiente."

    engine = AIEngine(CompletionProvider())
    context = ConversationContext()
    conversation = ConversationAI(engine, context)
    orchestrator = Orchestrator(conversation)

    first = orchestrator.handle("Analise o arquivo.")
    second = orchestrator.handle("Agora continue para a próxima etapa.")

    assert first == "Etapa concluída: arquivo analisado."
    assert second == "Próxima etapa iniciada com base no resultado anterior."
    assert "Etapa concluída: arquivo analisado." in context.messages


def test_wattson_does_not_use_failed_step_as_valid_result():
    class RecoverableProvider:
        def __init__(self):
            self.calls = 0

        def generate(self, prompt: str) -> str:
            self.calls += 1

            if self.calls == 1:
                raise RuntimeError("Falha durante a primeira etapa.")

            return "Segunda etapa executada."

    engine = AIEngine(RecoverableProvider())
    context = ConversationContext()
    conversation = ConversationAI(engine, context)
    orchestrator = Orchestrator(conversation)

    import pytest

    with pytest.raises(Exception):
        orchestrator.handle("Execute a primeira etapa.")

    assert "Falha durante a primeira etapa." not in context.messages

    result = orchestrator.handle("Agora execute a segunda etapa.")

    assert result == "Segunda etapa executada."
    assert "Agora execute a segunda etapa." in context.messages


def test_wattson_can_change_task_without_losing_previous_context():
    class TaskSwitchProvider:
        def __init__(self):
            self.prompts = []

        def generate(self, prompt: str) -> str:
            self.prompts.append(prompt)

            if "Tarefa B" in prompt:
                return "Nova tarefa recebida."

            return "Tarefa A processada."

    provider = TaskSwitchProvider()
    engine = AIEngine(provider)
    context = ConversationContext()
    conversation = ConversationAI(engine, context)
    orchestrator = Orchestrator(conversation)

    first = orchestrator.handle("Tarefa A: analise o arquivo.")
    second = orchestrator.handle("Tarefa B: pesquise outro assunto.")

    assert first == "Tarefa A processada."
    assert second == "Nova tarefa recebida."

    assert "Tarefa A: analise o arquivo." in context.messages
    assert "Tarefa B: pesquise outro assunto." in context.messages
