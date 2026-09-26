"""Leitura estática do código do projeto.

Somente leitura: o scanner abre arquivos para ler e nunca executa nem importa
o código analisado. Um módulo quebrado vira `parse_error`, não uma exceção.
"""
from __future__ import annotations

import ast
import fnmatch
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .contract import Contract

STDLIB = frozenset(getattr(sys, "stdlib_module_names", ())) | {"__future__"}
_MODE_CHARS = set("rwxabt+U")


class ProjectNotFound(Exception):
    """O pacote raiz não existe no diretório informado."""


def is_under(name: str, prefix: str) -> bool:
    return name == prefix or name.startswith(prefix + ".")


@dataclass(frozen=True)
class ImportRecord:
    target: str
    line: int
    internal: bool
    type_only: bool = False
    candidate: bool = False   # `from pkg import x`: x pode ser submódulo

    @property
    def root(self) -> str:
        return self.target.split(".", 1)[0]


@dataclass(frozen=True)
class CallRecord:
    name: str            # nome resolvido pelos aliases (ex.: subprocess.run)
    attr: str            # último segmento (ex.: run)
    line: int
    mode: str | None = None


@dataclass(frozen=True)
class FunctionInfo:
    name: str
    line: int
    length: int


@dataclass
class ModuleInfo:
    name: str
    path: Path
    rel_path: str
    is_package: bool
    lines: int = 0
    imports: list[ImportRecord] = field(default_factory=list)
    calls: list[CallRecord] = field(default_factory=list)
    functions: list[FunctionInfo] = field(default_factory=list)
    parse_error: str | None = None


@dataclass
class ProjectScan:
    root: Path
    package: str
    modules: dict[str, ModuleInfo]

    def under(self, prefix: str) -> list[ModuleInfo]:
        return [m for m in self.modules.values() if is_under(m.name, prefix)]

    def parse(self, module_name: str) -> ast.Module | None:
        """Relê e interpreta um módulo (para regras que inspecionam valores)."""
        info = self.modules.get(module_name)
        if info is None or info.parse_error:
            return None
        try:
            return ast.parse(info.path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, ValueError):
            return None


def call_matches(call: CallRecord, patterns: tuple[str, ...]) -> bool:
    """`.nome` casa pelo último segmento; demais padrões casam o nome resolvido."""
    for pattern in patterns:
        if pattern.startswith("."):
            if call.attr == pattern[1:]:
                return True
        elif fnmatch.fnmatchcase(call.name, pattern):
            return True
    return False


def _is_type_checking(test: ast.expr) -> bool:
    if isinstance(test, ast.Name):
        return test.id == "TYPE_CHECKING"
    return isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"


class _Extractor(ast.NodeVisitor):
    def __init__(self, module: str, is_package: bool, package: str, watched: tuple[str, ...]):
        self.module, self.is_package, self.package = module, is_package, package
        self.watched = watched
        self.imports: list[ImportRecord] = []
        self.calls: list[CallRecord] = []
        self.functions: list[FunctionInfo] = []
        self.aliases: dict[str, str] = {}
        self._type_depth = 0

    def run(self, tree: ast.AST) -> None:
        self._collect_aliases(tree)
        self.visit(tree)

    # -- imports ------------------------------------------------------------
    def _resolve(self, node: ast.ImportFrom) -> str | None:
        if node.level == 0:
            return node.module
        parts = self.module.split(".")
        if not self.is_package:
            parts = parts[:-1]
        up = node.level - 1
        if up >= len(parts) and up > 0:
            return None
        if up:
            parts = parts[:-up]
        base = ".".join(parts)
        if node.module:
            base = f"{base}.{node.module}" if base else node.module
        return base or None

    def _collect_aliases(self, tree: ast.AST) -> None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.asname:
                        self.aliases[alias.asname] = alias.name
                    else:
                        root = alias.name.split(".", 1)[0]
                        self.aliases.setdefault(root, root)
            elif isinstance(node, ast.ImportFrom):
                base = self._resolve(node)
                for alias in node.names:
                    if base and alias.name != "*":
                        self.aliases[alias.asname or alias.name] = f"{base}.{alias.name}"

    def _add_import(self, target: str, line: int, candidate: bool = False) -> None:
        root = target.split(".", 1)[0]
        self.imports.append(ImportRecord(
            target, line, internal=(root == self.package),
            type_only=self._type_depth > 0, candidate=candidate,
        ))

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._add_import(alias.name, node.lineno)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        base = self._resolve(node)
        if base is None:
            return
        self._add_import(base, node.lineno)
        for alias in node.names:
            if alias.name != "*":
                self._add_import(f"{base}.{alias.name}", node.lineno, candidate=True)

    def visit_If(self, node: ast.If) -> None:
        if not _is_type_checking(node.test):
            self.generic_visit(node)
            return
        self._type_depth += 1
        for child in node.body:
            self.visit(child)
        self._type_depth -= 1
        for child in node.orelse:
            self.visit(child)

    # -- funções e chamadas -------------------------------------------------
    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        end = getattr(node, "end_lineno", None) or node.lineno
        self.functions.append(FunctionInfo(node.name, node.lineno, end - node.lineno + 1))
        self.generic_visit(node)

    visit_FunctionDef = _visit_function
    visit_AsyncFunctionDef = _visit_function

    def _call_name(self, func: ast.expr) -> tuple[str, str]:
        parts: list[str] = []
        cur = func
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        parts.append(cur.id if isinstance(cur, ast.Name) else "?")
        parts.reverse()
        parts[0] = self.aliases.get(parts[0], parts[0])
        return ".".join(parts), parts[-1]

    @staticmethod
    def _mode_of(node: ast.Call, name: str, attr: str) -> str | None:
        """Modo de abertura de `open`; None quando a chamada não é uma abertura."""
        if attr != "open":
            return None
        index = 1 if name in ("open", "io.open") else 0
        value: ast.expr | None = node.args[index] if len(node.args) > index else None
        if value is None:
            value = next((kw.value for kw in node.keywords if kw.arg == "mode"), None)
        if value is None:
            return "r"
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            if index == 1 or set(value.value) <= _MODE_CHARS:
                return value.value
            return None    # ex.: webbrowser.open(url): não é modo de arquivo
        return "?"

    def visit_Call(self, node: ast.Call) -> None:
        name, attr = self._call_name(node.func)
        record = CallRecord(name, attr, node.lineno, self._mode_of(node, name, attr))
        if call_matches(record, self.watched):
            self.calls.append(record)
        self.generic_visit(node)


def _scan_file(path: Path, root: Path, package: str, watched: tuple[str, ...]) -> ModuleInfo:
    rel = path.relative_to(root)
    parts = list(rel.with_suffix("").parts)
    is_package = parts[-1] == "__init__"
    if is_package:
        parts.pop()
    info = ModuleInfo(".".join(parts), path, rel.as_posix(), is_package)
    try:
        source = path.read_text(encoding="utf-8")
        info.lines = len(source.splitlines())
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        info.parse_error = f"erro de sintaxe: {exc.msg} (linha {exc.lineno})"
        return info
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        info.parse_error = f"{type(exc).__name__}: {exc}"
        return info
    extractor = _Extractor(info.name, is_package, package, watched)
    extractor.run(tree)
    info.imports, info.calls, info.functions = (
        extractor.imports, extractor.calls, extractor.functions,
    )
    return info


def scan_project(root: Path | str, contract: Contract) -> ProjectScan:
    root = Path(root).resolve()
    package_dir = root / contract.root_package
    if not package_dir.is_dir():
        raise ProjectNotFound(f"pacote '{contract.root_package}' não encontrado em {root}")
    watched = contract.watched_calls()
    modules: dict[str, ModuleInfo] = {}
    for path in sorted(package_dir.rglob("*.py")):
        rel = path.relative_to(root)
        if any(part in contract.exclude_dirs for part in rel.parts):
            continue
        info = _scan_file(path, root, contract.root_package, watched)
        modules[info.name] = info
    known = set(modules)
    for info in modules.values():
        info.imports = [i for i in info.imports if not i.candidate or i.target in known]
    return ProjectScan(root, contract.root_package, modules)
