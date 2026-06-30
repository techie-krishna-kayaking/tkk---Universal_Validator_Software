import pytest

from app.config.settings import Settings
from app.core.security import (
    create_access_token,
    decode_token,
    enforce_password_policy,
    hash_password,
    verify_password,
)


def test_password_policy_enforced() -> None:
    settings = Settings(PASSWORD_MIN_LENGTH=12)
    enforce_password_policy("ValidPass#123", settings)

    with pytest.raises(ValueError):
        enforce_password_policy("short1#A", settings)


def test_password_hashing_round_trip() -> None:
    hashed = hash_password("ValidPass#123")
    assert verify_password("ValidPass#123", hashed)


def test_access_token_round_trip() -> None:
    settings = Settings(JWT_SECRET_KEY="unit-test-secret-key-32-characters!")
    token = create_access_token("user-id", settings, claims={"tenant_id": "tenant-a"})
    payload = decode_token(token, settings)
    assert payload["sub"] == "user-id"
    assert payload["tenant_id"] == "tenant-a"
