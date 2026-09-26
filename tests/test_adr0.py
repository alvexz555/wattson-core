"""Testes do ADR 0.

Cada regra é provada nos dois sentidos: detecta a violação proposital e não
acusa o projeto saudável. Rodar da raiz do projeto:

    python -m unittest discover -s tests -t . -v
"""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from wattson_core.adr0 import FitnessEngine, Severity, Status, exit_code
from wattson_core.adr0.cli import main as cli_main
from wattson_core.adr0.models import Confidence
from wattson_core.adr0.rules.base import Rule
from wattson_core.adr0.rules.structure import strongly_connected

PROJECT_ROOT = Path(__file__).resolve().parents[1]

HEALTHY = {
    "wattson_core/__init__.py": "",
    "wattson_core/core/__init__.py": "",
    "wattson_core/core/orchestrator.py": (
        "from wattson_core.ai.interface import AIProvider\n"
        "class Orchestrator:\n"
        "    def __init__(self, ai: AIProvider | None = None):\n"
        "        self.ai = ai\n"
    ),
    "wattson_core/ai/__init__.py": "",
    "wattson_core/ai/interface.py": (
        "from typing import Protocol\n"
        "class AIProvider(Protocol):\n"
        "    def generate(self, prompt: str) -> str: ...\n"
    ),
    "wattson_core/ai/registry.py": (
        "import importlib\n"
        "def load(name):\n"
        "    try:\n"
        "        return importlib.import_module(f'wattson_core.ai.providers.{name}')\n"
        "    except Exception:\n"
        "        return None\n"
    ),
    "wattson_core/ai/providers/__init__.py": "",
    "wattson_core/ai/providers/echo.py": "from wattson_core.ai.interface import AIProvider\n",
    "wattson_core/ai/providers/fake_llm.py": (
        "import biblioteca_que_nao_existe_xyz\n"
        "from wattson_core.ai.interface import AIProvider\n"
    ),
    "wattson_core/executor/__init__.py": "",
    "wattson_core/executor/runner.py": "import subprocess\n",
    "wattson_core/security/__init__.py": "",
    "wattson_core/security/boot.py": (
        "BOOT_STATE = {'MODE': 'CHAT_ONLY', 'EXECUTION': 'LOCKED', 'DIRECT_COMMAND': 'OFF',\n"
        "              'DEVICE_CONTROL': 'OFF', 'PRIVILEGED_ACTIONS': 'OFF'}\n"
    ),
}


class ProjectCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def analyze(self, files: dict[str, str] | None = None, **overrides):
        """Cria o projeto saudável, aplica `files` por cima e roda a arquitetura."""
        tree = {**HEALTHY, **(files or {})}
        for rel, content in tree.items():
            if content is None:
                continue
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        report = FitnessEngine(self.root).run(category="architecture", **overrides)
        return {r.rule_id: r for r in report.results}, report

    def assertViolation(self, results, rule_id, severity=Severity.HIGH):
        result = results[rule_id]
        self.assertEqual(result.status, Status.FAIL, f"{rule_id} deveria falhar: {result}")
        self.assertTrue(any(f.severity >= severity for f in result.findings))
        return result


class HealthyProject(ProjectCase):
    def test_healthy_project_has_no_violations(self):
        results, report = self.analyze()
        failing = {k: v.findings for k, v in results.items() if v.status == Status.FAIL}
        self.assertEqual(failing, {})
        self.assertIn(report.verdict(), ("OK", "ATENÇÃO"))
        self.assertEqual(results["R009"].status, Status.PASS)

    def test_provider_with_missing_dependency_is_only_informational(self):
        report = FitnessEngine(self._write_healthy()).run(only=["H005"])
        result = report.results[0]
        self.assertEqual(result.status, Status.PASS)
        self.assertTrue(any("fake_llm" in f.message for f in result.findings))
        self.assertTrue(all(f.severity == Severity.INFO for f in result.findings))

    def _write_healthy(self) -> Path:
        self.analyze()
        return self.root


class BoundaryRules(ProjectCase):
    def test_core_importing_provider_is_a_violation(self):
        results, _ = self.analyze({
            "wattson_core/core/orchestrator.py": "from wattson_core.ai.providers.echo import x\n"})
        result = self.assertViolation(results, "R002")
        self.assertEqual(result.findings[0].confidence, Confidence.CONFIRMADO)
        self.assertIn("core/orchestrator.py", result.findings[0].location)

    def test_from_package_import_submodule_is_caught(self):
        results, _ = self.analyze({
            "wattson_core/core/orchestrator.py": "from wattson_core.ai.providers import echo\n"})
        self.assertViolation(results, "R002")

    def test_relative_import_is_resolved(self):
        results, _ = self.analyze({
            "wattson_core/core/orchestrator.py": "from ..ai.providers import echo\n"})
        self.assertViolation(results, "R002")

    def test_core_importing_registry_is_a_violation(self):
        results, _ = self.analyze({
            "wattson_core/core/orchestrator.py": "from wattson_core.ai import registry\n"})
        self.assertViolation(results, "R002")

    def test_ai_importing_core_or_executor_is_a_violation(self):
        results, _ = self.analyze({
            "wattson_core/ai/providers/echo.py": "from wattson_core.core.orchestrator import Orchestrator\n"})
        self.assertViolation(results, "R002")

    def test_type_checking_import_is_still_a_boundary_violation(self):
        results, _ = self.analyze({
            "wattson_core/core/orchestrator.py": (
                "from typing import TYPE_CHECKING\n"
                "if TYPE_CHECKING:\n"
                "    from wattson_core.ai.providers.echo import x\n")})
        self.assertViolation(results, "R002")

    def test_provider_importing_provider_is_a_violation(self):
        results, _ = self.analyze({
            "wattson_core/ai/providers/echo.py": "from wattson_core.ai.providers import fake_llm\n"})
        self.assertViolation(results, "R003")

    def test_adr0_importing_the_rest_of_the_system_is_a_violation(self):
        results, _ = self.analyze({
            "wattson_core/adr0/__init__.py": "",
            "wattson_core/adr0/x.py": "from wattson_core.core import orchestrator\n"})
        self.assertViolation(results, "R002")

    def test_anything_importing_adr0_is_a_violation(self):
        results, _ = self.analyze({
            "wattson_core/adr0/__init__.py": "",
            "wattson_core/core/orchestrator.py": "from wattson_core.adr0 import FitnessEngine\n"})
        self.assertViolation(results, "R002")


class DependencyRules(ProjectCase):
    def test_third_party_in_core_is_flagged_but_not_in_provider(self):
        results, _ = self.analyze({
            "wattson_core/core/orchestrator.py": "import requests\n"})
        result = self.assertViolation(results, "R005", Severity.MEDIUM)
        self.assertEqual(len(result.findings), 1)
        self.assertIn("requests", result.findings[0].message)

    def test_dynamic_import_outside_registry_is_flagged(self):
        results, _ = self.analyze({
            "wattson_core/core/orchestrator.py": (
                "import importlib\nimportlib.import_module('x')\n__import__('y')\n")})
        result = self.assertViolation(results, "R006")
        self.assertEqual(len(result.findings), 2)

    def test_import_cycle_is_detected(self):
        results, _ = self.analyze({
            "wattson_core/core/a.py": "from wattson_core.core import b\n",
            "wattson_core/core/b.py": "from wattson_core.core import a\n"})
        result = self.assertViolation(results, "R004", Severity.MEDIUM)
        self.assertIn("wattson_core.core.a", result.findings[0].message)

    def test_type_checking_import_does_not_create_cycle(self):
        results, _ = self.analyze({
            "wattson_core/core/a.py": "from wattson_core.core import b\n",
            "wattson_core/core/b.py": (
                "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n"
                "    from wattson_core.core import a\n")})
        self.assertEqual(results["R004"].status, Status.PASS)

    def test_tarjan_finds_only_real_cycles(self):
        graph = {"a": ["b"], "b": ["c"], "c": ["a"], "d": ["a"], "e": []}
        cycles = [sorted(c) for c in strongly_connected(graph) if len(c) > 1]
        self.assertEqual(cycles, [["a", "b", "c"]])


class ExecutionRules(ProjectCase):
    def test_subprocess_outside_executor_is_flagged(self):
        results, _ = self.analyze({
            "wattson_core/core/orchestrator.py": "import subprocess\nsubprocess.run(['ls'])\n"})
        self.assertViolation(results, "R007")

    def test_aliases_do_not_evade_the_check(self):
        results, _ = self.analyze({
            "wattson_core/core/a.py": "import subprocess as sp\nsp.run(['ls'])\n",
            "wattson_core/core/b.py": "from os import system as s\ns('ls')\n",
            "wattson_core/core/c.py": "from subprocess import run\nrun(['ls'])\n"})
        messages = " ".join(f.message for f in results["R007"].findings)
        self.assertIn("subprocess.run()", messages)
        self.assertIn("os.system()", messages)

    def test_eval_outside_executor_is_flagged(self):
        results, _ = self.analyze({"wattson_core/core/a.py": "eval('1+1')\n"})
        self.assertViolation(results, "R007")

    def test_executor_may_use_subprocess(self):
        results, _ = self.analyze()
        self.assertEqual(results["R007"].status, Status.PASS)

    def test_ai_provider_cannot_execute(self):
        results, _ = self.analyze({
            "wattson_core/ai/providers/echo.py": "import os\nos.system('rm -rf x')\n"})
        self.assertViolation(results, "R007")


class BootRule(ProjectCase):
    def test_unlocked_boot_is_critical(self):
        results, _ = self.analyze({
            "wattson_core/security/boot.py": (
                "BOOT_STATE = {'MODE': 'COMMAND', 'EXECUTION': 'LOCKED', 'DIRECT_COMMAND': 'OFF',\n"
                "              'DEVICE_CONTROL': 'OFF', 'PRIVILEGED_ACTIONS': 'OFF'}\n")})
        result = self.assertViolation(results, "R009", Severity.CRITICAL)
        self.assertIn("MODE", result.findings[0].message)

    def test_missing_key_is_critical(self):
        results, _ = self.analyze({
            "wattson_core/security/boot.py": "BOOT_STATE = {'MODE': 'CHAT_ONLY'}\n"})
        self.assertViolation(results, "R009", Severity.CRITICAL)

    def test_non_literal_boot_state_is_indeterminate(self):
        results, _ = self.analyze({
            "wattson_core/security/boot.py": "BOOT_STATE = load_last_state()\n"})
        result = self.assertViolation(results, "R009")
        self.assertEqual(result.findings[0].confidence, Confidence.INDETERMINADO)

    def test_missing_boot_module_is_skipped_not_failed(self):
        self.analyze({"wattson_core/security/boot.py": None})   # None = não cria o arquivo
        self.assertFalse((self.root / "wattson_core/security/boot.py").exists())
        report = FitnessEngine(self.root).run(only=["R009"])
        self.assertEqual(report.results[0].status, Status.SKIP)


class StructureRules(ProjectCase):
    def test_syntax_error_is_reported_and_does_not_crash(self):
        results, report = self.analyze({"wattson_core/core/broken.py": "def x(:\n"})
        self.assertViolation(results, "R001")
        self.assertGreater(len(report.results), 5)   # as demais regras rodaram

    def test_oversized_entrypoint_and_file(self):
        results, _ = self.analyze({
            "wattson_core/__main__.py": "x = 1\n" * 100,
            "wattson_core/core/big.py": "x = 1\n" * 600})
        result = self.assertViolation(results, "R008", Severity.MEDIUM)
        text = " ".join(f.message for f in result.findings)
        self.assertIn("Ponto de entrada", text)
        self.assertIn("600 linhas", text)

    def test_long_function_is_only_a_warning(self):
        body = "def big():\n" + "    x = 1\n" * 90
        results, _ = self.analyze({"wattson_core/core/f.py": body})
        self.assertEqual(results["R008"].status, Status.WARN)


class ReadOnlyObserver(ProjectCase):
    def _adr0(self, code: str):
        return self.analyze({
            "wattson_core/adr0/__init__.py": "",
            "wattson_core/adr0/x.py": code})

    def test_write_open_is_flagged(self):
        results, _ = self._adr0("open('out.txt', 'w')\n")
        self.assertViolation(results, "R010")

    def test_read_open_is_fine(self):
        results, _ = self._adr0("open('in.txt')\nopen('in.txt', 'rb')\n")
        self.assertEqual(results["R010"].status, Status.PASS)

    def test_path_write_and_unlink_are_flagged(self):
        results, _ = self._adr0("from pathlib import Path\nPath('a').write_text('x')\nPath('a').unlink()\n")
        self.assertEqual(len(results["R010"].findings), 2)

    def test_network_and_subprocess_imports_are_flagged(self):
        results, _ = self._adr0("import socket\nimport subprocess\n")
        self.assertEqual(len(results["R010"].findings), 2)

    def test_webbrowser_open_is_not_mistaken_for_file_write(self):
        results, _ = self._adr0("import webbrowser\nwebbrowser.open('https://x.com/w')\n")
        self.assertEqual(results["R010"].status, Status.PASS)


class EngineBehaviour(ProjectCase):
    def test_a_crashing_rule_does_not_stop_the_diagnosis(self):
        class Boom(Rule):
            id, title, adr = "X001", "Regra quebrada", "teste"

            def check(self, ctx):
                raise RuntimeError("boom")

        self.analyze()
        engine = FitnessEngine(self.root)
        engine.rules.append(Boom())
        report = engine.run(category="architecture")
        by_id = {r.rule_id: r for r in report.results}
        self.assertEqual(by_id["X001"].status, Status.ERROR)
        self.assertIn("INDETERMINADO", by_id["X001"].note)
        self.assertEqual(by_id["R002"].status, Status.PASS)   # as outras seguiram
        self.assertEqual(exit_code(report, Severity.HIGH), 2)

    def test_missing_package_gives_clear_error(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = cli_main([str(self.root)])
        self.assertEqual(code, 2)
        self.assertIn("não encontrado", err.getvalue())

    def test_only_and_skip_filters(self):
        self.analyze()
        engine = FitnessEngine(self.root)
        self.assertEqual([r.rule_id for r in engine.run(only=["r002"]).results], ["R002"])
        ids = [r.rule_id for r in engine.run(skip=["R002"], category="architecture").results]
        self.assertNotIn("R002", ids)

    def test_analysis_never_modifies_the_project(self):
        self.analyze()
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        FitnessEngine(self.root).run()
        after = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)


class Cli(ProjectCase):
    def _run(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = cli_main([str(self.root), *args])
        return code, out.getvalue()

    def test_exit_codes_follow_fail_on(self):
        self.analyze({"wattson_core/core/orchestrator.py": "import subprocess\n"})
        self.assertEqual(self._run("--category", "architecture")[0], 1)
        self.assertEqual(self._run("--category", "architecture", "--fail-on", "critical")[0], 0)
        self.assertEqual(self._run("--category", "architecture", "--fail-on", "never")[0], 0)

    def test_json_output_is_valid_and_structured(self):
        self.analyze({"wattson_core/core/orchestrator.py": "import subprocess\n"})
        code, out = self._run("--format", "json", "--category", "architecture")
        data = json.loads(out)
        self.assertEqual(data["verdict"], "VIOLAÇÕES")
        r007 = next(r for r in data["results"] if r["rule_id"] == "R007")
        self.assertEqual(r007["status"], "FAIL")
        self.assertEqual(r007["findings"][0]["confidence"], "PROVÁVEL")

    def test_text_output_without_emoji(self):
        self.analyze()
        _, out = self._run("--no-emoji", "--category", "architecture")
        self.assertIn("[ OK ]", out)
        self.assertNotIn("🟢", out)


class DogfoodTest(unittest.TestCase):
    """O ADR 0 precisa passar nas próprias regras de arquitetura."""

    def test_adr0_obeys_its_own_architecture_rules(self):
        report = FitnessEngine(PROJECT_ROOT).run(category="architecture")
        failing = [(r.rule_id, r.findings) for r in report.results if r.status == Status.FAIL]
        self.assertEqual(failing, [])
        errors = [r.rule_id for r in report.results if r.status == Status.ERROR]
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
