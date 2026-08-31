#!/usr/bin/env bash
# Build the submission ZIP.
#
# Uses `git archive` rather than zipping the working tree, so the archive
# contains exactly what is committed — no virtual environment, no
# node_modules, no build output, no test caches — which is what the
# submission guidelines require. If it isn't committed, it isn't shipped.
set -euo pipefail
cd "$(dirname "$0")"

OUT="PathFinder-CriticalPath.zip"

if [ -n "$(git status --porcelain)" ]; then
  echo "warning: uncommitted changes will NOT be included:" >&2
  git status --short >&2
  echo >&2
fi

rm -f "$OUT"
git archive --format=zip --prefix=PathFinder/ -o "$OUT" HEAD
echo "Wrote $OUT ($(du -h "$OUT" | cut -f1), $(unzip -l "$OUT" | tail -1 | awk '{print $2}') files)"
