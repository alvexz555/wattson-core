"""Integração controlada do ADR0 como ferramenta de diagnóstico."""

from __future__ import annotations

import json

from wattson_core.executor.runner import run_adr0


class ADR0DiagnosticTool:
    def __init__(self, root: str = "."):
        self.root = root

    def run(self):
        result = run_adr0(self.root)

        if result.returncode != 0:
            raise RuntimeError(
                f"ADR0 falhou com código {result.returncode}: "
                f"{result.stderr.strip()}"
            )

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as error:
            raise RuntimeError(
                "ADR0 retornou uma saída que não é JSON válido."
            ) from error
