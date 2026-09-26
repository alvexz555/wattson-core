"""Renderização do relatório (texto e JSON). Só formata; não decide nada."""
from __future__ import annotations

import json

from .models import Finding, Report, RuleResult, Severity

_EMOJI = {"PASS": "🟢", "FAIL": "🔴", "WARN": "🟡", "SKIP": "⚪", "ERROR": "🟠"}
_PLAIN = {"PASS": "[ OK ]", "FAIL": "[FAIL]", "WARN": "[WARN]", "SKIP": "[SKIP]", "ERROR": "[ERR ]"}
_VERDICT_ICON = {"OK": "🟢", "ATENÇÃO": "🟡", "VIOLAÇÕES": "🔴"}
_SECTIONS = (("architecture", "ARQUITETURA"), ("health", "SAÚDE"))
_BAR = "═" * 62


def to_dict(report: Report) -> dict:
    return {
        "root": report.root,
        "generated_at": report.generated_at,
        "python": report.python,
        "modules_scanned": report.modules_scanned,
        "duration_ms": round(report.duration_ms, 1),
        "verdict": report.verdict(),
        "counts": report.counts(),
        "results": [
            {
                "rule_id": r.rule_id, "title": r.title, "adr": r.adr,
                "category": r.category, "status": r.status.value, "note": r.note,
                "elapsed_ms": round(r.elapsed_ms, 2),
                "findings": [
                    {
                        "message": f.message, "severity": f.severity.name,
                        "confidence": f.confidence.value, "location": f.location,
                        "why": f.why, "recommendation": f.recommendation,
                    }
                    for f in r.findings
                ],
            }
            for r in report.results
        ],
    }


def render_json(report: Report) -> str:
    return json.dumps(to_dict(report), ensure_ascii=False, indent=2)


def _render_finding(finding: Finding) -> list[str]:
    head = f"    • [{finding.severity.name} · {finding.confidence.value}]"
    if finding.location:
        head += f" {finding.location}"
    lines = [head, f"      {finding.message}"]
    if finding.why:
        lines.append(f"      Por quê: {finding.why}")
    if finding.recommendation:
        lines.append(f"      Fazer:   {finding.recommendation}")
    return lines


def _render_rule(result: RuleResult, icons: dict[str, str], max_findings: int) -> list[str]:
    line = f"  {icons[result.status.value]} {result.rule_id}  {result.title}"
    if result.note:
        line += f"  — {result.note}"
    lines = [line]
    for finding in result.findings[:max_findings]:
        lines.extend(_render_finding(finding))
    hidden = len(result.findings) - max_findings
    if hidden > 0:
        lines.append(f"    … e mais {hidden} achado(s) (use --max-findings ou --format json)")
    return lines


def _summary(report: Report, emoji: bool) -> list[str]:
    counts = report.counts()
    verdict = report.verdict()
    icon = _VERDICT_ICON[verdict] + " " if emoji else ""
    by_severity = {s: 0 for s in Severity}
    for finding in report.all_findings():
        by_severity[finding.severity] += 1
    severities = "  ".join(
        f"{s.name}: {n}" for s, n in sorted(by_severity.items(), reverse=True) if n
    ) or "nenhum achado"
    return [
        _BAR,
        f" VEREDITO: {icon}{verdict}",
        f" Regras: {counts['PASS']} ok · {counts['FAIL']} falha · {counts['WARN']} atenção · "
        f"{counts['SKIP']} n/a · {counts['ERROR']} erro",
        f" Achados: {severities}",
        " Análise estática: CONFIRMADO é fato do código; PROVÁVEL/POSSÍVEL são indícios.",
        _BAR,
    ]


def render_text(report: Report, emoji: bool = True, max_findings: int = 10) -> str:
    icons = _EMOJI if emoji else _PLAIN
    lines = [
        _BAR, " ADR 0 — DIAGNÓSTICO ARQUITETURAL", _BAR,
        f"Projeto : {report.root}",
        f"Gerado  : {report.generated_at}",
        f"Python  : {report.python}",
        f"Módulos : {report.modules_scanned}   Regras: {len(report.results)}"
        f"   Duração: {report.duration_ms:.0f} ms",
        "",
    ]
    for category, title in _SECTIONS:
        group = [r for r in report.results if r.category == category]
        if not group:
            continue
        lines += [title, "─" * len(title)]
        for result in group:
            lines.extend(_render_rule(result, icons, max_findings))
        lines.append("")
    lines.extend(_summary(report, emoji))
    return "\n".join(lines)
