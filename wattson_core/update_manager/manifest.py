from dataclasses import dataclass, field


@dataclass(frozen=True)
class Manifest:
    version: str
    format_version: int = 1
    files: dict[str, str] = field(default_factory=dict)

    def validate(self):
        for file_path, file_hash in self.files.items():
            if not isinstance(file_path, str) or not file_path.strip():
                raise ValueError("Invalid file path")

            if not isinstance(file_hash, str) or len(file_hash) != 64:
                raise ValueError("Invalid file hash")

            try:
                int(file_hash, 16)
            except ValueError:
                raise ValueError("Invalid file hash")
