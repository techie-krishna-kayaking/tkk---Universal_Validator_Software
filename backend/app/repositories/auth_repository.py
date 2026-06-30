from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from app.models.auth import (
    AuthSession,
    AuthUser,
    EmailVerificationToken,
    LoginAuditEvent,
    MfaFactor,
    PasswordResetToken,
    RefreshTokenRecord,
    SecurityAuditEvent,
    TrustedDevice,
)


@dataclass
class InMemoryAuthRepository:
    users: dict[str, AuthUser] = field(default_factory=dict)
    users_by_email: dict[str, str] = field(default_factory=dict)
    sessions: dict[str, AuthSession] = field(default_factory=dict)
    refresh_tokens: dict[str, RefreshTokenRecord] = field(default_factory=dict)
    password_resets: dict[str, PasswordResetToken] = field(default_factory=dict)
    email_verifications: dict[str, EmailVerificationToken] = field(default_factory=dict)
    mfa_factors: dict[str, MfaFactor] = field(default_factory=dict)
    trusted_devices: dict[str, TrustedDevice] = field(default_factory=dict)
    login_audit: list[LoginAuditEvent] = field(default_factory=list)
    security_audit: list[SecurityAuditEvent] = field(default_factory=list)

    def create_user(self, user: AuthUser) -> AuthUser:
        if not user.id:
            user.id = str(uuid4())
        self.users[user.id] = user
        self.users_by_email[user.email.lower()] = user.id
        return user

    def get_user_by_email(self, email: str) -> AuthUser | None:
        user_id = self.users_by_email.get(email.lower())
        if not user_id:
            return None
        return self.users.get(user_id)

    def get_user_by_id(self, user_id: str) -> AuthUser | None:
        return self.users.get(user_id)

    def update_user(self, user: AuthUser) -> AuthUser:
        user.updated_at = datetime.now(UTC)
        self.users[user.id] = user
        return user

    def create_session(self, session: AuthSession) -> AuthSession:
        if not session.id:
            session.id = str(uuid4())
        self.sessions[session.id] = session
        return session

    def get_session(self, session_id: str) -> AuthSession | None:
        return self.sessions.get(session_id)

    def store_refresh_token(self, token: RefreshTokenRecord) -> None:
        if not token.id:
            token.id = str(uuid4())
        self.refresh_tokens[token.token_hash] = token

    def get_refresh_token(self, token_hash: str) -> RefreshTokenRecord | None:
        return self.refresh_tokens.get(token_hash)

    def save_password_reset(self, record: PasswordResetToken) -> None:
        if not record.id:
            record.id = str(uuid4())
        self.password_resets[record.token_hash] = record

    def get_password_reset(self, token_hash: str) -> PasswordResetToken | None:
        return self.password_resets.get(token_hash)

    def save_email_verification(self, record: EmailVerificationToken) -> None:
        if not record.id:
            record.id = str(uuid4())
        self.email_verifications[record.token_hash] = record

    def get_email_verification(self, token_hash: str) -> EmailVerificationToken | None:
        return self.email_verifications.get(token_hash)

    def upsert_mfa_factor(self, factor: MfaFactor) -> None:
        if not factor.id:
            factor.id = str(uuid4())
        self.mfa_factors[factor.user_id] = factor

    def get_mfa_factor(self, user_id: str) -> MfaFactor | None:
        return self.mfa_factors.get(user_id)

    def add_trusted_device(self, trusted: TrustedDevice) -> None:
        if not trusted.id:
            trusted.id = str(uuid4())
        self.trusted_devices[f"{trusted.user_id}:{trusted.device_fingerprint}"] = trusted

    def find_trusted_device(self, user_id: str, fingerprint: str) -> TrustedDevice | None:
        return self.trusted_devices.get(f"{user_id}:{fingerprint}")

    def add_login_audit(self, event: LoginAuditEvent) -> None:
        if not event.id:
            event.id = str(uuid4())
        self.login_audit.append(event)

    def add_security_audit(self, event: SecurityAuditEvent) -> None:
        if not event.id:
            event.id = str(uuid4())
        self.security_audit.append(event)
