# scripts

## Purpose
Hosts operational automation for backup, restore, migration, and disaster recovery workflows.

## Responsibilities
- Execute repeatable operational tasks for database protection and recovery.
- Standardize migration execution across local, CI/CD, and Kubernetes environments.
- Provide DR drill checklist automation for operational readiness.

## Ownership
Platform Operations

## Coding Standards
- Scripts must be idempotent where possible and fail fast on errors (`set -euo pipefail`).
- Scripts SHALL align with approved architecture and SRS requirement IDs.
- Naming SHALL follow repository naming standards and semantic versioning policies.
- Security, privacy, and tenant isolation requirements SHALL be reflected in all artifacts.

## Prompt 42 Operational Scripts
- `backup/backup_postgres.sh`: creates PostgreSQL custom-format backups with checksums and retention cleanup.
- `restore/restore_postgres.sh`: restores PostgreSQL backups with optional checksum verification.
- `migration/run_alembic_migration.sh`: runs Alembic schema migrations to a target revision.
- `dr/dr_drill_checklist.sh`: prints DR drill checklist and RPO/RTO targets.

## Prompt 43 Performance Script
- `performance/run_k6_profile.sh`: runs load, stress, benchmark, or all k6 performance profiles.
