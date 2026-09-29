#!/usr/bin/env bash
# Regenerate every schemdraw schematic: units/*/*.py (excluding code/ and firmware/) -> .svg
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
py="$root/.venv/bin/python"
for script in "$root"/units/*/*.py; do
  (cd "$(dirname "$script")" && "$py" "$(basename "$script")")
  echo "built ${script%.py}.svg"
done
