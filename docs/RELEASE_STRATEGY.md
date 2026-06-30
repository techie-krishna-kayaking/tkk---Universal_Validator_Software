# Release Strategy

## Release Types
- Monthly minor release train for new capabilities.
- On-demand patch releases for high-priority fixes.
- Semiannual major releases for controlled breaking changes.

## Environments
- dev -> test -> stage -> prod promotion path.
- Promotion requires documented approval gates and evidence.

## Release Gates
- Requirement traceability complete.
- Security review complete for impacted areas.
- Architecture review complete for design-impacting changes.
- Changelog and release notes complete.
- Rollback plan and risk assessment complete.

## Artifacts
- Versioned tag and signed release notes.
- Updated changelog.
- Updated architecture and SRS references where applicable.

## Rollback Policy
- Each release must have tested rollback steps.
- Critical incidents trigger rollback to last known-good version.
- Incident review and corrective actions required post-rollback.
