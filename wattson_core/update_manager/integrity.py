import hashlib
from pathlib import Path


def calculate_file_hash(path: Path) -> str:
    hasher = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def verify_file_hash(path: Path, expected_hash: str) -> bool:
    return calculate_file_hash(path) == expected_hash
