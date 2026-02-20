#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   BACKEND_REPO=git@github.com:org/HomeTypeMap-backend.git \
#   FRONTEND_REPO=git@github.com:org/HomeTypeMap-frontend.git \
#   ./scripts/split_repos.sh

if [[ -z "${FRONTEND_REPO:-}" ]]; then
  echo "FRONTEND_REPO is required"
  exit 1
fi

git checkout main
git pull --ff-only origin main

echo "[1/2] Split frontend subtree..."
git subtree split --prefix=frontend -b split/frontend
git push "${FRONTEND_REPO}" split/frontend:main

if [[ -n "${BACKEND_REPO:-}" ]]; then
  echo "[2/2] Backend split placeholder..."
  echo "Use docs/repo-split-playbook.md to move app/alembic/tests/scripts safely."
else
  echo "[2/2] BACKEND_REPO not set, skip backend push."
fi

echo "Done."
