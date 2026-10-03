from dataclasses import dataclass
import subprocess


@dataclass(frozen=True)
class GitUpdateInfo:
    current_commit: str
    target_commit: str
    update_available: bool


class GitUpdateChecker:
    def __init__(self, repository_path: str = "."):
        self.repository_path = repository_path

    def _run_git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=self.repository_path,
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout.strip()

    def fetch(self) -> None:
        self._run_git("fetch", "--quiet")

    def current_commit(self) -> str:
        return self._run_git("rev-parse", "HEAD")

    def target_commit(self) -> str:
        branch = self._run_git(
            "rev-parse",
            "--abbrev-ref",
            "HEAD",
        )

        return self._run_git(
            "rev-parse",
            f"origin/{branch}",
        )

    def update_available(self) -> bool:
        return self.current_commit() != self.target_commit()

    def get_update_info(self) -> GitUpdateInfo:
        current = self.current_commit()
        target = self.target_commit()

        return GitUpdateInfo(
            current_commit=current,
            target_commit=target,
            update_available=current != target,
        )
