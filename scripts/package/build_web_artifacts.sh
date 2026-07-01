#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
VERSION="${VERSION:-local}"
OUTPUT_DIR="${REPO_ROOT}/dist/web"

mkdir -p "${OUTPUT_DIR}"

echo "[web-artifacts] building frontend production assets"
cd "${REPO_ROOT}/frontend"
NODE_ENV=production npm ci
NODE_ENV=production npm run build

echo "[web-artifacts] packaging archive"
tar -czf "${OUTPUT_DIR}/tkk-universal-validator-web-${VERSION}.tar.gz" -C "${REPO_ROOT}/frontend" dist

echo "[web-artifacts] artifact: ${OUTPUT_DIR}/tkk-universal-validator-web-${VERSION}.tar.gz"
