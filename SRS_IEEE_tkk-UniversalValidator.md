# tkk-UniversalValidator
## IEEE-Style Software Requirements Specification (SRS)
Document ID: TKK-UV-SRS-001
Version: 1.0
Date: 2026-06-30
Status: Approved for Product Build Planning
Architecture Baseline Reference: SOFTWARE_ARCHITECTURE_DOCUMENT.md v1.0

## 1. Introduction
### 1.1 Purpose
This document defines complete software requirements for tkk-UniversalValidator using only the approved architecture baseline. It is intended for product management, engineering, QA, security, operations, and compliance teams to implement the platform without ambiguity.

### 1.2 Scope
tkk-UniversalValidator is an enterprise, multi-tenant Universal Data Validation Platform providing:
- Cross-platform validation for files, APIs, databases, cloud stores, and BI data assets.
- Policy-driven execution with team-level governance and RBAC.
- Multi-mode validation engine (standard, regression, anomaly detection, Great Expectations rules).
- Control-plane APIs, asynchronous execution plane, and plugin ecosystem.
- Enterprise-grade security, auditability, observability, and reliability.

### 1.3 Intended Audience
- Product owners and business stakeholders.
- Backend, frontend, data, and platform engineers.
- QA and test automation teams.
- Security, compliance, and governance teams.
- Site reliability and cloud operations teams.

### 1.4 Definitions and Acronyms
- API: Application Programming Interface
- RBAC: Role-Based Access Control
- ABAC: Attribute-Based Access Control constraints
- OIDC: OpenID Connect
- SAML: Security Assertion Markup Language
- MFA: Multi-Factor Authentication
- PDP/PEP: Policy Decision Point / Policy Enforcement Point
- RPO/RTO: Recovery Point Objective / Recovery Time Objective
- SLA/SLO: Service Level Agreement / Service Level Objective
- DLQ: Dead Letter Queue
- GE: Great Expectations

### 1.5 Document Conventions
- Requirement statements use SHALL, SHOULD, MAY.
- Functional requirements are identified as FR-xxx.
- Non-functional requirements are identified as NFR-xxx.
- Acceptance criteria are identified as AC-xxx.

## 2. Executive Summary
tkk-UniversalValidator SHALL provide enterprise organizations a unified platform to validate data quality and reconciliation across heterogeneous sources and targets. The solution SHALL support large-scale workloads through a control-plane and queue-driven execution-plane architecture, enabling secure, auditable, tenant-isolated operations.

The platform SHALL include:
- End-user web experience and API-first automation.
- Configurable data validation workflows for file, database, API, and cloud sources.
- Team-aware governance, licensing, and operational observability.
- AI chatbot-assisted authoring, diagnostics, and reporting.

## 3. Business Goals
- BG-01: Reduce validation cycle times by at least 70% compared with manual baseline.
- BG-02: Detect high-severity data defects prior to production release in at least 95% of regression runs.
- BG-03: Support enterprise tenant onboarding with delegated administration.
- BG-04: Achieve enterprise security posture with SSO, MFA, fine-grained RBAC, and immutable audit.
- BG-05: Provide API-driven and UI-driven operations for diverse engineering maturity levels.
- BG-06: Enable a commercial licensing model with tiered feature entitlements.

## 4. Stakeholders
- Executive Sponsor: Business outcome ownership.
- Product Management: Feature prioritization and release scope.
- Enterprise Architects: Architecture governance and standards alignment.
- Platform Engineering: Control plane and execution plane implementation.
- Data Engineering Teams: Validation template authoring and job execution.
- QA Teams: Validation coverage and acceptance quality gates.
- Security and Compliance: Identity, controls, and audit conformance.
- Operations/SRE: Availability, scaling, and incident response.
- Tenant Administrators: Org/team setup, access, and governance.
- End Users (Architect/Tester/Viewer): Daily validation operations.

## 5. User Personas
- Persona P1: Super Admin
  - Manages global settings, tenant policies, platform-level controls.
  - Needs visibility into all tenants and platform health.
- Persona P2: Org Admin
  - Manages organizations, teams, subscriptions, entitlements.
  - Needs user lifecycle controls and policy assignment.
- Persona P3: Team Admin
  - Manages project access, team roles, and operational governance.
  - Needs efficient member onboarding and permission delegation.
- Persona P4: Architect
  - Creates connectors, templates, schedules, and advanced validation plans.
  - Needs deep diagnostics and broad configuration access.
- Persona P5: Tester
  - Runs validations, analyzes failures, exports reports.
  - Needs controlled execution access and clear actionable errors.
- Persona P6: Auditor
  - Reviews access logs, data lineage, and compliance evidence.
  - Needs immutable audit trail and filterable reporting.
- Persona P7: Viewer
  - Consumes dashboards and summary outcomes.
  - Needs read-only access and SLA-focused visibility.

## 6. Product Perspective
The platform SHALL implement the approved architecture:
- Control Plane services for identity, policy, project/configuration, scheduling, reporting, AI.
- Execution Plane services for queue-driven job orchestration, connector runtime, and validation workers.
- Shared data layer with metadata database, cache, and object storage.
- Plugin ecosystem for connectors, validators, reporting, notifications, and AI tools.

## 7. Functional Requirements
### 7.1 Identity, Access, and Tenant Management
- FR-001: The system SHALL support enterprise SSO using OIDC/SAML with Okta, Azure AD, and Google Workspace.
- FR-002: The system SHALL enforce MFA according to organization policy.
- FR-003: The system SHALL provide tenant-scoped organizations, teams, users, and project ownership.
- FR-004: The system SHALL enforce deny-by-default authorization using RBAC with attribute constraints.
- FR-005: The system SHALL provide delegated administration for Org Admin and Team Admin roles.
- FR-006: The system SHALL support invitation, activation, suspension, and role reassignment workflows.

### 7.2 Project, Configuration, and Template Management
- FR-007: The system SHALL allow creation and management of projects and folders.
- FR-008: The system SHALL support YAML-based and UI-based configuration authoring.
- FR-009: The system SHALL support reusable validation templates and template versioning.
- FR-010: The system SHALL maintain configuration change history and rollback metadata.

### 7.3 Connection and Connector Management
- FR-011: The system SHALL support source/target connection categories: database, file/object storage, API, cloud, and BI metadata.
- FR-012: The system SHALL validate connectivity and capability checks before run submission.
- FR-013: The system SHALL abstract secrets through secret references and never expose secret values in logs or UI.
- FR-014: The connector runtime SHALL support schema introspection and metadata retrieval.
- FR-015: The connector runtime SHALL support predicate pushdown where connector capability allows.

### 7.4 Validation Execution
- FR-016: The system SHALL support ad hoc, scheduled, and event-triggered validation execution.
- FR-017: The system SHALL execute standard validation checks:
  - Record count
  - Column count
  - Metadata types compatibility
  - Duplicate detection
  - Null analysis
  - Empty string detection
  - Data value comparison
- FR-018: The system SHALL execute regression validation checks:
  - Column order
  - Precision/scale/length
  - Distinct values
  - Date range min/max
  - Case sensitivity
  - Leading zeros
  - Special characters
  - Row checksums
  - Symmetric difference
- FR-019: The system SHALL support anomaly detection workflows using isolation-forest style analytics under approved engine mode.
- FR-020: The system SHALL support Great Expectations rule execution as a validation pack.
- FR-021: The system SHALL support compute engine selection policy (Pandas/Polars for small-medium workloads, Spark for large/distributed workloads) and tenant override controls.
- FR-022: The system SHALL support retries with configured backoff for transient execution failures.
- FR-023: The system SHALL publish execution states: queued, running, succeeded, failed, canceled, timed_out.

### 7.5 Results and Reporting
- FR-024: The system SHALL store validation summaries and detailed outcomes (check, column, row where applicable).
- FR-025: The system SHALL generate downloadable artifacts in CSV, JSON, HTML, and PDF.
- FR-026: The system SHALL support result persistence into configured result tables/warehouses.
- FR-027: The dashboard SHALL provide run KPIs, pass/fail trends, and drill-down diagnostics.
- FR-028: The system SHALL support notification subscriptions for run outcomes.

### 7.6 AI Chatbot
- FR-029: The system SHALL provide AI-assisted validation authoring from natural language prompts.
- FR-030: The system SHALL provide AI-assisted diagnostics for failed runs using approved data scope.
- FR-031: The system SHALL store tenant-isolated chat sessions and message history.
- FR-032: The system SHALL enforce policy-aware tool access and redact sensitive values in chatbot outputs.

### 7.7 Team Management and Governance
- FR-033: The system SHALL support team-level ownership of projects, templates, and schedules.
- FR-034: The system SHALL support access request and approval workflows for restricted resources.
- FR-035: The system SHALL enforce entitlement gates according to license tier.
- FR-036: The system SHALL maintain immutable audit records for security and governance actions.

### 7.8 API and Integration
- FR-037: The platform SHALL provide versioned REST APIs for all control-plane operations.
- FR-038: The platform SHALL provide asynchronous status updates via WebSocket/SSE for long-running jobs.
- FR-039: The platform SHALL implement idempotency keys for job submission APIs.
- FR-040: The platform SHALL expose OpenAPI specifications for published APIs.

## 8. Non-Functional Requirements
- NFR-001: The system SHALL target availability of 99.95% for Business tier and 99.99% for Enterprise tier.
- NFR-002: The platform SHALL be multi-tenant with strict tenant isolation controls.
- NFR-003: All service interfaces SHALL be versioned and backward-compatibility managed.
- NFR-004: The platform SHALL support horizontal scaling for execution workers independent of control-plane nodes.
- NFR-005: The platform SHALL provide full observability (metrics, logs, traces).
- NFR-006: The platform SHALL provide immutable audit logs for sensitive actions.
- NFR-007: The platform SHALL support automated backup and disaster recovery operations.
- NFR-008: The platform SHALL enforce secure-by-default configuration baselines.

## 9. Performance Requirements
- PR-001: Metadata/control-plane API endpoints SHALL meet P95 latency under 300 ms.
- PR-002: Job submission acknowledgement SHALL occur within 2 seconds under normal load.
- PR-003: Dashboard summary retrieval SHALL meet P95 under 1.5 seconds for standard filter scopes.
- PR-004: Queue dispatch-to-worker-start SHALL meet P95 under 5 seconds in healthy state.
- PR-005: Report generation for completed jobs SHALL meet P95 under 30 seconds for standard dataset outputs.

## 10. Scalability Requirements
- SR-001: The platform SHALL support at least 100,000 concurrent authenticated users.
- SR-002: The platform SHALL support at least 1,000,000 validation jobs per day.
- SR-003: Execution workers SHALL scale horizontally based on queue lag and resource utilization.
- SR-004: Connector runtime SHALL support parallel execution isolation per tenant/project policy.
- SR-005: Storage layers SHALL support retention-based archival without service downtime.

## 11. Security Requirements
- SEC-001: All user authentication SHALL occur via enterprise IdP (OIDC/SAML).
- SEC-002: MFA SHALL be enforceable at organization or tenant level.
- SEC-003: Authorization SHALL use central policy decision with deny-by-default enforcement.
- SEC-004: Data in transit SHALL be encrypted via TLS 1.2+.
- SEC-005: Data at rest SHALL be encrypted with managed key services.
- SEC-006: Secrets SHALL be managed through secret references and external secret manager integration.
- SEC-007: Sensitive fields SHALL be redacted in logs, traces, and exports.
- SEC-008: Service-to-service communication SHALL support mTLS/workload identity patterns.
- SEC-009: The platform SHALL provide periodic security posture reports and vulnerability status visibility.

## 12. Compliance Requirements
- CMP-001: The platform SHALL support controls aligned to SOC 2 and ISO 27001 operational standards.
- CMP-002: The platform SHALL support GDPR-oriented data subject handling controls where tenant-configured.
- CMP-003: The platform SHALL retain audit and policy decision logs according to tenant retention policy.
- CMP-004: The platform SHALL support evidence export for compliance audits.

## 13. Accessibility Requirements
- ACC-001: Web interfaces SHALL align with WCAG 2.1 AA guidelines.
- ACC-002: Keyboard-only navigation SHALL be supported for all critical workflows.
- ACC-003: Critical status indicators SHALL not depend on color-only signaling.
- ACC-004: Charts SHALL include textual summary alternatives.

## 14. Internationalization Requirements
- I18N-001: User interface strings SHALL support localization framework and translation bundles.
- I18N-002: Date/time formatting SHALL be locale-aware with timezone controls.
- I18N-003: Number and currency formatting SHALL be locale-aware.
- I18N-004: Unicode data handling SHALL preserve source fidelity in validation outputs.

## 15. Error Handling Requirements
- ERR-001: APIs SHALL return consistent structured error envelopes with correlation IDs.
- ERR-002: Permission errors SHALL explicitly indicate missing privilege without disclosing protected details.
- ERR-003: Connector errors SHALL classify root cause category: authentication, authorization, connectivity, schema, runtime.
- ERR-004: Retriable failures SHALL be retried according to policy; terminal failures SHALL be surfaced with remediation guidance.
- ERR-005: User-visible errors SHALL include actionable next steps and support trace references.

## 16. Logging Requirements
- LOG-001: Services SHALL emit structured JSON logs.
- LOG-002: Logs SHALL include timestamp, service, environment, trace_id, tenant_id, user_id where applicable.
- LOG-003: Security events SHALL be logged with event type, principal, action, resource, and outcome.
- LOG-004: Logging SHALL include redaction guardrails for secrets/PII.
- LOG-005: Log retention SHALL be policy-driven per tenant and compliance tier.

## 17. Audit Requirements
- AUD-001: Audit records SHALL be immutable and tamper-evident.
- AUD-002: The platform SHALL audit authentication, authorization decisions, role changes, configuration changes, run submissions, and report exports.
- AUD-003: Audit queries SHALL support filtering by tenant, actor, resource, action, and time window.
- AUD-004: Audit export SHALL be available to authorized auditor roles.

## 18. Backup Strategy
- BAK-001: Metadata database backups SHALL occur at scheduled intervals with point-in-time recovery support.
- BAK-002: Artifact storage SHALL be replicated and versioned according to policy.
- BAK-003: Backup verification SHALL run on scheduled restore-test cadence.
- BAK-004: Backup policy SHALL support tenant-specific retention tiers.

## 19. Disaster Recovery Requirements
- DR-001: The platform SHALL provide documented DR runbooks for control plane, execution plane, and data stores.
- DR-002: Target RPO SHALL be <= 15 minutes.
- DR-003: Target RTO SHALL be <= 60 minutes.
- DR-004: DR drills SHALL be executed at regular intervals with tracked outcomes.

## 20. User Stories
- US-001 (Architect): As an Architect, I want to define reusable validation templates so teams can standardize checks.
- US-002 (Tester): As a Tester, I want to run a template against source and target systems and receive pass/fail diagnostics.
- US-003 (Team Admin): As a Team Admin, I want to control who can create connectors and run jobs.
- US-004 (Org Admin): As an Org Admin, I want to enforce SSO, MFA, and retention policies.
- US-005 (Auditor): As an Auditor, I want immutable logs for access, policy, and execution events.
- US-006 (Viewer): As a Viewer, I want summary dashboards and trend reports without edit privileges.
- US-007 (Architect): As an Architect, I want the system to auto-select compute backend for performance.
- US-008 (Tester): As a Tester, I want AI assistant guidance when a run fails.

## 21. Use Cases
### UC-01: Create and Validate Connection
Preconditions:
- User has connection management permission.
- Tenant secret manager integration is configured.
Main flow:
1. User creates connection metadata and secret references.
2. System validates permission and policy.
3. Connector runtime performs connectivity and schema capability test.
4. System persists connection and status.
Postconditions:
- Connection is available for project use.

### UC-02: Run Validation Job
Preconditions:
- User has run permission for project/template.
- Source and target connections are active.
Main flow:
1. User submits run via UI/API.
2. Control plane validates idempotency, policy, and license entitlements.
3. Job is queued and assigned to execution workers.
4. Validation engine runs selected checks and stores outcomes.
5. Dashboard and notifications update.
Postconditions:
- Run artifacts and audit records are persisted.

### UC-03: Schedule Recurring Validation
Preconditions:
- User has scheduler permission.
Main flow:
1. User defines cron/event trigger.
2. Scheduler validates trigger and permissions.
3. Scheduled runs are emitted to queue and executed.
Postconditions:
- Historical schedule runs are traceable.

### UC-04: AI-Assisted Validation Authoring
Preconditions:
- User has chatbot feature entitlement.
Main flow:
1. User requests validation setup in natural language.
2. AI service proposes configuration mapped to allowed tools and data scope.
3. User approves and saves draft template.
Postconditions:
- Draft template is available for review/execution.

## 22. Acceptance Criteria
- AC-001: User authentication through approved IdP succeeds for authorized users and fails for non-authorized users.
- AC-002: RBAC matrix enforcement prevents unauthorized connector creation and run submission.
- AC-003: Standard check pack executes and produces deterministic outputs for known test fixtures.
- AC-004: Regression check pack includes all required checks and reports deviations accurately.
- AC-005: Failed connector authentication returns classified error with remediation guidance.
- AC-006: Scheduled job triggers execute at configured time windows and honor blackout policies.
- AC-007: Result exports are downloadable in CSV, JSON, HTML, and PDF.
- AC-008: Audit logs contain required event metadata and are queryable by authorized auditor.
- AC-009: DR simulation demonstrates recovery within target RPO/RTO envelopes.
- AC-010: Dashboard role-based views hide unauthorized projects and tenant data.

## 23. Data Validation Workflows
Workflow DV-01: Source-Target Reconciliation
1. Resolve project, template, source/target references.
2. Validate permissions and entitlements.
3. Perform metadata/schema introspection.
4. Execute standard and optional regression packs.
5. Aggregate summary and detailed outcomes.
6. Publish reports, notifications, and audit events.

Workflow DV-02: Anomaly and GE Rule Validation
1. Load profile/expectation packs.
2. Execute anomaly detection and GE validations.
3. Consolidate findings into run outcomes.
4. Store and surface explainable diagnostics.

## 24. API Workflows
Workflow API-01: Run Submission
1. Client submits POST run request with idempotency key.
2. API validates token, role, scope, and payload schema.
3. API persists run request and emits queue event.
4. API returns accepted status with correlation identifiers.

Workflow API-02: Live Run Monitoring
1. Client subscribes via WebSocket/SSE.
2. System streams state transitions and progress events.
3. Client queries details endpoint for artifacts/results when complete.

## 25. File Validation Workflows
Workflow FILE-01: Batch File Comparison
1. User configures source and target file locations and formats.
2. Connector runtime performs read and schema extraction.
3. Validation engine executes configured checks.
4. Results are persisted and downloadable.

Workflow FILE-02: Object Storage Validation
1. User configures cloud object store references.
2. System applies access policy checks and optional prefix filters.
3. Validation runs and publishes outcomes.

## 26. Database Validation Workflows
Workflow DB-01: Table-to-Table Validation
1. User selects source and target tables.
2. Connector runtime performs metadata introspection and pushdown where possible.
3. Engine executes selected checks and reconciliation.
4. System stores row/column/check summaries.

Workflow DB-02: Incremental Partition Validation
1. User selects partition/time-window predicate.
2. System executes constrained validation for selected window.
3. Outcomes are compared against historical baseline.

## 27. Cloud Validation Workflows
Workflow CLD-01: Cross-Cloud Data Validation
1. User configures cloud endpoints and credentials via secret references.
2. System validates network policy and access scopes.
3. Engine performs validation using approved connector capabilities.
4. System stores results with cloud-context metadata.

Workflow CLD-02: Lakehouse Dataset Validation
1. User selects dataset paths/tables in lakehouse environment.
2. System evaluates schema/partition metadata.
3. Engine runs checks and emits summary trend metrics.

## 28. AI Chatbot Workflows
Workflow AI-01: Conversational Run Design
1. User provides natural-language intent.
2. AI service maps intent to template draft using allowed resources.
3. User reviews and confirms configuration.
4. System stores draft and optional execution trigger.

Workflow AI-02: Conversational Failure Analysis
1. User asks why validation failed.
2. AI service retrieves run diagnostics and logs within tenant scope.
3. AI returns probable cause, impacted fields, and remediation steps.
4. Session transcript is saved under tenant policy.

## 29. Reporting Workflows
Workflow RPT-01: Operational Dashboard
1. User selects org/team/project filters.
2. Dashboard service retrieves authorized summary metrics.
3. User drills into failed checks and exports report.

Workflow RPT-02: Scheduled Executive Report
1. Admin defines recurring report schedule and recipients.
2. System compiles KPI snapshot and trend charts.
3. Report artifact is delivered and archived.

## 30. Team Management Workflows
Workflow TM-01: Team Provisioning
1. Org Admin creates team and assigns Team Admin.
2. Team Admin invites users and assigns roles.
3. System enforces policy and records audit events.

Workflow TM-02: Access Escalation and Revocation
1. User requests elevated role.
2. Admin approves/rejects request.
3. System applies role changes with effective timestamps.
4. Audit event is recorded and visible to Auditor.

## 31. RBAC Matrix
| Role | Org Mgmt | Team Mgmt | Project Config | Connector Mgmt | Run Validation | Schedule | View Reports | Export Reports | Audit Access | License Mgmt |
|---|---|---|---|---|---|---|---|---|---|---|
| Super Admin | Full | Full | Full | Full | Full | Full | Full | Full | Full | Full |
| Org Admin | Full (org scope) | Full (org scope) | Full (org scope) | Full (org scope) | Full (org scope) | Full (org scope) | Full (org scope) | Full (org scope) | Read (org scope) | Full (org scope) |
| Team Admin | None | Full (team scope) | Full (team scope) | Approve/manage (team scope) | Full (team scope) | Full (team scope) | Full (team scope) | Full (team scope) | None | None |
| Architect | None | None | Create/Update (project scope) | Create/Test (project scope) | Full (project scope) | Create/Manage (project scope) | Full (project scope) | Full (project scope) | None | None |
| Tester | None | None | Read/Execute (project scope) | Read/Test (assigned) | Full (assigned scope) | Limited (assigned scope) | Full (assigned scope) | Limited (assigned scope) | None | None |
| Auditor | None | None | Read (authorized scope) | None | None | None | Read (authorized scope) | Read (authorized scope) | Full (authorized scope) | None |
| Viewer | None | None | Read (authorized scope) | None | None | None | Read (authorized scope) | None | None | None |

## 32. Admin Operations
- AO-001: Configure SSO and MFA policy.
- AO-002: Create and manage organizations, teams, and user lifecycle.
- AO-003: Define role mappings, policy constraints, and entitlement boundaries.
- AO-004: Configure retention, backup, and disaster recovery policies.
- AO-005: Manage license subscriptions and feature packages.
- AO-006: Review audit reports and security posture dashboards.

## 33. User Operations
- UO-001: Create projects and folders within authorized scope.
- UO-002: Register source and target connections using secret references.
- UO-003: Create validation templates and execute runs.
- UO-004: Monitor run status and inspect diagnostics.
- UO-005: Export reports and share run summaries.
- UO-006: Use chatbot for guided setup and troubleshooting where entitled.

## 34. Licensing Model
License tiers aligned to approved architecture:
- Community Tier:
  - Core validations
  - Limited connectors
  - Basic dashboard and exports
- Professional Tier:
  - Advanced connectors
  - Scheduling and notifications
  - Team workflows and richer reporting
- Enterprise Tier:
  - SSO/MFA and advanced RBAC
  - Audit/compliance package
  - DR/HA options and private deployment support
  - Advanced AI capabilities and governance controls

Licensing dimensions:
- Active users
- Project count
- Run volume
- Data volume processed
- AI usage credits

## 35. Future Enhancements
- FE-001: Marketplace extension for connectors and validator packs.
- FE-002: Autonomous remediation recommendation workflows.
- FE-003: Cost governance and optimization advisor.
- FE-004: Expanded cross-tenant benchmarking with privacy preservation.
- FE-005: Edge/hybrid execution support.
- FE-006: Enhanced policy simulation and what-if access analysis.

## 36. Traceability Matrix (High-Level)
| Business Goal | Primary Functional Coverage | Primary NFR Coverage |
|---|---|---|
| BG-01 Cycle-time reduction | FR-016..FR-028, FR-037..FR-039 | NFR-004, PR-002, PR-004 |
| BG-02 Defect prevention | FR-017..FR-020, FR-024 | NFR-005, PR-005 |
| BG-03 Enterprise onboarding | FR-001..FR-006, FR-033..FR-036 | NFR-002, NFR-003 |
| BG-04 Security and governance | FR-001..FR-006, FR-036 | SEC-001..SEC-009, AUD-001..AUD-004 |
| BG-05 API and UI operations | FR-007..FR-010, FR-037..FR-040 | PR-001, PR-003 |
| BG-06 Commercial readiness | FR-035, AO-005 | NFR-001, CMP-001..CMP-004 |

## 37. Assumptions and Constraints
- The architecture baseline from SOFTWARE_ARCHITECTURE_DOCUMENT.md v1.0 is approved and immutable for this SRS version.
- Connector capabilities vary by provider; unsupported operations SHALL return capability-aware responses.
- Deployment profiles MAY choose queue/message implementation (RabbitMQ or Kafka) and worker orchestration implementation within approved stack.
- Tenant-specific regulatory obligations SHALL be configured through policy and retention controls.

## 38. Quality Assurance and Verification Strategy
- Unit, integration, contract, performance, and security testing SHALL be defined for all critical paths.
- Role-based and tenant-isolation tests SHALL be mandatory in release gates.
- DR runbook test evidence SHALL be required for major release milestones.
- API compatibility validation SHALL be required for version increments.

## 39. Appendix A: Validation Check Catalog
Mandatory check catalog supported by the platform:
1. Record Count
2. Column Count
3. Metadata Types Compatibility
4. Duplicate Detection
5. Null Analysis
6. Empty String Detection
7. Data Value Comparison
8. Column Order
9. Precision/Scale/Length
10. Distinct Values
11. Date Range (MIN/MAX)
12. Case Sensitivity
13. Leading Zeros
14. Special Characters
15. Row Checksums
16. Symmetric Difference
17. Anomaly Detection (Isolation Forest style)
18. Great Expectations rule pack execution

## 40. Appendix B: Primary State Models
Run state model:
- queued -> running -> succeeded
- queued -> running -> failed
- queued -> running -> canceled
- queued -> running -> timed_out

Schedule state model:
- active, paused, disabled, deleted

Connection health state model:
- unverified, healthy, degraded, failed, disabled

## 41. Approval
This SRS is approved for implementation planning and detailed sprint decomposition, subject to architecture governance controls and change management process.