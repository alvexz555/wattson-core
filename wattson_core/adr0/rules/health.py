"""Verificações de saúde do ambiente (leitura apenas).

Ainda não existem verificações de runtime, serviços e latência: elas dependem
do Runtime e do Event Log (Fase 1) e entram como novas regras quando existirem.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import sys

from ..models import Confidence, Finding, Severity
from ..scanner import STDLIB, is_under
from .base import Context, Rule, Skip

MIN_PYTHON = (3, 10)


class PythonVersion(Rule):
    id = "H001"
    title = "Versão do Python"
    adr = "ADR-0"
    category = "health"

    def check(self, ctx: Context) -> list[Finding]:
        if sys.version_info >= MIN_PYTHON:
            return []
        return [self.finding(
            f"Python {sys.version_info.major}.{sys.version_info.minor} em uso; "
            f"mínimo {MIN_PYTHON[0]}.{MIN_PYTHON[1]}",
            Severity.CRITICAL, Confidence.CONFIRMADO,
            recommendation="Atualizar o Python (VAIO e Pi 4 devem usar versões compatíveis).",
        )]


class DiskSpace(Rule):
    id = "H002"
    title = "Espaço em disco"
    adr = "ADR-0"
    category = "health"

    def check(self, ctx: Context) -> list[Finding]:
        try:
            usage = shutil.disk_usage(ctx.scan.root)
        except OSError as exc:
            raise Skip(f"não foi possível ler o disco: {exc}") from exc
        ratio = usage.free / usage.total if usage.total else 1.0
        limit = ctx.contract.disk_min_free_ratio
        if ratio >= limit:
            return []
        severity = Severity.HIGH if ratio < limit / 2 else Severity.MEDIUM
        return [self.finding(
            f"Apenas {ratio:.0%} de espaço livre (mínimo {limit:.0%})",
            severity, Confidence.CONFIRMADO,
            why="Disco cheio quebra logs, memória, backup e atualização (cartão SD do Pi).",
            recommendation="Liberar espaço antes de atualizar ou gravar dados.",
        )]


def _read_meminfo() -> dict[str, int]:
    values: dict[str, int] = {}
    with open("/proc/meminfo", encoding="utf-8") as handle:
        for line in handle:
            key, _, rest = line.partition(":")
            fields = rest.split()
            if fields and fields[0].isdigit():
                values[key] = int(fields[0])
    return values


class MemoryAvailable(Rule):
    id = "H003"
    title = "Memória disponível"
    adr = "ADR-0"
    category = "health"

    def check(self, ctx: Context) -> list[Finding]:
        try:
            info = _read_meminfo()
        except OSError as exc:
            raise Skip("/proc/meminfo indisponível nesta plataforma") from exc
        total, available = info.get("MemTotal"), info.get("MemAvailable")
        if not total or available is None:
            raise Skip("MemAvailable não informado pelo sistema")
        ratio = available / total
        limit = ctx.contract.memory_min_available_ratio
        if ratio >= limit:
            return []
        return [self.finding(
            f"Apenas {ratio:.0%} da memória disponível (mínimo {limit:.0%})",
            Severity.MEDIUM, Confidence.CONFIRMADO,
            recommendation="Verificar processos e modelos carregados.",
        )]


class LoadAverage(Rule):
    id = "H004"
    title = "Carga do sistema"
    adr = "ADR-0"
    category = "health"

    def check(self, ctx: Context) -> list[Finding]:
        if not hasattr(os, "getloadavg"):
            raise Skip("carga média indisponível nesta plataforma")
        per_cpu = os.getloadavg()[1] / (os.cpu_count() or 1)
        limit = ctx.contract.load_max_per_cpu
        if per_cpu <= limit:
            return []
        return [self.finding(
            f"Carga de 5 min por CPU = {per_cpu:.2f} (máximo {limit:.2f})",
            Severity.LOW, Confidence.PROVAVEL,
            why="Carga alta pode ser transitória; confirmar com medições repetidas.",
        )]


class OptionalProviders(Rule):
    id = "H005"
    title = "Providers opcionais (degradação isolada)"
    adr = "ADR-1 §3.1"
    category = "health"

    def check(self, ctx: Context) -> list[Finding]:
        out: list[Finding] = []
        for zone in ctx.contract.optional_zones:
            for mod in ctx.scan.under(zone):
                out.extend(self._missing(mod, zone))
        return out

    def _missing(self, mod, zone: str) -> list[Finding]:
        provider = mod.name[len(zone) + 1:].split(".", 1)[0] if is_under(mod.name, zone) else mod.name
        found: list[Finding] = []
        reported: set[str] = set()
        for imp in mod.imports:
            if imp.internal or imp.type_only or imp.root in STDLIB or imp.root in reported:
                continue
            reported.add(imp.root)
            try:
                available = importlib.util.find_spec(imp.root) is not None
            except (ImportError, ValueError):
                available = False
            if not available:
                found.append(self.finding(
                    f"Provider '{provider}' indisponível: dependência '{imp.root}' não instalada",
                    Severity.INFO, Confidence.CONFIRMADO,
                    why="Providers são opcionais; o Wattson segue funcionando sem eles.",
                ))
        return found
