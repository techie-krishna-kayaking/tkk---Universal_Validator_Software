# Semantic Versioning Strategy

## Version Format
MAJOR.MINOR.PATCH

## Rules
- MAJOR increments for breaking architecture or contract changes.
- MINOR increments for backward-compatible feature additions.
- PATCH increments for backward-compatible fixes and clarifications.

## Pre-release and Metadata
- Pre-release labels: -alpha.N, -beta.N, -rc.N
- Build metadata optional: +build.<id>

## Compatibility Policy
- API versioning SHALL align with semantic versioning.
- Plugin and connector compatibility matrix SHALL be versioned and published.
- Deprecation windows SHALL be announced before MAJOR removals.

## Examples
- 1.0.0: first stable baseline release.
- 1.1.0: adds non-breaking new reporting workflow.
- 1.1.1: fixes documentation defects.
- 2.0.0: introduces a breaking contract change.
