"""Contrato arquitetural do Wattson: os ADRs escritos como dados.

Este é o arquivo que você edita quando a arquitetura muda. As regras em
`rules/` só interpretam o contrato; nenhuma decisão fica escondida no código
delas. Mudou uma decisão? Muda aqui, e o ADR 0 passa a cobrar a nova versão.
"""
from __future__ import annotations

from dataclasses import dataclass, field

ROOT_PACKAGE = "wattson_core"
_P = ROOT_PACKAGE
PROVIDERS = f"{_P}.ai.providers"


@dataclass(frozen=True)
class Forbid:
    """`source` (e submódulos) não pode importar `target` (e submódulos)."""

    source: str
    target: str
    why: str
    adr: str = ""
    exempt: tuple[str, ...] = ()   # fontes isentas (ex.: o próprio alvo)


@dataclass(frozen=True)
class OnlyAllow:
    """`source` só pode importar (internamente) o que estiver em `allowed`."""

    source: str
    allowed: tuple[str, ...]
    why: str
    adr: str = ""


@dataclass(frozen=True)
class SiblingIsolation:
    """Filhos diretos de `parent` não podem importar uns aos outros."""

    parent: str
    why: str
    adr: str = ""


@dataclass(frozen=True)
class Contract:
    root_package: str = ROOT_PACKAGE
    exclude_dirs: tuple[str, ...] = ("__pycache__", ".venv", "venv", "node_modules", ".git")

    # --- fronteiras entre componentes -------------------------------------
    forbid: tuple[Forbid, ...] = ()
    only_allow: tuple[OnlyAllow, ...] = ()
    siblings: tuple[SiblingIsolation, ...] = ()

    # --- dependências externas --------------------------------------------
    # zona -> raízes permitidas; ("*",) libera tudo. Fora daqui: só stdlib.
    third_party: dict[str, tuple[str, ...]] = field(default_factory=dict)
    # zonas cujas dependências externas são opcionais (falta = degradação)
    optional_zones: tuple[str, ...] = ()

    # --- importação dinâmica e execução -----------------------------------
    dynamic_import_allowed: tuple[str, ...] = ()
    dynamic_import_calls: tuple[str, ...] = ()
    exec_allowed: tuple[str, ...] = ()
    exec_modules: tuple[str, ...] = ()
    exec_calls: tuple[str, ...] = ()

    # --- o ADR 0 observa e diagnostica, não controla ----------------------
    readonly_zone: str = ""
    readonly_forbidden_imports: tuple[str, ...] = ()
    readonly_write_calls: tuple[str, ...] = ()

    # --- anti God Script ---------------------------------------------------
    max_file_lines: int = 500
    max_function_lines: int = 80
    entrypoint_names: tuple[str, ...] = ("main.py", "__main__.py")
    entrypoint_max_lines: int = 60

    # --- boot seguro (ADR 6) ----------------------------------------------
    boot_module: str = ""
    boot_required: dict[str, str] = field(default_factory=dict)

    # --- limites de saúde --------------------------------------------------
    disk_min_free_ratio: float = 0.10
    memory_min_available_ratio: float = 0.10
    load_max_per_cpu: float = 1.5

    def watched_calls(self) -> tuple[str, ...]:
        """Padrões de chamada que o scanner precisa registrar."""
        return tuple(dict.fromkeys(
            self.exec_calls
            + self.dynamic_import_calls
            + self.readonly_write_calls
            + ("open", "io.open", ".open")
        ))


CONTRACT = Contract(
    forbid=(
        Forbid(
            _P, PROVIDERS,
            "Nenhum componente depende estaticamente de um provider de IA. "
            "Providers são carregados pelo registry e podem falhar sem afetar o Wattson.",
            "ADR-1 §3.1", exempt=(PROVIDERS,),
        ),
        Forbid(
            _P, f"{_P}.adr0",
            "O ADR 0 observa o sistema; nenhum componente pode depender dele.",
            "ADR-0", exempt=(f"{_P}.adr0",),
        ),
        Forbid(
            f"{_P}.core", f"{_P}.ai.registry",
            "O Core recebe o AIProvider por injeção (ai.interface). "
            "Quem carrega providers é o ponto de composição, não o Core.",
            "ADR-1 §3.1",
        ),
        Forbid(
            f"{_P}.ai.interface", f"{_P}.ai.registry",
            "A interface é um contrato; não conhece quem carrega implementações.",
            "ADR-1 §3.1",
        ),
        Forbid(
            PROVIDERS, f"{_P}.ai.registry",
            "Um provider não conhece quem o carrega.",
            "ADR-1 §3.1",
        ),
        Forbid(
            f"{_P}.executor", f"{_P}.ai",
            "O Executor não depende de IA: executa somente o que foi autorizado.",
            "ADR-2 / ADR-6",
        ),
        Forbid(
            f"{_P}.security", f"{_P}.ai",
            "A camada de autorização não pode depender de IA.",
            "ADR-6",
        ),
    ),
    only_allow=(
        OnlyAllow(
            f"{_P}.ai", (f"{_P}.ai",),
            "O módulo de IA fornece raciocínio, classificação e seleção de ferramentas. "
            "O fluxo de controle (Core, Security, Executor) pertence ao Wattson.",
            "ADR-1 / ADR-2",
        ),
        OnlyAllow(
            f"{_P}.adr0", (f"{_P}.adr0",),
            "O ADR 0 precisa continuar funcionando quando o resto do sistema estiver quebrado.",
            "ADR-0",
        ),
    ),
    siblings=(
        SiblingIsolation(
            PROVIDERS,
            "Cada provider é isolado: a falha de um não pode afetar outro. "
            "Código compartilhado pertence a ai.interface.",
            "ADR-1 §3.1",
        ),
    ),
    third_party={PROVIDERS: ("*",)},
    optional_zones=(PROVIDERS,),
    dynamic_import_allowed=(f"{_P}.ai.registry",),
    dynamic_import_calls=("importlib.import_module", "importlib.__import__", "__import__"),
    exec_allowed=(f"{_P}.executor",),
    exec_modules=("subprocess", "pty", "pexpect"),
    exec_calls=(
        "subprocess.*", "os.system", "os.popen", "os.exec*", "os.spawn*",
        "os.posix_spawn*", "pty.spawn", "eval", "exec",
    ),
    readonly_zone=f"{_P}.adr0",
    readonly_forbidden_imports=(
        "subprocess", "socket", "ssl", "http", "urllib", "ftplib", "smtplib",
        "telnetlib", "pty", "ctypes", "requests",
    ),
    readonly_write_calls=(
        "os.remove", "os.unlink", "os.rename", "os.replace", "os.mkdir", "os.makedirs",
        "os.rmdir", "os.removedirs", "os.chmod", "os.chown", "os.truncate",
        "shutil.rmtree", "shutil.move", "shutil.copy", "shutil.copy2",
        "shutil.copyfile", "shutil.copytree",
        ".write_text", ".write_bytes", ".unlink", ".rmdir", ".mkdir", ".touch", ".rename",
    ),
    boot_module=f"{_P}.security.boot",
    boot_required={
        "MODE": "CHAT_ONLY",
        "EXECUTION": "LOCKED",
        "DIRECT_COMMAND": "OFF",
        "DEVICE_CONTROL": "OFF",
        "PRIVILEGED_ACTIONS": "OFF",
    },
)
