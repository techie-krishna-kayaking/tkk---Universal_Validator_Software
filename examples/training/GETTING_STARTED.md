# Getting Started — tkk-UniversalValidator

## Prerequisites
- Docker and Docker Compose
- Python 3.13 and Poetry (for local dev)

---

## Quick Start (Docker)

```bash
# Clone the repo
git clone https://github.com/techie-krishna-kayaking/tkk---Universal_Validator_Software.git
cd tkk---Universal_Validator_Software

# Start all services
docker compose up -d --build

# Seed demo data
python scripts/demo/seed_demo_data.py

# Open the dashboard
open http://localhost:8080
```

**Login credentials:**

| Role | Email | Password |
|---|---|---|
| Platform Admin | admin@tkkvalidator.local | Admin@123 |
| Architect | architect@tkkvalidator.local | Architect@123 |
| QA Lead | qalead@tkkvalidator.local | QALead@123 |
| QA Engineer | tester@tkkvalidator.local | Tester@123 |
| Viewer | viewer@tkkvalidator.local | Viewer@123 |

---

## Lab 1 — Explore the Dashboard

1. Log in as **architect** (`architect@tkkvalidator.local` / `Architect@123`).
2. Review the Overview page — notice the KPI cards for active jobs, pass rate, and failures.
3. Click **Projects** to see the pre-loaded demo projects.
4. Click **Connections** — note the connection types available.

---

## Lab 2 — Run the AMEX Migration Validation

**Scenario:** Validate 10,000 customer records migrated from Oracle to PostgreSQL.
The target data has intentional issues for demo purposes:
- 1 missing record (AMEX-1009)
- 1 extra record (AMEX-1011)
- 1 NULL balance (AMEX-1007)
- 1 phone number format change (AMEX-1006)
- 1 account type mismatch (AMEX-1010: PLATINUM → GOLD)

**Steps:**
1. Click **Validations → New Validation**.
2. Select project `AMEX-DM-001`.
3. Set Source: upload or point to `examples/demo_data/amex/customers_source.csv`.
4. Set Target: `examples/demo_data/amex/customers_target.csv`.
5. Set Primary Key: `customer_id`.
6. Enable validation rules: Record Count, Null Analysis, Data Comparison, Symmetric Difference.
7. Click **Run**.
8. View the report under **Reports**.

Or use the YAML workflow directly with the CLI:
```bash
cd backend
poetry run python -c "
from app.services.yaml_workflow_service import YAMLWorkflowService
import yaml, asyncio

with open('../sample_configs/demo_amex_migration.yaml') as f:
    wf = yaml.safe_load(f)

print('Workflow loaded:', wf['workflow_id'])
"
```

---

## Lab 3 — Run the Snowflake Migration Validation

**Scenario:** Validate product catalog records migrated to Snowflake.
Intentional issues:
- 2 missing records (SKU-2006 — inactive, SKU-2011)
- 1 stock quantity mismatch (SKU-2010: 450 → 460)
- 1 supplier ID mismatch (SKU-2010: SUP-104 → SUP-999)
- 1 new unexpected record (SKU-2012)

**Steps:**
1. Click **Validations → New Validation**.
2. Select project `SNOW-VAL-001`.
3. Source: `examples/demo_data/snowflake/products_source.csv`.
4. Target: `examples/demo_data/snowflake/products_target.csv`.
5. Primary Key: `product_id`.
6. Enable: Record Count, Data Comparison, Symmetric Difference.
7. Click **Run** and review the report.

---

## Lab 4 — AI Chatbot Validation

1. Click **AI Chatbot** in the left nav.
2. Type: _"Validate that all customer IDs in the AMEX migration target match the source and there are no nulls in the balance column"_
3. Review the generated validation plan.
4. Click **Apply and Run**.

---

## Lab 5 — Generate a SQL Validation Query

1. Click **SQL Generator**.
2. Type: _"Find all customer records where the account type changed between source and target"_
3. Select dialect: **PostgreSQL**.
4. Review the generated SQL, then click **Optimize**.
5. Click **Explain** to get a natural language explanation.

---

## Lab 6 — AI Report Explainer

1. After completing Lab 2 or Lab 3, go to **Reports**.
2. Open the completed report.
3. Click **Explain with AI**.
4. Review: Failure Summary, Anomaly Explanation, Recommended Fixes.

---

## Lab 7 — Administration

1. Log out and log back in as **admin** (`admin@tkkvalidator.local` / `Admin@123`).
2. Click **Administration**.
3. Review the list of users and their roles.
4. Try creating a new custom role with specific permissions.
5. View the audit log for recent activity.

---

## CLI Walkthrough

Run the automated walkthrough script:
```bash
BASE_URL=http://localhost:8000 bash scripts/demo/run_demo_walkthrough.sh
```

This exercises: health check → login → session → metrics in sequence.
