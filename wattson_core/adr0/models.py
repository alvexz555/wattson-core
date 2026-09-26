"""Modelos de dados do ADR 0.

Somente dados: nenhuma lógica de I/O mora aqui.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum


class Severity(IntEnum):
    INFO = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class Confidence(Enum):
    """O ADR 0 nunca transforma hipótese em certeza (ADR 7)."""

    CONFIRMADO = "CONFIRMADO"
    PROVAVEL = "PROVÁVEL"
    POSSIVEL = "POSSÍVEL"
    INDETERMINADO = "INDETERMINADO"


class Status(Enum):
    PASS = "PASS"      # nenhuma violação
    FAIL = "FAIL"      # violação de severidade MEDIUM ou maior
    WARN = "WARN"      # apenas achados LOW
    SKIP = "SKIP"      # regra ainda não se aplica (componente não existe)
    ERROR = "ERROR"    # a própria regra falhou: resultado INDETERMINADO


@dataclass(frozen=True)
class Finding:
    rule_id: str
    message: str
    severity: Severity
    confidence: Confidence
    location: str | None = None
    why: str = ""
    recommendation: str = ""


@dataclass
class RuleResult:
    rule_id: str
    title: str
    adr: str
    category: str
    status: Status
    findings: list[Finding] = field(default_factory=list)
    note: str = ""
    elapsed_ms: float = 0.0


@dataclass
class Report:
    root: str
    generated_at: str
    python: str
    modules_scanned: int
    duration_ms: float
    results: list[RuleResult] = field(default_factory=list)

    def all_findings(self) -> list[Finding]:
        return [f for r in self.results for f in r.findings]

    def counts(self) -> dict[str, int]:
        counts = {s.value: 0 for s in Status}
        for result in self.results:
            counts[result.status.value] += 1
        return counts

    def verdict(self) -> str:
        counts = self.counts()
        if counts["FAIL"]:
            return "VIOLAÇÕES"
        if counts["WARN"] or counts["ERROR"]:
            return "ATENÇÃO"
        return "OK"
