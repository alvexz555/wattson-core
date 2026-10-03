from wattson_core.diagnostics.formatter import DiagnosticFormatter


class Orchestrator:
    def __init__(
        self,
        conversation,
        diagnostic_tool=None,
        search_tool=None,
    ):
        self.conversation = conversation
        self.diagnostic_tool = diagnostic_tool
        self.search_tool = search_tool
        self.diagnostic_formatter = DiagnosticFormatter()

    def handle(self, message: str) -> str:
        if self._is_diagnostic_request(message):
            diagnostic = self.run_diagnostic()
            return self.diagnostic_formatter.format(diagnostic)

        if self._is_search_request(message):
            return self.run_search(message)

        return self.conversation.respond(message)

    def _is_diagnostic_request(self, message: str) -> bool:
        keywords = (
            "diagnóstico",
            "diagnostico",
            "erros",
            "erro",
            "problemas",
        )
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in keywords)

    def _is_search_request(self, message: str) -> bool:
        keywords = (
            "pesquise",
            "pesquisa",
            "procure",
            "busque",
        )

        message_lower = message.strip().lower()

        return any(
            message_lower.startswith(keyword)
            for keyword in keywords
        )

    def run_search(self, query: str):
        if self.search_tool is None:
            raise RuntimeError("Ferramenta de pesquisa não configurada.")

        results = self.search_tool.search(query)
        research_prompt = self._build_search_prompt(query, results)

        return self.conversation.respond(research_prompt)

    def _build_search_prompt(self, query: str, results: list) -> str:
        results = results[:5]

        lines = [
            f"Pergunta do usuário: {query}",
            "",
            "Resultados encontrados na pesquisa:",
        ]

        for index, result in enumerate(results, start=1):
            title = result.get("title", "")
            url = result.get("url", "")
            content = result.get("content", "")

            lines.extend([
                "",
                f"Resultado {index}:",
                f"Título: {title}",
                f"URL: {url}",
                f"Conteúdo: {content}",
            ])

        return "\n".join(lines)

    def run_diagnostic(self):
        if self.diagnostic_tool is None:
            raise RuntimeError("Ferramenta de diagnóstico não configurada.")

        return self.diagnostic_tool.run()
