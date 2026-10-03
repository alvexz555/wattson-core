class ConversationAI:
    def __init__(self, engine, context):
        self.engine = engine
        self.context = context

    def respond(self, message: str) -> str:
        self.context.add(message)
        prompt = "\n".join(self.context.messages)

        response = self.engine.generate(prompt)

        self.context.add(response)

        return response
