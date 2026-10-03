import uuid

from .context import ConversationContext


class Session:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.context = ConversationContext()
        self.active = True

    def add_message(self, message: str):
        if not self.active:
            raise RuntimeError("Sessão encerrada.")

        self.context.add(message)

    def clear_context(self):
        self.context.messages.clear()

    def close(self):
        self.active = False
