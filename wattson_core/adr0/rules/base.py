"""Base das regras do ADR 0."""
from __future__ import annotations

from dataclasses import dataclass

from ..contract import Contract
from ..models import Confidence, Finding, Severity
from ..scanner import ModuleInfo, ProjectScan


class Skip(Exception):
    """A regra ainda não se aplica (o componente verificado não existe)."""


@dataclass
class Context:
    scan: ProjectScan
    contract: Contract


def loc(module: ModuleInfo, line: int | None = None) -> str:
    return f"{module.rel_path}:{line}" if line else module.rel_path


def zone_value(name: str, mapping: dict[str, tuple[str, ...]]) -> tuple[str, ...] | None:
    """Valor da zona mais específica que contém `name` (prefixo mais longo)."""
    best: str | None = None
    for prefix in mapping:
        if (name == prefix or name.startswith(prefix + ".")) and (
            best is None or len(prefix) > len(best)
        ):
            best = prefix
    return mapping[best] if best is not None else None


class Rule:
    id = ""
    title = ""
    adr = ""
    category = "architecture"   # "architecture" | "health"

    def check(self, ctx: Context) -> list[Finding]:
        raise NotImplementedError

    def finding(
        self,
        message: str,
        severity: Severity,
        confidence: Confidence,
        location: str | None = None,
        why: str = "",
        recommendation: str = "",
    ) -> Finding:
        return Finding(self.id, message, severity, confidence, location, why, recommendation)
