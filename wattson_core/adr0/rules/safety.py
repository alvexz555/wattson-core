"""Regras de segurança: execução, boot seguro e ADR 0 somente-leitura."""
from __future__ import annotations

import ast

from ..models import Confidence, Finding, Severity
from ..scanner import call_matches, is_under
from .base import Context, Rule, Skip, loc

_WRITE_MODE_CHARS = set("wax+")


class ExecutionOnlyInExecutor(Rule):
    id = "R007"
    title = "Execução externa só no Executor"
    adr = "ADR-2 / ADR-6"

    def check(self, ctx: Context) -> list[Finding]:
        c = ctx.contract
        out: list[Finding] = []
        why = ("Toda execução precisa passar por Permission Layer → Session → Executor. "
               "O ADR 0 estático não prova o fluxo, mas detecta onde ele pode ser contornado.")
        fix = "Mover para wattson_core.executor e chamar somente depois da autorização."
        for mod in ctx.scan.modules.values():
            if any(is_under(mod.name, z) for z in c.exec_allowed):
                continue
            for imp in mod.imports:
                if not imp.type_only and imp.root in c.exec_modules:
                    out.append(self.finding(
                        f"{mod.name} importa '{imp.root}' fora do Executor",
                        Severity.HIGH, Confidence.PROVAVEL, loc(mod, imp.line), why, fix,
                    ))
            for call in mod.calls:
                if call_matches(call, c.exec_calls):
                    out.append(self.finding(
                        f"{mod.name} chama {call.name}() fora do Executor",
                        Severity.HIGH, Confidence.PROVAVEL, loc(mod, call.line), why, fix,
                    ))
        return out


def _boot_state(tree: ast.Module) -> ast.expr | None:
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == "BOOT_STATE" for t in node.targets):
                return node.value
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == "BOOT_STATE":
                return node.value
    return None


class SafeBoot(Rule):
    id = "R009"
    title = "Boot seguro (CHAT_ONLY)"
    adr = "ADR-6"

    def check(self, ctx: Context) -> list[Finding]:
        c = ctx.contract
        mod = ctx.scan.modules.get(c.boot_module)
        if mod is None:
            raise Skip(f"{c.boot_module} ainda não existe (Fase 2)")
        why = "Todo boot deve iniciar no estado de menor privilégio; nunca restaurar o último modo."
        tree = ctx.scan.parse(c.boot_module)
        node = _boot_state(tree) if tree else None
        if node is None:
            return [self.finding(
                f"{c.boot_module} não declara BOOT_STATE literal",
                Severity.HIGH, Confidence.INDETERMINADO, loc(mod), why,
                "Declarar BOOT_STATE como dict literal para o ADR 0 poder verificar.",
            )]
        try:
            state = ast.literal_eval(node)
        except (ValueError, SyntaxError):
            state = None
        if not isinstance(state, dict):
            return [self.finding(
                "BOOT_STATE não é um dict literal; verificação estática impossível",
                Severity.HIGH, Confidence.INDETERMINADO, loc(mod, node.lineno), why,
                "Usar valores literais (strings) em BOOT_STATE.",
            )]
        return [
            self.finding(
                f"BOOT_STATE[{key!r}] = {state.get(key)!r} (esperado {expected!r})",
                Severity.CRITICAL, Confidence.CONFIRMADO, loc(mod, node.lineno), why,
                "Corrigir o estado inicial: o Wattson sempre inicia bloqueado.",
            )
            for key, expected in c.boot_required.items() if state.get(key) != expected
        ]


class ReadOnlyObserver(Rule):
    id = "R010"
    title = "ADR 0 observa, não controla"
    adr = "ADR-0"

    def check(self, ctx: Context) -> list[Finding]:
        c = ctx.contract
        if not c.readonly_zone:
            raise Skip("zona somente-leitura não definida no contrato")
        why = "O ADR 0 observa e diagnostica; não vira controlador do sistema."
        out: list[Finding] = []
        for mod in ctx.scan.under(c.readonly_zone):
            for imp in mod.imports:
                if imp.root in c.readonly_forbidden_imports:
                    out.append(self.finding(
                        f"{mod.name} importa '{imp.root}'",
                        Severity.HIGH, Confidence.CONFIRMADO, loc(mod, imp.line), why,
                        "O observador não executa comandos nem acessa a rede.",
                    ))
            for call in mod.calls:
                out.extend(self._check_call(mod, call, c.readonly_write_calls, why))
        return out

    def _check_call(self, mod, call, write_calls, why: str) -> list[Finding]:
        if call.attr == "open" and call.mode is not None:
            if call.mode == "?":
                return [self.finding(
                    f"{mod.name} abre arquivo com modo não literal",
                    Severity.MEDIUM, Confidence.POSSIVEL, loc(mod, call.line), why,
                    "Usar modo de leitura literal.",
                )]
            if _WRITE_MODE_CHARS & set(call.mode):
                return [self.finding(
                    f"{mod.name} abre arquivo para escrita (modo {call.mode!r})",
                    Severity.HIGH, Confidence.CONFIRMADO, loc(mod, call.line), why,
                    "O relatório sai por stdout; quem chama decide onde gravar.",
                )]
            return []
        if call_matches(call, write_calls):
            return [self.finding(
                f"{mod.name} chama {call.name}(), que altera o sistema de arquivos",
                Severity.HIGH, Confidence.PROVAVEL, loc(mod, call.line), why,
                "O ADR 0 não altera o que observa.",
            )]
        return []
