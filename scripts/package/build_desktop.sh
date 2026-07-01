#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "[desktop] building frontend production assets"
cd "${REPO_ROOT}/frontend"
npm ci
npm run build

echo "[desktop] running Tauri build"
cd "${REPO_ROOT}/desktop"
npm install
npm run build

echo "[desktop] installers written to desktop/src-tauri/target/release/bundle/"
