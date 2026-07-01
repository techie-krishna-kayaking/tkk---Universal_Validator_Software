# Changelog

All notable changes to tkk-UniversalValidator are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [1.0.0] - 2026-07-01

### Phase 7 — Enterprise Readiness
- Security review: OWASP Top 10 assessment, STRIDE threat model, pen-test checklist, automated bandit/pip-audit/npm-audit CI scan.
- Comprehensive testing: Vitest frontend unit tests, backend security unit tests, Playwright API and E2E tests, comprehensive CI matrix workflow.
- Documentation suite: Developer Guide, User Guide, Admin Guide, Architecture Guide, API Docs, Plugin SDK.
- Packaging: Tauri v2 desktop installer scaffold (Windows .msi / macOS .dmg / Linux .AppImage/.deb/.rpm), Capacitor v7 mobile project (Android/iOS), web artifact pipeline.
- Release management: git-cliff changelog generation, release-drafter, automated GitHub Release workflow, version bump script.

### Phase 6 — DevOps and Deployment
- Docker multi-stage production images for backend and frontend; root `docker-compose.yml`.
- Kubernetes raw manifests and Helm chart with namespace, config, secrets, HPA, and ingress.
- Terraform multi-cloud modules for AWS (EKS, VPC, ECR), Azure (AKS, VNet, ACR), GCP (GKE, VPC, Artifact Registry) with `dev` environment wrappers.
- GitHub Actions workflows: CI, docker-release, deploy, backup-DR, performance, security-scan.
- Monitoring and observability: Prometheus metrics endpoint, OpenTelemetry tracing, ELK + Grafana Docker overlay, provisioned dashboard.
- Backup, restore, migration, and DR automation scripts; Kubernetes CronJob for scheduled backups.
- Performance testing: k6 load, stress, and benchmark profiles with CI integration.

### Phase 5 — AI Assistant
- AI Chatbot with natural language validation plan generation.
- Source-to-target mapping reader (Excel, Word, PDF) with auto validation case generation.
- SQL Generator: generate, optimize, explain SQL in multiple dialects.
- Test Case Generator: manual, automation, negative, boundary, edge cases.
- AI Report Explainer: summarize failures, explain anomalies, recommend fixes.
- Conversation History: search, bookmarks, export, share.

### Phase 4 — Enterprise Dashboard
- React 19 + TypeScript + Vite + MUI 7 dashboard with dark/light theme and role-based navigation.
- Dashboard widgets: KPIs, validation trends, pass/fail charts.
- Project Management UI.
- Connection Management UI with test and metadata preview.
- Validation Builder with rule selection.
- Execution Monitoring with live logs and queue status.
- Report Dashboard with interactive charts and export.
- Administration Console: organisations, users, teams, permissions, audit.
- Settings: secrets, themes, notifications, SMTP, AI providers.
- Accessibility: skip link, keyboard shortcuts (Alt+1/2/3), screen reader support, WCAG AA, multi-language (EN/ES/FR).

### Phase 3 — Core Validation Engine
- Universal Validation Engine with 23 validation types and plugin architecture.
- Execution engines: Pandas, PySpark, Polars, DuckDB with automatic selection.
- YAML Workflow Engine with schema validation and versioning.
- SQL Transformation Framework.
- Data Profiling Engine with HTML reports.
- Great Expectations integration.
- Isolation Forest anomaly detection.
- Result Storage Engine (database, CSV, JSON, Parquet, HTML, Excel).
- Report Generator (HTML, PDF, Excel, email, executive summary).
- Scheduler and Job Orchestration (Cron, one-time, recurring, retry, pause/resume).

### Foundation (Prompts 6–10)
- Backend: FastAPI + Python 3.13, SQLAlchemy 2, Alembic, Pydantic v2, Poetry, Redis, Celery, Structlog. Full middleware stack, health endpoints, OTEL, Prometheus.
- Authentication: JWT, MFA (TOTP), OAuth2 (Google/Microsoft/Azure AD/Okta), account lockout, password policies, login audit.
- Organisation, Team, Project, User, RBAC, and permission management.
- Secrets and configuration management with Fernet encryption and multi-source loading.
- Universal Connector Framework: plugin SDK, registry, loader, factory covering files, databases, cloud storage, big data, and APIs.

## [0.2.0] - 2026-06-15
### Added
- Backend authentication and enterprise security module.
- Secrets and configuration management module.
- Universal Connector Framework.

## [0.1.0] - 2026-06-01
### Added
- Repository structure, architecture documentation, SRS, and TDR.
- Backend foundation with application factory, middleware, health endpoints.
