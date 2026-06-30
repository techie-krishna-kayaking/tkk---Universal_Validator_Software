# Git Branching Strategy

## Branch Model
- main: production-ready branch; protected, release-tagged, signed commits only.
- develop: integration branch for next release train.
- feature/<area>-<ticket>: feature and documentation changes.
- release/<major>.<minor>.0: release stabilization branch.
- hotfix/<major>.<minor>.<patch>: urgent production fixes.

## Pull Request Rules
- Minimum two reviewers for architecture-impacting changes.
- Mandatory checks: linting of markdown, link validation, policy checks.
- Rebase or squash merge only.
- No direct push to main or develop.

## Branch Protection
- Required status checks must pass before merge.
- Require signed commits.
- Require linear history.
- Restrict force push and branch deletion.

## Naming Convention
- feature/security-rbac-matrix-update
- feature/docs-validation-workflow-revision
- release/1.2.0
- hotfix/1.2.1

## Release Flow
1. Merge approved work into develop.
2. Cut release branch from develop.
3. Stabilize and finalize release notes.
4. Merge release branch into main and tag version.
5. Back-merge release branch into develop.
