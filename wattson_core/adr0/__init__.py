"""ADR 0 — Autoanálise, Diagnóstico e Fitness Arquitetural.

Observa e diagnostica; não controla. Só usa a biblioteca padrão e nunca
importa o resto do Wattson: precisa funcionar quando o resto estiver quebrado.
"""
from .contract import CONTRACT, Contract
from .engine import FitnessEngine, exit_code
from .models import Confidence, Finding, Report, RuleResult, Severity, Status

__version__ = "0.1.0"
__all__ = [
    "CONTRACT", "Contract", "FitnessEngine", "exit_code",
    "Confidence", "Finding", "Report", "RuleResult", "Severity", "Status",
]
