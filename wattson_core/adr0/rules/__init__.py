"""Catálogo de regras do ADR 0.

O catálogo é uma lista explícita: uma regra só existe se estiver aqui.
"""
from __future__ import annotations

from .base import Rule
from .boundaries import (
    ComponentBoundaries,
    DynamicImports,
    SiblingIsolationRule,
    ThirdPartyDependencies,
)
from .health import DiskSpace, LoadAverage, MemoryAvailable, OptionalProviders, PythonVersion
from .safety import ExecutionOnlyInExecutor, ReadOnlyObserver, SafeBoot
from .structure import GodScript, ImportCycles, ModuleIntegrity


def all_rules() -> list[Rule]:
    return [
        ModuleIntegrity(),
        ComponentBoundaries(),
        SiblingIsolationRule(),
        ImportCycles(),
        ThirdPartyDependencies(),
        DynamicImports(),
        ExecutionOnlyInExecutor(),
        GodScript(),
        SafeBoot(),
        ReadOnlyObserver(),
        PythonVersion(),
        DiskSpace(),
        MemoryAvailable(),
        LoadAverage(),
        OptionalProviders(),
    ]
