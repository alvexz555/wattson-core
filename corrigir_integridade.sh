#!/bin/bash

set -e

MANAGER="wattson_core/update_manager/manager.py"

python - <<'PY'
from pathlib import Path

path = Path("wattson_core/update_manager/manager.py")
text = path.read_text()

method = '''    def verify_package_integrity(self, package_path: str, expected_hash: str) -> bool:
        from .integrity import verify_file_hash

        return verify_file_hash(package_path, expected_hash)
'''

# Remove todas as cópias atuais do método
lines = text.splitlines()
result = []
i = 0

while i < len(lines):
    if lines[i].lstrip().startswith("def verify_package_integrity("):
        i += 1

        while i < len(lines):
            stripped = lines[i].strip()

            if stripped.startswith("def ") or stripped.startswith("@"):
                break

            i += 1

        continue

    result.append(lines[i])
    i += 1

text = "\n".join(result).rstrip() + "\n"

# Adiciona uma única versão correta no final da classe
text += "\n" + method

path.write_text(text)

print("OK: verify_package_integrity corrigido.")
PY

echo
echo "=== Verificando método ==="
grep -n -A5 -B2 "verify_package_integrity" "$MANAGER"

echo
echo "=== Rodando teste ==="
python -m pytest tests/test_update_manager.py::test_update_manager_verifies_package_integrity -v
