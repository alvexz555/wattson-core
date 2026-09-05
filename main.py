class WattsonCore:
    """
    Núcleo principal do Wattson.

    Nesta primeira versão:
    - recebe uma mensagem;
    - envia a mensagem para o modelo de IA;
    - retorna a resposta.
    """

    def __init__(self, client, model="gpt-5.6-luna"):
        self.name = "Wattson"
        self.version = "0.2.0"

        self.client = client
        self.model = model

    def think(self, message: str) -> str:

        if not message.strip():
            return "Não recebi nenhuma entrada."

        response = self.client.responses.create(
            model=self.model,
            instructions=(
                "Você é Wattson, o núcleo de uma inteligência "
                "artificial experimental. "
                "Responda sempre em português do Brasil. "
                "Seja natural, objetivo e útil."
            ),
            input=message
        )

        return response.output_text
