#!/usr/bin/env python3
"""
Demo environment seeder for tkk-UniversalValidator.

Seeds the running backend API with:
- Demo organization: TKK Technologies Pvt Ltd
- Demo team:         Data Engineering Team
- Demo users:        admin, architect, qalead, tester, viewer
- Demo projects:     AMEX-DM-001, SNOW-VAL-001

Usage:
    python scripts/demo/seed_demo_data.py
    BASE_URL=http://localhost:8000 python scripts/demo/seed_demo_data.py
"""
import os
import sys

import httpx

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
API_PREFIX = "/api/v1"
TENANT_ID = "TKK-ORG-001"

DEMO_USERS = [
    {"username": "admin",     "email": "admin@tkkvalidator.local",       "password": "Admin@123",      "role": "platform_admin"},
    {"username": "architect", "email": "architect@tkkvalidator.local",   "password": "Architect@123",  "role": "architect"},
    {"username": "qalead",    "email": "qalead@tkkvalidator.local",      "password": "QALead@123",     "role": "qa_lead"},
    {"username": "tester",    "email": "tester@tkkvalidator.local",      "password": "Tester@123",     "role": "qa_engineer"},
    {"username": "viewer",    "email": "viewer@tkkvalidator.local",      "password": "Viewer@123",     "role": "viewer"},
    {"username": "dataengineer", "email": "dataengineer@tkkvalidator.local", "password": "Data@123",   "role": "architect"},
]

DEMO_PROJECTS = [
    {"name": "American Express Data Migration",  "code": "AMEX-DM-001",  "description": "Customer and transaction data migration validation from Oracle to PostgreSQL"},
    {"name": "Snowflake Migration Validation",    "code": "SNOW-VAL-001", "description": "Product catalog and inventory migration validation to Snowflake"},
]


def _api(path: str) -> str:
    return f"{BASE_URL}{API_PREFIX}{path}"


def _print(msg: str) -> None:
    print(f"[seed] {msg}")


def register_users(client: httpx.Client) -> dict[str, str]:
    tokens: dict[str, str] = {}
    for user in DEMO_USERS:
        resp = client.post(
            _api("/auth/register"),
            json={"email": user["email"], "password": user["password"], "tenant_id": TENANT_ID},
        )
        if resp.status_code not in (201, 400, 409):
            _print(f"WARNING: register {user['email']} returned {resp.status_code}: {resp.text[:120]}")
            continue
        if resp.status_code == 201:
            _print(f"registered {user['email']}")
        else:
            _print(f"user already exists: {user['email']}")

        login_resp = client.post(
            _api("/auth/login"),
            json={"email": user["email"], "password": user["password"], "tenant_id": TENANT_ID},
            headers={"X-Geo-Country": "US"},
        )
        if login_resp.status_code == 200:
            tokens[user["username"]] = login_resp.json()["access_token"]
            _print(f"authenticated {user['username']}")
        else:
            _print(f"WARNING: login failed for {user['username']}: {login_resp.text[:120]}")

    return tokens


def create_organization(client: httpx.Client, admin_token: str) -> str | None:
    resp = client.post(
        _api("/admin/organizations"),
        json={
            "name": "TKK Technologies Pvt Ltd",
            "slug": "tkk-technologies",
            "settings": {"industry": "Financial Services", "region": "Global"},
        },
        headers={"Authorization": f"Bearer {admin_token}", "X-Tenant-ID": TENANT_ID},
    )
    if resp.status_code in (200, 201):
        org_id = resp.json().get("id")
        _print(f"created organization: TKK Technologies Pvt Ltd (id={org_id})")
        return org_id
    _print(f"organization create returned {resp.status_code} (may already exist): {resp.text[:120]}")
    return None


def create_team(client: httpx.Client, admin_token: str, org_id: str | None) -> str | None:
    payload: dict = {
        "name": "Data Engineering Team",
        "settings": {"slack_channel": "#data-engineering", "jira_project": "DE"},
    }
    if org_id:
        payload["organization_id"] = org_id

    resp = client.post(
        _api("/admin/teams"),
        json=payload,
        headers={"Authorization": f"Bearer {admin_token}", "X-Tenant-ID": TENANT_ID},
    )
    if resp.status_code in (200, 201):
        team_id = resp.json().get("id")
        _print(f"created team: Data Engineering Team (id={team_id})")
        return team_id
    _print(f"team create returned {resp.status_code}: {resp.text[:120]}")
    return None


def create_projects(client: httpx.Client, admin_token: str) -> None:
    for project in DEMO_PROJECTS:
        resp = client.post(
            _api("/admin/projects"),
            json={"name": project["name"], "code": project["code"], "description": project["description"]},
            headers={"Authorization": f"Bearer {admin_token}", "X-Tenant-ID": TENANT_ID},
        )
        if resp.status_code in (200, 201):
            _print(f"created project: {project['code']} — {project['name']}")
        else:
            _print(f"project {project['code']} returned {resp.status_code}: {resp.text[:120]}")


def check_backend(client: httpx.Client) -> bool:
    try:
        resp = client.get(f"{BASE_URL}/openapi.json", timeout=5)
        return resp.status_code == 200
    except Exception as exc:
        _print(f"backend not reachable at {BASE_URL}: {exc}")
        return False


def main() -> None:
    _print(f"connecting to {BASE_URL}")

    with httpx.Client(timeout=15) as client:
        if not check_backend(client):
            _print("ERROR: backend is not running. Start it with: poetry run backend-api")
            sys.exit(1)

        _print("seeding demo users")
        tokens = register_users(client)

        admin_token = tokens.get("admin")
        if not admin_token:
            _print("ERROR: could not authenticate as admin. Aborting.")
            sys.exit(1)

        _print("seeding demo organization")
        org_id = create_organization(client, admin_token)

        _print("seeding demo team")
        create_team(client, admin_token, org_id)

        _print("seeding demo projects")
        create_projects(client, admin_token)

    _print("")
    _print("Demo seed complete.")
    _print("Login at http://localhost:8000/docs or http://localhost:5173")
    _print("")
    _print("  Platform Admin :  admin@tkkvalidator.local  /  Admin@123")
    _print("  Architect      :  architect@tkkvalidator.local  /  Architect@123")
    _print("  QA Lead        :  qalead@tkkvalidator.local  /  QALead@123")
    _print("  QA Engineer    :  tester@tkkvalidator.local  /  Tester@123")
    _print("  Viewer         :  viewer@tkkvalidator.local  /  Viewer@123")


if __name__ == "__main__":
    main()
