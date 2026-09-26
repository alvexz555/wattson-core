from dataclasses import dataclass
import re

CURRENT_VERSION = "0.1.0"

@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, value: str) -> "Version":
        match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", value)

        if not match:
            raise ValueError(f"Invalid SemVer: {value}")

        major, minor, patch = map(int, match.groups())

        return cls(
            major=major,
            minor=minor,
            patch=patch,
        )
