# Enterprise Configuration Management

## Overview
The enterprise configuration management module provides encrypted secret storage, credential lifecycle controls, source reload, and auditability for runtime connections.

## Supported Configuration Sources
- .env
- YAML
- Environment Variables
- AWS Secrets Manager (blob adapter)
- Azure Key Vault (blob adapter)
- Google Secret Manager (blob adapter)
- HashiCorp Vault (future-ready blob adapter)

## Security Controls
- Every credential value is encrypted before repository storage.
- Credentials are masked in all API responses.
- Secret rotation updates credential versions and records audit events.
- Secret caching uses TTL-based in-memory cache and version-aware invalidation.

## Supported Connection Types
- Database Connections
- Cloud Connections
- API Connections
- File Connections
- Storage Connections
- SMTP
- Slack
- Microsoft Teams
- LLM Providers
- Notification Settings

## Dynamic Reload
The reload API pulls current source payloads from configured adapters and persists source snapshots with revision numbers.

## Settings
- CONFIG_ENCRYPTION_KEY
- SECRET_CACHE_TTL_SECONDS
- CONFIG_ENV_PREFIX
- DOTENV_SOURCE_PATH
- YAML_SOURCE_PATH
- AWS_SECRETS_MANAGER_BLOB
- AZURE_KEY_VAULT_BLOB
- GOOGLE_SECRET_MANAGER_BLOB
- HASHICORP_VAULT_BLOB

## Rotation Hooks
Service-level rotation hooks are available through register_rotation_hook(callback) for integration with external automation.
