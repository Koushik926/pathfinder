#!/usr/bin/env bash
# Produce the submission ZIP: source only, no venv, node_modules or build output.
set -euo pipefail
cd "$(dirname "$0")"
OUT="PathFinder-CriticalPath.zip"
rm -f "$OUT"
zip -r "$OUT" . \
  -x '*.git/*' '*/.venv/*' '*/node_modules/*' '*/dist/*' '*/__pycache__/*' \
     '*.pyc' '*.egg-info/*' '*.DS_Store' "$OUT" >/dev/null
echo "Wrote $OUT ($(du -h "$OUT" | cut -f1))"
