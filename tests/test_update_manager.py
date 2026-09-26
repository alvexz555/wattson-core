from wattson_core.update_manager.contract import (
    UpdateRequest,
    UpdateResult,
    UpdateStatus,
)
from wattson_core.update_manager.version import Version
from wattson_core.update_manager.manager import UpdateManager
from wattson_core.update_manager.manifest import Manifest
from wattson_core.update_manager.integrity import (
    calculate_file_hash,
    verify_file_hash,
)


def test_update_request_stores_versions():
    request = UpdateRequest(
        current_version="0.1.0",
        target_version="0.2.0",
    )

    assert request.current_version == "0.1.0"
    assert request.target_version == "0.2.0"


def test_update_result_stores_update_state():
    result = UpdateResult(
        status=UpdateStatus.VERIFIED,
        current_version="0.1.0",
        target_version="0.2.0",
        message="Update verified successfully.",
    )

    assert result.status is UpdateStatus.VERIFIED
    assert result.current_version == "0.1.0"
    assert result.target_version == "0.2.0"
    assert result.message == "Update verified successfully."


def test_update_status_is_string_compatible():
    assert UpdateStatus.AVAILABLE == "available"
    assert UpdateStatus.ROLLED_BACK == "rolled_back"


def test_version_parses_semver():
    version = Version.parse("1.2.3")

    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3


def test_version_detects_newer_version():
    current = Version.parse("1.2.3")
    target = Version.parse("1.3.0")

    assert target > current
    assert not current > target


def test_version_rejects_invalid_semver():
    try:
        Version.parse("1.2")
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid SemVer should raise ValueError")


def test_manifest_stores_version():
    manifest = Manifest(version="0.1.0")

    assert manifest.version == "0.1.0"


def test_manifest_is_immutable():
    manifest = Manifest(version="0.1.0")

    try:
        manifest.version = "0.2.0"
    except AttributeError:
        pass
    else:
        raise AssertionError("Manifest must be immutable")


def test_manifest_has_format_version():
    manifest = Manifest(
        version="0.1.0",
        format_version=1,
    )

    assert manifest.format_version == 1


def test_manifest_stores_files():
    manifest = Manifest(
        version="0.1.0",
        files={
            "wattson_core/update_manager/manifest.py": "abc123",
            "wattson_core/update_manager/version.py": "def456",
        },
    )

    assert manifest.files["wattson_core/update_manager/manifest.py"] == "abc123"
    assert manifest.files["wattson_core/update_manager/version.py"] == "def456"


def test_calculate_file_hash(tmp_path):
    test_file = tmp_path / "example.txt"
    test_file.write_text("Wattson")

    file_hash = calculate_file_hash(test_file)

    assert len(file_hash) == 64
    assert all(character in "0123456789abcdef" for character in file_hash)


def test_verify_file_hash(tmp_path):
    test_file = tmp_path / "verify.txt"
    test_file.write_text("Wattson")

    expected_hash = calculate_file_hash(test_file)

    assert verify_file_hash(test_file, expected_hash)
    assert not verify_file_hash(test_file, "0" * 64)
from wattson_core.update_manager.version import CURRENT_VERSION


def test_current_version_exists():
    assert CURRENT_VERSION == "0.1.0"
def test_manifest_rejects_invalid_file_hash():
    try:
        Manifest(
            version="0.1.0",
            files={
                "wattson_core/update_manager/version.py": "invalid-hash",
            },
        ).validate()
    except ValueError:
        pass
    else:
        raise AssertionError("Manifest must reject invalid file hashes")
def test_manifest_rejects_non_hex_file_hash():
    try:
        Manifest(
            version="0.1.0",
            files={
                "wattson_core/update_manager/version.py": "g" * 64,
            },
        ).validate()
    except ValueError:
        pass
    else:
        raise AssertionError("Manifest must reject non-hex file hashes")
def test_manifest_accepts_valid_file_hash():
    Manifest(
        version="0.1.0",
        files={
            "wattson_core/update_manager/version.py": "a" * 64,
        },
    ).validate()
def test_manifest_accepts_empty_files():
    Manifest(
        version="0.1.0",
        files={},
    ).validate()
def test_manifest_rejects_empty_file_path():
    try:
        Manifest(
            version="0.1.0",
            files={
                "": "a" * 64,
            },
        ).validate()
    except ValueError:
        pass
    else:
        raise AssertionError("Manifest must reject empty file paths")
def test_manifest_rejects_whitespace_file_path():
    try:
        Manifest(
            version="0.1.0",
            files={
                "   ": "a" * 64,
            },
        ).validate()
    except ValueError:
        pass
    else:
        raise AssertionError("Manifest must reject whitespace file paths")
def test_manifest_rejects_empty_file_hash():
    try:
        Manifest(
            version="0.1.0",
            files={
                "wattson_core/update_manager/version.py": "",
            },
        ).validate()
    except ValueError:
        pass
    else:
        raise AssertionError("Manifest must reject empty file hashes")
def test_manifest_rejects_non_string_file_path():
    try:
        Manifest(
            version="0.1.0",
            files={
                123: "a" * 64,
            },
        ).validate()
    except (ValueError, TypeError):
        pass
    else:
        raise AssertionError("Manifest must reject non-string file paths")
def test_manifest_rejects_non_string_file_hash():
    try:
        Manifest(
            version="0.1.0",
            files={
                "wattson_core/update_manager/version.py": 123,
            },
        ).validate()
    except (ValueError, TypeError):
        pass
    else:
        raise AssertionError("Manifest must reject non-string file hashes")
def test_version_detects_update_available():
    current = Version(0, 1, 0)
    target = Version(0, 2, 0)

    assert target > current
def test_update_manager_detects_update_available():
    current = Version(0, 1, 0)
    target = Version(0, 2, 0)

    assert target > current
def test_update_manager_reports_update_available():
    manager = UpdateManager()

    assert manager.is_update_available(
        Version(0, 1, 0),
        Version(0, 2, 0),
    ) is True
def test_update_manager_reports_no_update_for_older_version():
    manager = UpdateManager()

    assert manager.is_update_available(
        Version(0, 2, 0),
        Version(0, 1, 0),
    ) is False
def test_update_manager_reports_no_update_for_same_version():
    manager = UpdateManager()

    assert manager.is_update_available(
        Version(0, 2, 0),
        Version(0, 2, 0),
    ) is False
def test_update_manager_reads_target_version_from_manifest():
    manager = UpdateManager()

    manifest = Manifest(
        version="0.2.0",
        files={},
    )

    assert manager.get_target_version(manifest) == "0.2.0"
def test_update_manager_reads_files_from_manifest():
    manager = UpdateManager()

    manifest = Manifest(
        version="0.2.0",
        files={
            "wattson_core/update_manager/version.py": "a" * 64,
        },
    )

    assert manager.get_manifest_files(manifest) == {
        "wattson_core/update_manager/version.py": "a" * 64,
    }
def test_update_manager_validates_manifest():
    manager = UpdateManager()

    manifest = Manifest(
        version="0.2.0",
        files={
            "wattson_core/update_manager/version.py": "a" * 64,
        },
    )

    assert manager.validate_manifest(manifest) is True
def test_update_manager_rejects_invalid_manifest():
    manager = UpdateManager()

    manifest = Manifest(
        version="0.2.0",
        files={
            "wattson_core/update_manager/version.py": "invalid-hash",
        },
    )

    try:
        manager.validate_manifest(manifest)
    except ValueError:
        pass
    else:
        raise AssertionError("UpdateManager must reject invalid manifests")
def test_update_manager_downloads_package(tmp_path):
    manager = UpdateManager()

    package_source = tmp_path / "update.zip"
    package_source.write_bytes(b"fake update package")

    package_destination = tmp_path / "downloads" / "update.zip"

    manager.download_package(
        str(package_source),
        str(package_destination),
    )

    assert package_destination.exists()
def test_update_manager_rejects_missing_package_source(tmp_path):
    manager = UpdateManager()

    package_source = tmp_path / "missing.zip"
    package_destination = tmp_path / "downloads" / "update.zip"

    try:
        manager.download_package(
            str(package_source),
            str(package_destination),
        )
    except FileNotFoundError:
        pass
    else:
        raise AssertionError(
            "UpdateManager must reject a missing package source"
        )
def test_update_manager_downloads_package_with_same_content(tmp_path):
    manager = UpdateManager()

    package_source = tmp_path / "update.zip"
    package_content = b"fake update package content"
    package_source.write_bytes(package_content)

    package_destination = tmp_path / "downloads" / "update.zip"

    manager.download_package(
        str(package_source),
        str(package_destination),
    )

    assert package_destination.read_bytes() == package_content
def test_update_manager_verifies_package_integrity(tmp_path):
    manager = UpdateManager()

    package = tmp_path / "update.zip"
    package_content = b"package content"
    package.write_bytes(package_content)

    from wattson_core.update_manager.integrity import calculate_file_hash

    expected_hash = calculate_file_hash(package)

    assert manager.verify_package_integrity(
        str(package),
        expected_hash,
    ) is True

def test_update_manager_rejects_invalid_package_integrity(tmp_path):
    manager = UpdateManager()

    package = tmp_path / "update.zip"
    package.write_bytes(b"package content")

    invalid_hash = "b" * 64

    assert manager.verify_package_integrity(
        str(package),
        invalid_hash,
    ) is False
def test_update_manager_creates_backup(tmp_path):
    manager = UpdateManager()

    source = tmp_path / "current"
    source.mkdir()

    file = source / "wattson.txt"
    file.write_text("current version")

    backup = tmp_path / "backup"

    manager.create_backup(
        str(source),
        str(backup),
    )

    assert (backup / "wattson.txt").exists()
def test_update_manager_rejects_missing_backup_source(tmp_path):
    manager = UpdateManager()

    source = tmp_path / "missing"
    backup = tmp_path / "backup"

    try:
        manager.create_backup(
            str(source),
            str(backup),
        )
    except FileNotFoundError:
        pass
    else:
        raise AssertionError(
            "UpdateManager must reject a missing backup source"
        )
def test_update_manager_replaces_existing_backup(tmp_path):
    manager = UpdateManager()

    source = tmp_path / "current"
    source.mkdir()

    current_file = source / "wattson.txt"
    current_file.write_text("current version")

    backup = tmp_path / "backup"
    backup.mkdir()

    old_file = backup / "old.txt"
    old_file.write_text("old backup")

    manager.create_backup(
        str(source),
        str(backup),
    )

    assert (backup / "wattson.txt").read_text() == "current version"
    assert not (backup / "old.txt").exists()
def test_update_manager_applies_update(tmp_path):
    manager = UpdateManager()

    current = tmp_path / "current"
    current.mkdir()

    current_file = current / "wattson.txt"
    current_file.write_text("old version")

    update = tmp_path / "update"
    update.mkdir()

    update_file = update / "wattson.txt"
    update_file.write_text("new version")

    manager.apply_update(
        str(update),
        str(current),
    )

    assert current_file.read_text() == "new version"
def test_update_manager_rejects_missing_update_source(tmp_path):
    manager = UpdateManager()

    update = tmp_path / "missing"
    current = tmp_path / "current"

    try:
        manager.apply_update(
            str(update),
            str(current),
        )
    except FileNotFoundError:
        pass
    else:
        raise AssertionError(
            "UpdateManager must reject a missing update source"
        )
def test_update_manager_applies_new_file(tmp_path):
    manager = UpdateManager()

    current = tmp_path / "current"
    current.mkdir()

    update = tmp_path / "update"
    update.mkdir()

    new_file = update / "new_feature.txt"
    new_file.write_text("new feature")

    manager.apply_update(
        str(update),
        str(current),
    )

    assert (current / "new_feature.txt").read_text() == "new feature"
def test_update_manager_applies_nested_directory(tmp_path):
    manager = UpdateManager()

    current = tmp_path / "current"
    current.mkdir()

    update = tmp_path / "update"
    update.mkdir()

    nested = update / "wattson_core" / "module"
    nested.mkdir(parents=True)

    nested_file = nested / "feature.py"
    nested_file.write_text("new feature")

    manager.apply_update(
        str(update),
        str(current),
    )

    assert (
        current / "wattson_core" / "module" / "feature.py"
    ).read_text() == "new feature"
def test_update_manager_replaces_existing_nested_directory(tmp_path):
    manager = UpdateManager()

    current = tmp_path / "current"
    current.mkdir()

    current_nested = current / "wattson_core" / "module"
    current_nested.mkdir(parents=True)

    (current_nested / "old.py").write_text("old code")

    update = tmp_path / "update"
    update.mkdir()

    update_nested = update / "wattson_core" / "module"
    update_nested.mkdir(parents=True)

    (update_nested / "new.py").write_text("new code")

    manager.apply_update(
        str(update),
        str(current),
    )

    assert (
        current / "wattson_core" / "module" / "new.py"
    ).read_text() == "new code"

    assert not (
        current / "wattson_core" / "module" / "old.py"
    ).exists()
def test_update_manager_verifies_applied_file(tmp_path):
    manager = UpdateManager()

    current = tmp_path / "current"
    current.mkdir()

    file = current / "wattson.txt"
    file.write_text("new version")

    expected_hash = __import__("hashlib").sha256(
        b"new version"
    ).hexdigest()

    assert manager.verify_applied_file(
        str(file),
        expected_hash,
    ) is True
def test_update_manager_rejects_modified_applied_file(tmp_path):
    manager = UpdateManager()

    current = tmp_path / "current"
    current.mkdir()

    file = current / "wattson.txt"
    file.write_text("tampered version")

    expected_hash = __import__("hashlib").sha256(
        b"new version"
    ).hexdigest()

    assert manager.verify_applied_file(
        str(file),
        expected_hash,
    ) is False
def test_update_manager_rejects_missing_applied_file(tmp_path):
    manager = UpdateManager()

    current = tmp_path / "current"
    current.mkdir()

    expected_hash = __import__("hashlib").sha256(
        b"new version"
    ).hexdigest()

    missing_file = current / "wattson.txt"

    assert manager.verify_applied_file(
        str(missing_file),
        expected_hash,
    ) is False
def test_update_manager_rejects_directory_as_applied_file(tmp_path):
    manager = UpdateManager()

    current = tmp_path / "current"
    current.mkdir()

    directory = current / "wattson_core"
    directory.mkdir()

    expected_hash = __import__("hashlib").sha256(
        b"new version"
    ).hexdigest()

    assert manager.verify_applied_file(
        str(directory),
        expected_hash,
    ) is False
def test_update_manager_verifies_all_applied_files():
    from pathlib import Path
    from wattson_core.update_manager.manager import UpdateManager
    from wattson_core.update_manager.integrity import calculate_file_hash

    current_path = Path("tests/tmp_verify_all")
    current_path.mkdir(parents=True, exist_ok=True)

    file_a = current_path / "file_a.txt"
    file_b = current_path / "file_b.txt"

    file_a.write_text("conteudo A")
    file_b.write_text("conteudo B")

    files = {
        "file_a.txt": calculate_file_hash(file_a),
        "file_b.txt": calculate_file_hash(file_b),
    }

    manager = UpdateManager()

    assert manager.verify_applied_files(
        files,
        str(current_path),
    ) is True
def test_update_manager_rejects_modified_file_in_applied_files():
    from pathlib import Path
    from wattson_core.update_manager.manager import UpdateManager
    from wattson_core.update_manager.integrity import calculate_file_hash

    current_path = Path("tests/tmp_verify_all_modified")
    current_path.mkdir(parents=True, exist_ok=True)

    file_a = current_path / "file_a.txt"
    file_b = current_path / "file_b.txt"

    file_a.write_text("conteudo A")
    file_b.write_text("conteudo B")

    files = {
        "file_a.txt": calculate_file_hash(file_a),
        "file_b.txt": calculate_file_hash(file_b),
    }

    file_b.write_text("conteudo B MODIFICADO")

    manager = UpdateManager()

    assert manager.verify_applied_files(
        files,
        str(current_path),
    ) is False
def test_update_manager_applies_and_verifies_update():
    from pathlib import Path
    from wattson_core.update_manager.manager import UpdateManager
    from wattson_core.update_manager.integrity import calculate_file_hash

    update_path = Path("tests/tmp_update_verify_source")
    current_path = Path("tests/tmp_update_verify_current")

    update_path.mkdir(parents=True, exist_ok=True)
    current_path.mkdir(parents=True, exist_ok=True)

    file_a = update_path / "file_a.txt"
    file_b = update_path / "file_b.txt"

    file_a.write_text("novo conteudo A")
    file_b.write_text("novo conteudo B")

    files = {
        "file_a.txt": calculate_file_hash(file_a),
        "file_b.txt": calculate_file_hash(file_b),
    }

    manager = UpdateManager()

    manager.apply_update(
        str(update_path),
        str(current_path),
    )

    assert manager.verify_applied_files(
        files,
        str(current_path),
    ) is True
def test_update_manager_rolls_back_from_backup():
    from pathlib import Path
    from wattson_core.update_manager.manager import UpdateManager

    backup_path = Path("tests/tmp_rollback_backup")
    current_path = Path("tests/tmp_rollback_current")

    backup_path.mkdir(parents=True, exist_ok=True)
    current_path.mkdir(parents=True, exist_ok=True)

    backup_file = backup_path / "config.txt"
    current_file = current_path / "config.txt"

    backup_file.write_text("versao anterior")
    current_file.write_text("versao nova")

    manager = UpdateManager()

    manager.rollback_update(
        str(backup_path),
        str(current_path),
    )

    assert current_file.read_text() == "versao anterior"
def test_update_manager_rejects_missing_rollback_backup():
    from pathlib import Path
    from wattson_core.update_manager.manager import UpdateManager

    backup_path = Path("tests/tmp_missing_rollback_backup")
    current_path = Path("tests/tmp_rollback_missing_current")

    current_path.mkdir(parents=True, exist_ok=True)
    (current_path / "config.txt").write_text("versao nova")

    manager = UpdateManager()

    try:
        manager.rollback_update(
            str(backup_path),
            str(current_path),
        )
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass
def test_update_manager_rejects_file_as_rollback_backup():
    from pathlib import Path
    from wattson_core.update_manager.manager import UpdateManager

    backup_path = Path("tests/tmp_invalid_rollback_backup")
    current_path = Path("tests/tmp_rollback_invalid_current")

    current_path.mkdir(parents=True, exist_ok=True)
    backup_path.write_text("backup invalido")

    (current_path / "config.txt").write_text("versao nova")

    manager = UpdateManager()

    try:
        manager.rollback_update(
            str(backup_path),
            str(current_path),
        )
        assert False, "Expected NotADirectoryError"
    except NotADirectoryError:
        pass
def test_update_manager_rollback_removes_files_created_by_update():
    from pathlib import Path
    from wattson_core.update_manager.manager import UpdateManager

    backup_path = Path("tests/tmp_rollback_new_file_backup")
    current_path = Path("tests/tmp_rollback_new_file_current")

    backup_path.mkdir(parents=True, exist_ok=True)
    current_path.mkdir(parents=True, exist_ok=True)

    (backup_path / "config.txt").write_text("versao anterior")

    (current_path / "config.txt").write_text("versao nova")
    (current_path / "novo_recurso.txt").write_text("arquivo criado pelo update")

    manager = UpdateManager()

    manager.rollback_update(
        str(backup_path),
        str(current_path),
    )

    assert (current_path / "config.txt").read_text() == "versao anterior"
    assert not (current_path / "novo_recurso.txt").exists()
def test_update_manager_rollback_restores_nested_directory(tmp_path):
    from wattson_core.update_manager.manager import UpdateManager

    backup_path = tmp_path / "rollback_nested_backup"
    current_path = tmp_path / "rollback_nested_current"

    backup_path.mkdir(parents=True, exist_ok=True)
    current_path.mkdir(parents=True, exist_ok=True)

    backup_nested = backup_path / "config"
    current_nested = current_path / "config"

    backup_nested.mkdir()
    current_nested.mkdir()

    (backup_nested / "settings.txt").write_text("configuracao anterior")
    (current_nested / "settings.txt").write_text("configuracao nova")
    (current_nested / "new.txt").write_text("arquivo novo")

    manager = UpdateManager()

    manager.rollback_update(
        str(backup_path),
        str(current_path),
    )

    assert (
        current_nested / "settings.txt"
    ).read_text() == "configuracao anterior"

    assert not (current_nested / "new.txt").exists()
def test_update_manager_rolls_back_when_verification_fails(tmp_path):
    from wattson_core.update_manager.manager import UpdateManager
    from wattson_core.update_manager.integrity import calculate_file_hash

    backup_path = tmp_path / "backup"
    current_path = tmp_path / "current"
    update_path = tmp_path / "update"

    backup_path.mkdir()
    current_path.mkdir()
    update_path.mkdir()

    (backup_path / "config.txt").write_text("versao anterior")
    (current_path / "config.txt").write_text("versao atual")
    (update_path / "config.txt").write_text("versao nova")
    (update_path / "novo.txt").write_text("arquivo novo")

    expected_hash = calculate_file_hash(
        current_path / "config.txt"
    )

    manager = UpdateManager()

    manager.create_backup(
        str(current_path),
        str(backup_path),
    )

    manager.apply_update(
        str(update_path),
        str(current_path),
    )

    verification_result = manager.verify_applied_file(
        str(current_path / "config.txt"),
        expected_hash,
    )

    assert verification_result is False

    manager.rollback_update(
        str(backup_path),
        str(current_path),
    )

    assert (
        current_path / "config.txt"
    ).read_text() == "versao atual"

    assert not (current_path / "novo.txt").exists()
def test_update_manager_automatically_rolls_back_when_verification_fails(
    tmp_path,
):
    from wattson_core.update_manager.manager import UpdateManager
    from wattson_core.update_manager.integrity import calculate_file_hash

    backup_path = tmp_path / "backup"
    current_path = tmp_path / "current"
    update_path = tmp_path / "update"

    backup_path.mkdir()
    current_path.mkdir()
    update_path.mkdir()

    (current_path / "config.txt").write_text("versao atual")
    (update_path / "config.txt").write_text("versao nova")
    (update_path / "novo.txt").write_text("arquivo novo")

    expected_hash = calculate_file_hash(
        current_path / "config.txt"
    )

    manager = UpdateManager()

    manager.create_backup(
        str(current_path),
        str(backup_path),
    )

    manager.apply_update(
        str(update_path),
        str(current_path),
    )

    result = manager.verify_and_rollback_if_needed(
        str(current_path / "config.txt"),
        expected_hash,
        str(backup_path),
        str(current_path),
    )

    assert result is False

    assert (
        current_path / "config.txt"
    ).read_text() == "versao atual"

    assert not (current_path / "novo.txt").exists()
def test_update_manager_runs_complete_update_cycle(tmp_path):
    from wattson_core.update_manager.manager import UpdateManager
    from wattson_core.update_manager.integrity import calculate_file_hash
    from wattson_core.update_manager.manifest import Manifest
    from wattson_core.update_manager.version import Version

    source_path = tmp_path / "source"
    package_path = tmp_path / "package"
    current_path = tmp_path / "current"
    backup_path = tmp_path / "backup"

    source_path.mkdir()
    package_path.mkdir()
    current_path.mkdir()

    (source_path / "config.txt").write_text("versao nova")

    package_file = package_path / "config.txt"
    package_file.write_text("versao nova")

    expected_hash = calculate_file_hash(package_file)

    manifest = Manifest(
        version="0.2.0",
        files={
            "config.txt": expected_hash,
        },
    )

    manager = UpdateManager()

    result = manager.run_update_cycle(
        current_version=Version(0, 1, 0),
        target_version=Version(0, 2, 0),
        manifest=manifest,
        package_path=str(package_path),
        current_path=str(current_path),
        backup_path=str(backup_path),
    )

    assert result is True

    assert (
        current_path / "config.txt"
    ).read_text() == "versao nova"

    assert backup_path.exists()
def test_update_manager_full_cycle_rolls_back_on_verification_failure(
    tmp_path,
):
    from wattson_core.update_manager.manager import UpdateManager
    from wattson_core.update_manager.integrity import calculate_file_hash
    from wattson_core.update_manager.manifest import Manifest
    from wattson_core.update_manager.version import Version

    package_path = tmp_path / "package"
    current_path = tmp_path / "current"
    backup_path = tmp_path / "backup"

    package_path.mkdir()
    current_path.mkdir()

    (current_path / "config.txt").write_text("versao anterior")
    (package_path / "config.txt").write_text("versao nova")
    (package_path / "novo.txt").write_text("arquivo novo")

    wrong_hash = calculate_file_hash(
        current_path / "config.txt"
    )

    manifest = Manifest(
        version="0.2.0",
        files={
            "config.txt": wrong_hash,
        },
    )

    manager = UpdateManager()

    result = manager.run_update_cycle(
        current_version=Version(0, 1, 0),
        target_version=Version(0, 2, 0),
        manifest=manifest,
        package_path=str(package_path),
        current_path=str(current_path),
        backup_path=str(backup_path),
    )

    assert result is False

    assert (
        current_path / "config.txt"
    ).read_text() == "versao anterior"

    assert not (current_path / "novo.txt").exists()
