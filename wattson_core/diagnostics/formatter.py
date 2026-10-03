"""Formatação humana dos relatórios de diagnóstico."""

from __future__ import annotations


class DiagnosticFormatter:
    def format(self, report: dict) -> str:
        if "status" in report and "verdict" not in report:
            return self._format_generic(report)

        return self._format_adr0(report)

    def _format_generic(self, report: dict) -> str:
        status = report.get("status", "unknown")
        errors = report.get("errors", [])

        lines = [
            "Diagnóstico concluído.",
            "",
            f"Status: {status}",
            f"errors: {errors}",
        ]

        if errors:
            lines.extend([
                "",
                "Problemas encontrados:",
            ])

            for error in errors:
                lines.append(f"• {error}")
        else:
            lines.extend([
                "",
                "Nenhum erro encontrado.",
            ])

        return "\n".join(lines)

    def _format_adr0(self, report: dict) -> str:
        verdict = report.get("verdict", "DESCONHECIDO")
        counts = report.get("counts", {})
        modules = report.get("modules_scanned", 0)
        results = report.get("results", [])

        lines = [
            "Diagnóstico concluído.",
            "",
            f"Status: {self._status_label(verdict)}",
            f"Módulos analisados: {modules}",
            "",
            f"✓ {counts.get('PASS', 0)} verificações passaram",
            f"⚠ {counts.get('WARN', 0)} verificações com atenção",
            f"✗ {counts.get('FAIL', 0)} verificações com problema",
            f"○ {counts.get('SKIP', 0)} verificações ignoradas",
        ]

        problems = [
            result
            for result in results
            if result.get("status") in ("FAIL", "WARN", "ERROR")
        ]

        if problems:
            lines.extend([
                "",
                "Problemas encontrados:",
            ])

            for result in problems:
                rule_id = result.get("rule_id", "?")
                title = result.get("title", "Regra desconhecida")
                status = result.get("status", "?")

                lines.append(
                    f"• {rule_id} | {status} | {title}"
                )

        elif verdict == "OK":
            lines.extend([
                "",
                "Nenhuma violação encontrada.",
            ])

        return "\n".join(lines)

    def _status_label(self, verdict: str) -> str:
        labels = {
            "OK": "OK 🟢",
            "ATENÇÃO": "ATENÇÃO 🟡",
            "VIOLAÇÕES": "VIOLAÇÕES 🔴",
        }

        return labels.get(verdict, verdict)
