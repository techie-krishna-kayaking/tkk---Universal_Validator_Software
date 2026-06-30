import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from enum import StrEnum

import jwt
import pyotp
from passlib.context import CryptContext

from app.config.settings import Settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def enforce_password_policy(password: str, settings: Settings) -> None:
    if len(password) < settings.password_min_length:
        raise ValueError(f"Password must be at least {settings.password_min_length} characters")

    if settings.password_require_upper and not any(ch.isupper() for ch in password):
        raise ValueError("Password must include an uppercase letter")
    if settings.password_require_lower and not any(ch.islower() for ch in password):
        raise ValueError("Password must include a lowercase letter")
    if settings.password_require_number and not any(ch.isdigit() for ch in password):
        raise ValueError("Password must include a number")
    if settings.password_require_special and not any(not ch.isalnum() for ch in password):
        raise ValueError("Password must include a special character")


def _encode_token(
    subject: str,
    token_type: TokenType,
    settings: Settings,
    expires_delta: timedelta,
    extra_claims: dict | None = None,
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": now,
        "nbf": now,
        "exp": now + expires_delta,
        "jti": secrets.token_urlsafe(24),
        "type": token_type.value,
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")


def create_access_token(subject: str, settings: Settings, claims: dict | None = None) -> str:
    return _encode_token(
        subject,
        TokenType.ACCESS,
        settings,
        timedelta(minutes=settings.jwt_access_token_expire_minutes),
        claims,
    )


def create_refresh_token(subject: str, settings: Settings, claims: dict | None = None) -> str:
    return _encode_token(
        subject,
        TokenType.REFRESH,
        settings,
        timedelta(days=settings.jwt_refresh_token_expire_days),
        claims,
    )


def create_password_reset_token(subject: str, settings: Settings) -> str:
    return _encode_token(subject, TokenType.PASSWORD_RESET, settings, timedelta(minutes=30))


def create_email_verification_token(subject: str, settings: Settings) -> str:
    return _encode_token(subject, TokenType.EMAIL_VERIFICATION, settings, timedelta(hours=24))


def decode_token(token: str, settings: Settings) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=["HS256"],
        audience=settings.jwt_audience,
        issuer=settings.jwt_issuer,
    )


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def new_totp_secret() -> str:
    return pyotp.random_base32()


def verify_totp_code(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return bool(totp.verify(code, valid_window=1))


def generate_recovery_codes(count: int = 10) -> list[str]:
    return [secrets.token_hex(6) for _ in range(count)]
