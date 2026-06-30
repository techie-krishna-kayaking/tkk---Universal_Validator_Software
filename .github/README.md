# .github

## Purpose
Hosts repository governance metadata for workflows, issue templates, labels, and milestones guidance.

## Responsibilities
- Define issue/PR governance taxonomy.
- Maintain labeling, milestone, and workflow standards.
- Ensure repository process consistency.

## GitHub Actions Workflows
- `workflows/ci.yml`: Pull request and push validation for backend and frontend (lint, tests, build).
- `workflows/docker-release.yml`: Builds and publishes backend/frontend images to GHCR on main and release tags.
- `workflows/deploy.yml`: Manual Helm-based deployment using environment gating (`dev`, `stage`, `prod`).
- `workflows/backup-dr.yml`: Manual Kubernetes backup, restore, and migration operations for DR readiness.
- `workflows/performance.yml`: Manual load, stress, and benchmark performance test execution with k6.

## Required Repository Secrets
- `KUBECONFIG_DATA`: Base64-encoded kubeconfig used by `deploy.yml`.

## Ownership
Engineering Productivity Team

## Coding Standards
- No implementation code in this folder unless approved by Architecture Review Board and Product Governance.
- Changes SHALL align with approved architecture and SRS requirement IDs.
- Naming SHALL follow repository naming standards and semantic versioning policies.
- Security, privacy, and tenant isolation requirements SHALL be reflected in all artifacts.
