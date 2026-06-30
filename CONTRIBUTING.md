# Contributing Guidelines

## Purpose
This repository is architecture and requirements driven. Contributions must preserve the approved architecture baseline and requirement traceability.

## Contribution Workflow
1. Create or update an issue with objective, scope, and impacted requirement IDs.
2. Create a branch using the naming strategy in docs/GIT_BRANCHING_STRATEGY.md.
3. Submit documentation changes with explicit rationale and impacted artifacts.
4. Open a pull request with:
   - Summary
   - Requirement traceability
   - Security/compliance impact
   - Review checklist completion
5. Obtain mandatory approvals:
   - Domain owner
   - Security reviewer for security-impacting changes
   - Architecture reviewer for design-impacting changes

## Mandatory Standards
- No implementation code in current phase.
- No architecture redesign without Architecture Review Board decision record.
- Use precise language with SHALL/SHOULD/MAY where applicable.
- Preserve multi-tenant and security constraints.

## Pull Request Checklist
- Scope is documented and limited.
- Requirements/architecture traceability included.
- Naming conventions and doc style followed.
- No secrets, credentials, or sensitive data included.
- Changelog updated for user-visible documentation changes.
