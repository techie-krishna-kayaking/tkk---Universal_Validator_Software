# User Guide — tkk-UniversalValidator

## What is tkk-UniversalValidator?

tkk-UniversalValidator is an enterprise-grade Universal Data Validation Platform. It enables data engineering and QA teams to validate data quality across databases, files, cloud storage, and APIs — using a visual dashboard, AI-assisted workflows, and YAML-driven automation.

---

## Accessing the Platform

Open your browser and navigate to the URL provided by your administrator (typically `https://your-org.tkkvalidator.com`).

In development and staging environments, a **Demo Mode** banner at the login screen offers prefilled credentials for testing. This is disabled in production.

Development seed context:
- Organization: `TKK Technologies Pvt Ltd` (`TKK-ORG-001`)
- Team: `Data Engineering Team` (`TEAM-DE-001`)
- Projects: `American Express Data Migration` (`AMEX-DM-001`) and `Snowflake Migration Validation` (`SNOW-VAL-001`)

Development test users:
- `admin / Admin@123` (Platform Admin)
- `orgadmin / Admin@123` (Organization Admin)
- `architect / Architect@123` (Architect)
- `qalead / QALead@123` (QA Lead)
- `tester / Tester@123` (QA Engineer)
- `dataengineer / Data@123` (Data Engineer)
- `viewer / Viewer@123` (Viewer)
- `guest / Guest@123` (Guest)

---

## Default Roles

| Role | Description |
|---|---|
| Platform Admin | Full system access including org management |
| Organization Admin | Manages users, teams, and org-wide settings |
| Architect | Creates connections, designs workflows, configures AI |
| Data Engineer | Runs validation workflows and data quality checks |
| QA Lead | Creates and runs validations, views all reports |
| QA Engineer | Runs validations, views reports |
| Viewer | Read-only access to reports and dashboards |
| Guest | Restricted access, no execution |

Your role determines which navigation menu items and actions are available to you.

---

## Dashboard Overview

After login you land on the **Overview** page showing:
- Active validation job count
- Pass / fail trend over the last 7 days
- Top failing validation suites
- Upcoming scheduled jobs

---

## Projects

Projects group related validation suites. To create a project:

1. Click **Projects** in the left menu.
2. Click **+ New Project**.
3. Enter project name, code, and optional description.
4. Assign a team.
5. Click **Save**.

---

## Connections

Connections define how the platform connects to your data sources and targets.

Supported categories:
- **Files** — CSV, TSV, Excel, JSON, Parquet, XML, Avro, ORC, Delta, Iceberg
- **Databases** — PostgreSQL, MySQL, Snowflake, Redshift, BigQuery, Databricks SQL, and more
- **Cloud Storage** — AWS S3, Azure Blob, Azure Data Lake, GCS, SharePoint, OneDrive
- **Big Data** — Spark, Hive, Delta Lake, Kafka
- **APIs** — REST, GraphQL, OpenAPI

To add a connection:
1. Click **Connections** → **+ Add Connection**.
2. Select the connection type.
3. Fill in credentials and host details.
4. Click **Test Connection** to verify before saving.

Credentials are encrypted at rest using Fernet encryption.

---

## Validation Builder

The Validation Builder provides a guided interface to design validation jobs:

1. Click **Validations** → **+ New Validation**.
2. Select **Source** connection and object (table/file).
3. Optionally select a **Target** for comparison validations.
4. Choose **Primary Keys** for row-level matching.
5. Select validation rules from the rule library:
   - Record Count, Column Count, Duplicate Detection, Null Analysis
   - Data Comparison, Row Checksum, Symmetric Difference
   - Date Range, Precision, Scale, Distinct Count, and more
   - Great Expectations suite execution
   - Isolation Forest anomaly detection
   - Custom SQL and Python validators
6. Click **Preview** to sample the data.
7. Click **Run** to execute immediately, or configure a **Schedule**.

---

## Executing and Monitoring Jobs

Navigate to **Execution** to see:
- Running jobs with live progress
- Completed and cancelled jobs
- Celery queue status
- Full execution logs per job

You can pause, resume, or cancel jobs from this view.

---

## Reports

Navigate to **Reports** to:
- Filter by project, date range, and status
- View pass/fail breakdowns with interactive charts
- Download reports in HTML, PDF, Excel, CSV, or JSON
- Share report links or email reports directly

---

## AI Assistant Features

### AI Chatbot
Click **AI Chatbot** to describe a validation goal in natural language. The chatbot generates a validation plan and optionally runs it.

### Mapping Reader
Click **Mapping Reader** to upload a source-to-target mapping document (Excel, Word, PDF). The platform parses the mapping and auto-generates validation cases.

### SQL Generator
Click **SQL Generator** to describe data logic in plain English. The platform generates, optimises, and explains SQL for your target dialect (PostgreSQL, Snowflake, Databricks).

### Test Case Generator
Click **Test Case Generator** to generate manual, automation, negative, boundary, and edge test cases for any validation suite.

### AI Report Explainer
On any completed report, click **Explain with AI** to receive a plain-language summary, anomaly explanations, and recommended fixes.

---

## Settings

Click **Settings** to manage:
- **Secrets** — encrypt and store credentials for your integrations
- **Theme** — switch between dark and light mode
- **Notifications** — configure email, Slack, and Teams alerts
- **SMTP** — set up outbound email
- **AI Providers** — configure OpenAI, Azure OpenAI, or Ollama endpoints
- **Language** — switch between English, Spanish, and French

---

## Accessibility

The platform supports screen readers, keyboard navigation, and WCAG 2.1 AA standards.

Keyboard shortcuts:
- `Alt+1` — Dashboard
- `Alt+2` — Validations
- `Alt+3` — Projects

A skip-to-content link is available at the top of every page. Language can be changed from the header toolbar.
