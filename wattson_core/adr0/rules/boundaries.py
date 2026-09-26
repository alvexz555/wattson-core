"""Regras de fronteira: quem pode depender de quem."""
from __future__ import annotations

from ..models import Confidence, Finding, Severity
from ..scanner import STDLIB, call_matches, is_under
from .base import Context, Rule, loc, zone_value


class ComponentBoundaries(Rule):
    id = "R002"
    title = "Fronteiras entre componentes"
    adr = "ADR-1 / ADR-2 / ADR-0"

    def check(self, ctx: Context) -> list[Finding]:
        out: list[Finding] = []
        seen: set[tuple[str, int, int]] = set()
        for mod in ctx.scan.modules.values():
            for imp in mod.imports:
                if not imp.internal:
                    continue
                for item in ctx.contract.forbid:
                    if (
                        is_under(mod.name, item.source)
                        and is_under(imp.target, item.target)
                        and not any(is_under(mod.name, e) for e in item.exempt)
                        and (mod.name, imp.line, id(item)) not in seen
                    ):
                        seen.add((mod.name, imp.line, id(item)))
                        out.append(self._violation(mod, imp, item.why, item.adr))
                for item in ctx.contract.only_allow:
                    if (
                        is_under(mod.name, item.source)
                        and not any(is_under(imp.target, a) for a in item.allowed)
                        and (mod.name, imp.line, id(item)) not in seen
                    ):
                        seen.add((mod.name, imp.line, id(item)))
                        out.append(self._violation(mod, imp, item.why, item.adr))
        return out

    def _violation(self, mod, imp, why: str, adr: str) -> Finding:
        return self.finding(
            f"{mod.name} importa {imp.target}",
            Severity.HIGH, Confidence.CONFIRMADO, loc(mod, imp.line),
            why=f"{why} [{adr}]" if adr else why,
            recommendation="Depender de uma interface (injeção) em vez da implementação, "
                           "ou mover o código para o componente correto.",
        )


def _child(name: str, parent: str) -> str | None:
    if not name.startswith(parent + "."):
        return None
    return name[len(parent) + 1:].split(".", 1)[0]


class SiblingIsolationRule(Rule):
    id = "R003"
    title = "Isolamento entre irmãos (providers)"
    adr = "ADR-1 §3.1"

    def check(self, ctx: Context) -> list[Finding]:
        out: list[Finding] = []
        for item in ctx.contract.siblings:
            for mod in ctx.scan.under(item.parent):
                own = _child(mod.name, item.parent)
                if own is None:
                    continue
                for imp in mod.imports:
                    other = _child(imp.target, item.parent)
                    if other is not None and other != own:
                        out.append(self.finding(
                            f"'{own}' importa '{other}' ({imp.target})",
                            Severity.HIGH, Confidence.CONFIRMADO, loc(mod, imp.line),
                            why=f"{item.why} [{item.adr}]",
                            recommendation="Mover o código compartilhado para a interface "
                                           "do componente pai; nunca entre irmãos.",
                        ))
        return out


class ThirdPartyDependencies(Rule):
    id = "R005"
    title = "Dependências externas restritas"
    adr = "Regra de integração"

    def check(self, ctx: Context) -> list[Finding]:
        out: list[Finding] = []
        for mod in ctx.scan.modules.values():
            allowed = zone_value(mod.name, ctx.contract.third_party) or ()
            if "*" in allowed:
                continue
            reported: set[str] = set()
            for imp in mod.imports:
                if imp.internal or imp.type_only or imp.root in STDLIB:
                    continue
                if imp.root in allowed or imp.root in reported:
                    continue
                reported.add(imp.root)
                out.append(self.finding(
                    f"{mod.name} importa a biblioteca externa '{imp.root}'",
                    Severity.MEDIUM, Confidence.CONFIRMADO, loc(mod, imp.line),
                    why="Tecnologia externa só entra atrás de interface própria e removível.",
                    recommendation="Isolar em um provider/adapter, ou declarar a exceção em "
                                   "contract.third_party depois de avaliar licença e dependências.",
                ))
        return out


class DynamicImports(Rule):
    id = "R006"
    title = "Importação dinâmica controlada"
    adr = "ADR-1 §3.1"

    def check(self, ctx: Context) -> list[Finding]:
        c = ctx.contract
        out: list[Finding] = []
        for mod in ctx.scan.modules.values():
            if any(is_under(mod.name, z) for z in c.dynamic_import_allowed):
                continue
            for call in mod.calls:
                if call_matches(call, c.dynamic_import_calls):
                    out.append(self.finding(
                        f"{mod.name} usa {call.name}() fora do registry",
                        Severity.HIGH, Confidence.PROVAVEL, loc(mod, call.line),
                        why="Importação dinâmica esconde dependências do ADR 0 e pode "
                            "contornar as fronteiras entre componentes.",
                        recommendation="Carregar módulos somente pelo registry, isolando falhas.",
                    ))
        return out
