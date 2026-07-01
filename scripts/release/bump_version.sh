#!/usr/bin/env bash
# bump_version.sh — atomically bumps version across all package manifests,
# commits, and creates an annotated git tag.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

NEW_VERSION="${1:-}"

usage() {
  echo "Usage: $0 <new-version>"
  echo "  Example: $0 1.2.0"
  exit 1
}

[[ -z "${NEW_VERSION}" ]] && usage

TAG="v${NEW_VERSION}"

echo "[release] bumping all manifests to ${NEW_VERSION}"

# backend/pyproject.toml
sed -i.bak "s/^version = \".*\"/version = \"${NEW_VERSION}\"/" "${REPO_ROOT}/backend/pyproject.toml"
rm -f "${REPO_ROOT}/backend/pyproject.toml.bak"

# frontend/package.json
sed -i.bak "s/\"version\": \".*\"/\"version\": \"${NEW_VERSION}\"/" "${REPO_ROOT}/frontend/package.json"
rm -f "${REPO_ROOT}/frontend/package.json.bak"

# desktop/package.json
sed -i.bak "s/\"version\": \".*\"/\"version\": \"${NEW_VERSION}\"/" "${REPO_ROOT}/desktop/package.json"
rm -f "${REPO_ROOT}/desktop/package.json.bak"

# desktop/src-tauri/tauri.conf.json
sed -i.bak "s/\"version\": \".*\"/\"version\": \"${NEW_VERSION}\"/" "${REPO_ROOT}/desktop/src-tauri/tauri.conf.json"
rm -f "${REPO_ROOT}/desktop/src-tauri/tauri.conf.json.bak"

# mobile/package.json
sed -i.bak "s/\"version\": \".*\"/\"version\": \"${NEW_VERSION}\"/" "${REPO_ROOT}/mobile/package.json"
rm -f "${REPO_ROOT}/mobile/package.json.bak"

# desktop/src-tauri/Cargo.toml
sed -i.bak "s/^version = \".*\"/version = \"${NEW_VERSION}\"/" "${REPO_ROOT}/desktop/src-tauri/Cargo.toml"
rm -f "${REPO_ROOT}/desktop/src-tauri/Cargo.toml.bak"

echo "[release] committing version bump"
cd "${REPO_ROOT}"
git add \
  backend/pyproject.toml \
  frontend/package.json \
  desktop/package.json \
  desktop/src-tauri/tauri.conf.json \
  desktop/src-tauri/Cargo.toml \
  mobile/package.json

git commit -m "chore: bump version to ${NEW_VERSION}"

echo "[release] creating annotated tag ${TAG}"
git tag -a "${TAG}" -m "Release ${TAG}"

echo ""
echo "Done. Push with:"
echo "  git push origin main ${TAG}"
