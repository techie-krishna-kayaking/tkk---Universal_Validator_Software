# Swagger and OpenAPI - Authentication Module

## OpenAPI Scope
The authentication module extends API documentation with enterprise auth routes under:
- /api/v1/auth/*
- /api/v1/health*

## Security in OpenAPI
- Bearer token authentication is implemented through HTTP bearer scheme dependencies.
- Protected endpoints require Authorization and X-Tenant-ID headers.

## Auth Endpoint Groups
- auth-public:
  - register
  - login
  - refresh
  - forgot-password
  - reset-password
  - verify-email
  - oauth authorize and callback
- auth-protected:
  - logout
  - session
  - mfa setup and verify
  - feature authorization decision
  - rbac probe

## Swagger Usage
1. Obtain access token using /api/v1/auth/login.
2. Use Authorize button with Bearer token.
3. Pass X-Tenant-ID header for tenant-authorized routes.
