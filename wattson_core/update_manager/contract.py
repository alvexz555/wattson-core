from dataclasses import dataclass
from enum import Enum


class UpdateStatus(str, Enum):
    AVAILABLE = "available"
    VALIDATED = "validated"
    BACKED_UP = "backed_up"
    APPLIED = "applied"
    VERIFIED = "verified"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


@dataclass(frozen=True)
class UpdateRequest:
    current_version: str
    target_version: str
@dataclass(frozen=True)
class UpdateResult:
    status: UpdateStatus
    current_version: str
    target_version: str
    message: str
