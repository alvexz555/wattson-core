"""Fitness Engine: executa as regras e monta o relatório.

Princípio: uma regra defeituosa nunca derruba o diagnóstico. Ela vira um
resultado ERROR (INDETERMINADO) e as demais regras continuam.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Iterable

from .contract import CONTRACT, Contract
from .models import Finding, Report, RuleResult, Severity, Status
from .rules import all_rules
from .rules.base import Context, Rule, Skip
from .scanner import scan_project


def derive_status(findings: list[Finding]) -> Status:
    if not findings:
        return Status.PASS
    worst = max(f.severity for f in findings)
    if worst >= Severity.MEDIUM:
        return Status.FAIL
    if worst == Severity.LOW:
        return Status.WARN
    return Status.PASS   # INFO não é problema: aparece no relatório como nota


def _run_rule(rule: Rule, ctx: Context) -> RuleResult:
    result = RuleResult(rule.id, rule.title, rule.adr, rule.category, Status.PASS)
    started = perf_counter()
    try:
        result.findings = list(rule.check(ctx))
        result.status = derive_status(result.findings)
    except Skip as skip:
        result.status, result.note = Status.SKIP, str(skip)
    except Exception as exc:  # noqa: BLE001 - regra defeituosa não derruba o diagnóstico
        result.status = Status.ERROR
        result.note = f"a regra falhou ({type(exc).__name__}: {exc}); resultado INDETERMINADO"
    result.elapsed_ms = (perf_counter() - started) * 1000
    return result


class FitnessEngine:
    def __init__(
        self,
        root: Path | str = ".",
        contract: Contract = CONTRACT,
        rules: Iterable[Rule] | None = None,
    ):
        self.root = Path(root)
        self.contract = contract
        self.rules = list(rules) if rules is not None else all_rules()

    def select(
        self, only: Iterable[str] = (), skip: Iterable[str] = (), category: str | None = None
    ) -> list[Rule]:
        only_ids = {r.upper() for r in only}
        skip_ids = {r.upper() for r in skip}
        return [
            r for r in self.rules
            if (not only_ids or r.id.upper() in only_ids)
            and r.id.upper() not in skip_ids
            and (category is None or r.category == category)
        ]

    def run(
        self, only: Iterable[str] = (), skip: Iterable[str] = (), category: str | None = None
    ) -> Report:
        started = perf_counter()
        scan = scan_project(self.root, self.contract)
        ctx = Context(scan, self.contract)
        results = [_run_rule(rule, ctx) for rule in self.select(only, skip, category)]
        results.sort(key=lambda r: (r.category, r.rule_id))
        return Report(
            root=str(scan.root),
            generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            python=sys.version.split()[0],
            modules_scanned=len(scan.modules),
            duration_ms=(perf_counter() - started) * 1000,
            results=results,
        )


def exit_code(report: Report, fail_on: Severity | None) -> int:
    """0 = ok · 1 = violação na severidade pedida · 2 = diagnóstico incompleto."""
    if fail_on is not None and any(f.severity >= fail_on for f in report.all_findings()):
        return 1
    if any(r.status == Status.ERROR for r in report.results):
        return 2
    return 0
