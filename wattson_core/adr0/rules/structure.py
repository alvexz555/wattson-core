"""Regras de estrutura: integridade, ciclos e tamanho (God Script)."""
from __future__ import annotations

from ..models import Confidence, Finding, Severity
from ..scanner import is_under
from .base import Context, Rule, loc


class ModuleIntegrity(Rule):
    id = "R001"
    title = "Integridade dos módulos"
    adr = "ADR-0"

    def check(self, ctx: Context) -> list[Finding]:
        return [
            self.finding(
                f"Módulo não pôde ser analisado: {mod.parse_error}",
                Severity.HIGH, Confidence.CONFIRMADO, loc(mod),
                why="Um arquivo ilegível deixa as demais regras cegas a ele.",
                recommendation="Corrigir o erro de sintaxe/codificação.",
            )
            for mod in ctx.scan.modules.values() if mod.parse_error
        ]


def strongly_connected(graph: dict[str, list[str]]) -> list[list[str]]:
    """Tarjan iterativo (sem risco de estourar a recursão)."""
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    components: list[list[str]] = []
    counter = 0
    for start in graph:
        if start in index:
            continue
        index[start] = low[start] = counter
        counter += 1
        stack.append(start)
        on_stack.add(start)
        work = [(start, iter(graph[start]))]
        while work:
            node, neighbours = work[-1]
            descended = False
            for nxt in neighbours:
                if nxt not in index:
                    index[nxt] = low[nxt] = counter
                    counter += 1
                    stack.append(nxt)
                    on_stack.add(nxt)
                    work.append((nxt, iter(graph[nxt])))
                    descended = True
                    break
                if nxt in on_stack:
                    low[node] = min(low[node], index[nxt])
            if descended:
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
            if low[node] == index[node]:
                component = []
                while True:
                    member = stack.pop()
                    on_stack.discard(member)
                    component.append(member)
                    if member == node:
                        break
                components.append(component)
    return components


class ImportCycles(Rule):
    id = "R004"
    title = "Sem ciclos de importação"
    adr = "ADR-7 (componentes independentes)"

    def check(self, ctx: Context) -> list[Finding]:
        modules = ctx.scan.modules
        graph: dict[str, list[str]] = {name: [] for name in modules}
        for mod in modules.values():
            for imp in mod.imports:
                target = imp.target
                if (
                    imp.internal and not imp.type_only and target in modules
                    and target != mod.name
                    and not is_under(mod.name, target)   # importar o pacote-pai é normal
                    and target not in graph[mod.name]
                ):
                    graph[mod.name].append(target)
        out: list[Finding] = []
        for component in strongly_connected(graph):
            if len(component) < 2:
                continue
            names = sorted(component)
            out.append(self.finding(
                "Ciclo de importação: " + " ↔ ".join(names),
                Severity.MEDIUM, Confidence.CONFIRMADO, loc(modules[names[0]]),
                why="Módulos que se importam mutuamente não são independentes nem substituíveis.",
                recommendation="Extrair a dependência comum para uma interface, "
                               "ou inverter uma das direções.",
            ))
        return out


class GodScript(Rule):
    id = "R008"
    title = "Sem God Script"
    adr = "ADR-2 / ADR-7 (restrições)"

    def check(self, ctx: Context) -> list[Finding]:
        c = ctx.contract
        out: list[Finding] = []
        for mod in ctx.scan.modules.values():
            if mod.parse_error:
                continue
            if mod.path.name in c.entrypoint_names and mod.lines > c.entrypoint_max_lines:
                out.append(self.finding(
                    f"Ponto de entrada com {mod.lines} linhas (limite {c.entrypoint_max_lines})",
                    Severity.MEDIUM, Confidence.PROVAVEL, loc(mod),
                    why="Lógica dentro do main é o começo de um monólito.",
                    recommendation="Manter o entrypoint apenas iniciando o Runtime/CLI.",
                ))
            if mod.lines > c.max_file_lines:
                out.append(self.finding(
                    f"Arquivo com {mod.lines} linhas (limite {c.max_file_lines})",
                    Severity.MEDIUM, Confidence.PROVAVEL, loc(mod),
                    why="Tamanho é um sinal, não uma prova: pode haver mais de uma responsabilidade.",
                    recommendation="Separar por responsabilidade.",
                ))
            for fn in mod.functions:
                if fn.length > c.max_function_lines:
                    out.append(self.finding(
                        f"Função '{fn.name}' com {fn.length} linhas (limite {c.max_function_lines})",
                        Severity.LOW, Confidence.PROVAVEL, loc(mod, fn.line),
                        recommendation="Quebrar em funções menores.",
                    ))
        return out
