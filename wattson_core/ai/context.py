class ConversationContext:
    def __init__(self):
        self.messages = []

    def add(self, message: str) -> None:
        self.messages.append(message)

    def get_messages(self):
        return self.messages

    def clear(self) -> None:
        self.messages.clear()
