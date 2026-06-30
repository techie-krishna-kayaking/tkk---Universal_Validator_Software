# Enterprise User Management Module

## Scope
This module implements organization, team, project, user membership, invitation, ownership transfer, and dynamic RBAC capabilities for admin UI APIs.

## Hierarchy
- Organization
- Team
- Project
- User Membership
- Role
- Permission

## Implemented Capabilities
- Organization CRUD
- Team CRUD
- Project CRUD
- Invite user and email outbox event generation
- Accept invitation
- Deactivate user membership
- Delete user membership
- Transfer ownership for organization/team/project
- Update organization/team/project settings
- Dynamic custom role creation and permission updates
- Feature-level permission evaluation
- Audit event tracking for all admin operations

## Default Roles
- platform_admin
- organization_admin
- architect
- developer
- qa_lead
- qa_engineer
- viewer
- guest

## Feature Permissions
- can_create_connections
- can_delete_connections
- can_run_validation
- can_view_reports
- can_download_reports
- can_configure_ai
- can_manage_secrets
- can_configure_schedulers

## Security
- Every admin endpoint is protected by bearer auth, tenant checks, and permission dependencies.
