# tests

## Purpose
Hosts quality strategy, test taxonomy, and validation criteria documentation.

## Responsibilities
- Define test levels: unit, integration, contract, load, security.
- Map acceptance criteria to automated and manual checks.
- Maintain release quality gates and evidence standards.

## Prompt 43 Performance Suite
- `performance/k6/load.js`: load profile for expected traffic behavior.
- `performance/k6/stress.js`: stress profile for saturation boundary testing.
- `performance/k6/benchmark.js`: benchmark profile for before/after optimization comparisons.
- `performance/results/`: run outputs (`--summary-export` JSON artifacts).

## Ownership
Quality Engineering

## Coding Standards
- No implementation code in this folder unless approved by Architecture Review Board and Product Governance.
- Changes SHALL align with approved architecture and SRS requirement IDs.
- Naming SHALL follow repository naming standards and semantic versioning policies.
- Security, privacy, and tenant isolation requirements SHALL be reflected in all artifacts.
