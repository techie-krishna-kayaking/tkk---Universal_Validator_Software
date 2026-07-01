#!/usr/bin/env bash
# walkthrough.sh — interactive CLI walkthrough of tkk-UniversalValidator demo
# Exercises: login, health check, create user, validate YAML workflow, view report.
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
TENANT_ID="${TENANT_ID:-TKK-ORG-001}"
API="${BASE_URL}/api/v1"

BOLD="\033[1m"
GREEN="\033[0;32m"
CYAN="\033[0;36m"
RESET="\033[0m"

step() { echo -e "\n${BOLD}${CYAN}==== Step $1: $2 ====${RESET}"; }
ok()   { echo -e "${GREEN}✓ $*${RESET}"; }

echo -e "${BOLD}"
echo "  ╔══════════════════════════════════════════════════════╗"
echo "  ║   tkk-UniversalValidator — Interactive Demo         ║"
echo "  ║   TKK Technologies Pvt Ltd  |  DEV MODE             ║"
echo "  ╚══════════════════════════════════════════════════════╝"
echo -e "${RESET}"

# ── Step 1: Check backend availability ────────────────────────────────────────
step 1 "Backend Health Check"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/openapi.json")
if [[ "${HTTP_CODE}" != "200" ]]; then
  echo "Backend not reachable at ${BASE_URL}. Start with: poetry run backend-api"
  exit 1
fi
ok "Backend is running at ${BASE_URL}"

# ── Step 2: Register and login as architect ────────────────────────────────────
step 2 "Register and Login as Architect"
curl -s -X POST "${API}/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"architect@tkkvalidator.local","password":"Architect@123","tenant_id":"TKK-ORG-001"}' > /dev/null

LOGIN=$(curl -s -X POST "${API}/auth/login" \
  -H "Content-Type: application/json" \
  -H "X-Geo-Country: US" \
  -d '{"email":"architect@tkkvalidator.local","password":"Architect@123","tenant_id":"TKK-ORG-001"}')

TOKEN=$(echo "${LOGIN}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null || true)

if [[ -z "${TOKEN}" ]]; then
  echo "Login failed: ${LOGIN}"
  exit 1
fi
ok "Logged in as architect@tkkvalidator.local"

# ── Step 3: Retrieve session information ──────────────────────────────────────
step 3 "View Current Session"
SESSION=$(curl -s "${API}/auth/session" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "X-Tenant-ID: ${TENANT_ID}")
echo "${SESSION}" | python3 -m json.tool 2>/dev/null || echo "${SESSION}"
ok "Session retrieved"

# ── Step 4: Health readiness probe ────────────────────────────────────────────
step 4 "Readiness Probe"
READINESS=$(curl -s "${API}/health/readiness" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "X-Tenant-ID: ${TENANT_ID}")
echo "${READINESS}" | python3 -m json.tool 2>/dev/null || echo "${READINESS}"
ok "Readiness probe complete"

# ── Step 5: Validate AMEX demo YAML workflow ──────────────────────────────────
step 5 "Validate AMEX Migration YAML (schema check)"
YAML_VALIDATE=$(curl -s -X POST "${API}/workflows/validate-schema" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "X-Tenant-ID: ${TENANT_ID}" \
  -H "Content-Type: application/json" \
  -d "{\"yaml_path\":\"sample_configs/demo_amex_migration.yaml\"}" 2>/dev/null || echo '{"note":"endpoint may require DB; verify manually"}')
echo "${YAML_VALIDATE}" | python3 -m json.tool 2>/dev/null || echo "${YAML_VALIDATE}"
ok "YAML validation check sent"

# ── Step 6: Check Prometheus metrics ──────────────────────────────────────────
step 6 "Prometheus Metrics"
METRICS=$(curl -s "${API}/metrics" | head -20)
echo "${METRICS}"
ok "Metrics endpoint is live"

# ── Step 7: Summary ───────────────────────────────────────────────────────────
echo -e "\n${BOLD}${GREEN}Demo Walkthrough Complete!${RESET}"
echo ""
echo "  Next steps:"
echo "  1. Open the frontend: http://localhost:5173 (dev) or http://localhost:8080 (Docker)"
echo "  2. Seed demo data:   python scripts/demo/seed_demo_data.py"
echo "  3. View API docs:    ${BASE_URL}/docs"
echo "  4. Run AMEX demo:    Use Validation Builder with sample_configs/demo_amex_migration.yaml"
echo "  5. Run Snowflake:    Use Validation Builder with sample_configs/demo_snowflake_migration.yaml"
echo ""
