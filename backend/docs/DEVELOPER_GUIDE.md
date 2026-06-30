# Developer Guide - Backend Foundation, Authentication, and Configuration Management

## Objective
This backend now includes enterprise authentication, security baseline capabilities, and enterprise configuration management.

## Local Setup
1. Install Poetry.
2. Run poetry install.
3. Copy .env.example to .env.
4. Start service with poetry run backend-api.

## Key Modules
- app/core/application.py: application factory and middleware wiring.
- app/config/settings.py: profiles and security settings.
- app/services/auth_service.py: authentication lifecycle service.
- app/services/federated_auth_service.py: OAuth/OIDC provider hooks.
- app/dependencies/auth.py: principal extraction and authorization dependencies.
- app/api/v1/auth.py: authentication and authorization APIs.
- app/services/config_service.py: encrypted configuration and secret lifecycle service.
- app/repositories/config_repository.py: in-memory configuration repository and source snapshots.
- app/api/v1/config_mgmt.py: admin configuration management APIs.
- app/connectors/base.py: common connector interface and operation contract.
- app/connectors/registry.py: plugin registration and connector spec lookup.
- app/connectors/loader.py: plugin discovery from packages, paths, and entry points.
- app/connectors/factory.py: connector creation façade and discovery orchestration.
- app/connectors/pipeline.py: dependency-aware parallel connector operation pipelines with retries.
- app/validators/base.py: common validator interface and execution contract.
- app/validators/registry.py: validator plugin registration and lookup.
- app/validators/loader.py: validator plugin discovery from packages, paths, and entry points.
- app/validators/factory.py: validator creation façade and discovery orchestration.
- app/validators/pipeline.py: dependency-aware parallel validation pipelines with retries and templates.
- app/execution/engines.py: Pandas/PySpark/Polars/DuckDB execution adapters.
- app/execution/selector.py: dynamic engine selection logic based on workload profile.
- app/execution/orchestrator.py: automatic fallback orchestration across engine candidates.
- app/services/execution_service.py: service facade for execution engine usage.

## Testing
- Unit tests: tests/unit
- Integration tests: tests/integration

## Notes
- No UI is included.
- This milestone focuses on backend auth and security controls.
