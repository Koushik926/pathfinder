#!/usr/bin/env bash
# Deploy PathFinder to a Hugging Face Docker Space.
#
# Prerequisite (run once, in your own terminal so the token never leaves it):
#     hf auth login
#
# Then:  ./deploy/deploy-hf-space.sh [space-name]
set -euo pipefail
cd "$(dirname "$0")/.."

SPACE_NAME="${1:-pathfinder}"

if ! hf auth whoami >/dev/null 2>&1; then
  echo "Not logged in. Run:  hf auth login" >&2
  exit 1
fi
USER="$(hf auth whoami 2>/dev/null | head -1 | awk '{print $1}' | tr -d '[:space:]')"
if [ -z "$USER" ]; then echo "Could not determine your Hugging Face username." >&2; exit 1; fi
REPO="$USER/$SPACE_NAME"
echo "Deploying to https://huggingface.co/spaces/$REPO"

# Stage exactly what the image needs, plus the Space README that carries the
# YAML front-matter Hugging Face reads (sdk: docker, app_port).
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
git archive HEAD | tar -x -C "$STAGE"
cp deploy/space-README.md "$STAGE/README.md"
rm -rf "$STAGE/docs" "$STAGE/deploy" "$STAGE/SUBMISSION.md"

hf repo create "$REPO" --repo-type space --space_sdk docker --exist-ok

hf upload "$REPO" "$STAGE" . --repo-type space \
  --commit-message "Deploy PathFinder"

echo
echo "Building. Watch progress at:"
echo "  https://huggingface.co/spaces/$REPO"
echo "Live URL once the build finishes:"
echo "  https://${USER//./-}-${SPACE_NAME}.hf.space"
