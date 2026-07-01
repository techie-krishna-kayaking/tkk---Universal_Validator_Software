"""Security-focused unit tests covering CSRF, rate limiting, RBAC, password policy, and security headers."""

import pytest
from fastapi.testclient import TestClient

from app.config.settings import Settings
from app.core.application import create_app
from app.core.security import (
    create_access_token,
    decode_token,
    enforce_password_policy,
    hash_password,
    verify_password,
)
from app.exceptions.custom import ApiError
from app.middleware.rate_limit_hook import InMemoryRateLimiter
from app.middleware.security_headers import SecurityHeadersMiddleware


# ── Password Policy ────────────────────────────────────────────────────────────

class TestPasswordPolicy:
    def test_rejects_short_password(self) -> None:
        settings = Settings(PASSWORD_MIN_LENGTH=12)
        with pytest.raises(ValueError, match="at least 12"):
            enforce_password_policy("Ab1!", settings)

    def test_rejects_missing_uppercase(self) -> None:
        settings = Settings(PASSWORD_REQUIRE_UPPER=True)
        with pytest.raises(ValueError, match="uppercase"):
            enforce_password_policy("abcdefgh1!", settings)

    def test_rejects_missing_digit(self) -> None:
        settings = Settings(PASSWORD_REQUIRE_NUMBER=True)
        with pytest.raises(ValueError, match="number"):
            enforce_password_policy("Abcdefghijk!", settings)

    def test_rejects_missing_special_char(self) -> None:
        settings = Settings(PASSWORD_REQUIRE_SPECIAL=True)
        with pytest.raises(ValueError, match="special"):
            enforce_password_policy("Abcdefgh1234", settings)

    def test_accepts_compliant_password(self) -> None:
        settings = Settings()
        # Should not raise
        enforce_password_policy("Secure#Pass99!", settings)


# ── Password Hashing ──────────────────────────────────────────────────────────

class TestPasswordHashing:
    def test_hash_is_not_plaintext(self) -> None:
        hashed = hash_password("MySecret#1")
        assert hashed != "MySecret#1"

    def test_verify_correct_password(self) -> None:
        hashed = hash_password("MySecret#1")
        assert verify_password("MySecret#1", hashed) is True

    def test_reject_wrong_password(self) -> None:
        hashed = hash_password("MySecret#1")
        assert verify_password("Wrong#Pass2", hashed) is False


# ── JWT ───────────────────────────────────────────────────────────────────────

class TestJWT:
    def test_decode_valid_token(self) -> None:
        settings = Settings()
        token = create_access_token("user-123", settings, {"tenant_id": "tenant-a"})
        payload = decode_token(token, settings)
        assert payload["sub"] == "user-123"
        assert payload["tenant_id"] == "tenant-a"

    def test_decode_fails_with_wrong_secret(self) -> None:
        import jwt as pyjwt

        settings = Settings(JWT_SECRET_KEY="real_secret_key_min_32_characters_long")
        token = create_access_token("user-123", settings)

        wrong_settings = Settings(JWT_SECRET_KEY="wrong_secret_key_min_32_characters__")
        with pytest.raises(pyjwt.exceptions.InvalidSignatureError):
            decode_token(token, wrong_settings)

    def test_token_contains_required_claims(self) -> None:
        settings = Settings()
        token = create_access_token("user-abc", settings)
        payload = decode_token(token, settings)
        for claim in ("sub", "iss", "aud", "iat", "exp", "jti", "type"):
            assert claim in payload, f"Missing claim: {claim}"


# ── Rate Limiter ──────────────────────────────────────────────────────────────

class TestRateLimiter:
    @pytest.mark.asyncio
    async def test_raises_after_limit_exceeded(self) -> None:
        from unittest.mock import MagicMock

        limiter = InMemoryRateLimiter(attempts=3, window_seconds=60)
        request = MagicMock()
        request.client.host = "10.0.0.1"
        request.url.path = "/api/v1/auth/login"

        for _ in range(3):
            await limiter.check(request)

        with pytest.raises(ApiError) as exc_info:
            await limiter.check(request)

        assert exc_info.value.status_code == 429

    @pytest.mark.asyncio
    async def test_does_not_limit_unprotected_paths(self) -> None:
        from unittest.mock import MagicMock

        limiter = InMemoryRateLimiter(attempts=2, window_seconds=60)
        request = MagicMock()
        request.client.host = "10.0.0.2"
        request.url.path = "/api/v1/health"

        for _ in range(10):
            await limiter.check(request)  # Should never raise


# ── Security Headers ──────────────────────────────────────────────────────────

REQUIRED_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}


class TestSecurityHeaders:
    def test_all_required_headers_present(self) -> None:
        app = create_app()
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/auth/login",
                json={"email": "any@example.com", "password": "x", "tenant_id": "t"},
            )
        for header, expected in REQUIRED_HEADERS.items():
            assert response.headers.get(header) == expected, (
                f"Missing or wrong header: {header}"
            )

    def test_csp_header_present(self) -> None:
        app = create_app()
        with TestClient(app) as client:
            response = client.get("/openapi.json")
        assert "Content-Security-Policy" in response.headers


# ── CSRF ──────────────────────────────────────────────────────────────────────

class TestCSRF:
    def test_rejects_post_without_csrf_header_when_session_cookie_present(self) -> None:
        app = create_app()
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/auth/logout",
                json={"refresh_token": "x"},
                cookies={"session_id": "fake-session"},
                headers={},  # no CSRF header
            )
        assert response.status_code == 403

    def test_accepts_post_when_csrf_header_and_cookie_match(self) -> None:
        app = create_app()
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/auth/logout",
                json={"refresh_token": "x"},
                cookies={"session_id": "fake-session", "csrf_token": "tok"},
                headers={"X-CSRF-Token": "tok", "Authorization": "Bearer invalid"},
            )
        # 401 or 422 means CSRF passed (JWT failed), not 403
        assert response.status_code in {401, 422}
