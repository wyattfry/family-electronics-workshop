#!/usr/bin/env bash
# Build the static site into _site/ (MkDocs Material). The repo stays readable on
# GitHub as-is; this copies the content into _site_src/ because MkDocs can't use the
# repo root itself as its docs folder.
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf _site_src _site
mkdir _site_src
rsync -a \
  --exclude '.git' --exclude '.github' --exclude '.venv' --exclude '_site*' \
  --exclude 'tools' --exclude '__pycache__' --exclude '.pytest_cache' \
  --exclude 'mkdocs.yml' --exclude 'requirements*.txt' --exclude '.gitignore' \
  ./ _site_src/
mkdocs build "$@"
