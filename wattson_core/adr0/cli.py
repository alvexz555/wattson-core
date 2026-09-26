"""Interface de linha de comando do ADR 0."""
from __future__ import annotations

import argparse
import sys

from .engine import FitnessEngine, exit_code
from .models import Severity
from .report import render_json, render_text
from .scanner import ProjectNotFound

_FAIL_ON = {s.name.lower(): s for s in Severity}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m wattson_core.adr0",
        description="ADR 0 — diagnóstico arquitetural do Wattson (somente leitura).",
    )
    parser.add_argument("root", nargs="?", default=".",
                        help="pasta que contém o pacote wattson_core (padrão: .)")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--category", choices=("architecture", "health"))
    parser.add_argument("--only", nargs="+", metavar="ID", default=[])
    parser.add_argument("--skip", nargs="+", metavar="ID", default=[])
    parser.add_argument("--fail-on", choices=[*_FAIL_ON, "never"], default="high",
                        help="severidade mínima que gera código de saída 1 (padrão: high)")
    parser.add_argument("--max-findings", type=int, default=10)
    parser.add_argument("--no-emoji", action="store_true")
    parser.add_argument("--list-rules", action="store_true")
    return parser


def _can_print_emoji() -> bool:
    try:
        "🟢".encode(sys.stdout.encoding or "utf-8")
    except (UnicodeEncodeError, LookupError):
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    engine = FitnessEngine(args.root)
    if args.list_rules:
        for rule in engine.rules:
            print(f"{rule.id}  {rule.category:<12} {rule.title}  [{rule.adr}]")
        return 0
    try:
        report = engine.run(args.only, args.skip, args.category)
    except ProjectNotFound as exc:
        print(f"ADR 0: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(render_json(report))
    else:
        emoji = not args.no_emoji and _can_print_emoji()
        print(render_text(report, emoji, args.max_findings))
    return exit_code(report, _FAIL_ON.get(args.fail_on))
