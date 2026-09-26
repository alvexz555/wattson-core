from .version import Version


class UpdateManager:
    def is_update_available(self, current: Version, target: Version) -> bool:
        return target > current

    def get_target_version(self, manifest) -> str:
        return manifest.version

    def get_manifest_files(self, manifest) -> dict[str, str]:
        return manifest.files

    def validate_manifest(self, manifest) -> bool:
        manifest.validate()
        return True

    def download_package(self, source: str, destination: str) -> None:
        from pathlib import Path
        import shutil

        destination_path = Path(destination)
        destination_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(source, destination_path)

    def verify_package_integrity(self, package_path: str, expected_hash: str) -> bool:
        from pathlib import Path
        from .integrity import verify_file_hash

        return verify_file_hash(Path(package_path), expected_hash)
    def create_backup(self, source_path: str, backup_path: str) -> None:
        from pathlib import Path
        import shutil

        source = Path(source_path)
        backup = Path(backup_path)

        if not source.exists():
            raise FileNotFoundError(source)

        backup.parent.mkdir(parents=True, exist_ok=True)

        if backup.exists():
            shutil.rmtree(backup)

        shutil.copytree(source, backup)
    def apply_update(self, update_path: str, current_path: str) -> None:
        from pathlib import Path
        import shutil

        update = Path(update_path)
        current = Path(current_path)

        if not update.exists():
            raise FileNotFoundError(update)

        current.mkdir(parents=True, exist_ok=True)

        for item in update.iterdir():
            destination = current / item.name

            if item.is_dir():
                if destination.exists():
                    shutil.rmtree(destination)

                shutil.copytree(item, destination)
            else:
                shutil.copy2(item, destination)
    def verify_applied_file(
        self,
        file_path: str,
        expected_hash: str,
    ) -> bool:
        from pathlib import Path
        from .integrity import verify_file_hash

        path = Path(file_path)

        if not path.exists():
            return False

        if not path.is_file():
            return False

        return verify_file_hash(
            path,
            expected_hash,
        )
    def verify_applied_files(
        self,
        files: dict[str, str],
        base_path: str,
    ) -> bool:
        from pathlib import Path

        base = Path(base_path)

        for file_path, expected_hash in files.items():
            path = base / file_path

            if not self.verify_applied_file(
                str(path),
                expected_hash,
            ):
                return False

        return True
    def rollback_update(
        self,
        backup_path: str,
        current_path: str,
    ) -> None:
        from pathlib import Path
        import shutil

        backup = Path(backup_path)
        current = Path(current_path)

        if not backup.exists():
            raise FileNotFoundError(backup)

        if current.exists():
            shutil.rmtree(current)

        shutil.copytree(backup, current)
    def verify_and_rollback_if_needed(
        self,
        file_path: str,
        expected_hash: str,
        backup_path: str,
        current_path: str,
    ) -> bool:
        if self.verify_applied_file(
            file_path,
            expected_hash,
        ):
            return True

        self.rollback_update(
            backup_path,
            current_path,
        )

        return False
    def run_update_cycle(
        self,
        current_version: Version,
        target_version: Version,
        manifest,
        package_path: str,
        current_path: str,
        backup_path: str,
    ) -> bool:
        if not self.is_update_available(
            current_version,
            target_version,
        ):
            return False

        self.validate_manifest(manifest)

        self.create_backup(
            current_path,
            backup_path,
        )

        self.apply_update(
            package_path,
            current_path,
        )

        verified = self.verify_applied_files(
            self.get_manifest_files(manifest),
            current_path,
        )

        if verified:
            return True

        self.rollback_update(
            backup_path,
            current_path,
        )

        return False
