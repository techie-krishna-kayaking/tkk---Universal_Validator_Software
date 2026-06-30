from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.config.settings import Settings
from app.core.security import (
    create_access_token,
    create_email_verification_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
    enforce_password_policy,
    generate_recovery_codes,
    hash_password,
    hash_token,
    new_totp_secret,
    verify_password,
    verify_totp_code,
)
from app.exceptions.custom import ApiError
from app.models.auth import (
    AuthSession,
    AuthUser,
    EmailVerificationToken,
    LoginAuditEvent,
    MfaFactor,
    PasswordResetToken,
    RefreshTokenRecord,
    SecurityAuditEvent,
    SecurityEventType,
    SessionStatus,
    TrustedDevice,
)
from app.models.user_mgmt import DEFAULT_ROLES
from app.repositories.auth_repository import InMemoryAuthRepository
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest, SessionInfo


class AuthService:
    def __init__(self, settings: Settings, repository: InMemoryAuthRepository) -> None:
        self.settings = settings
        self.repository = repository

    def register_user(self, payload: RegisterRequest) -> SessionInfo:
        existing = self.repository.get_user_by_email(payload.email)
        if existing:
            raise ApiError(code="email_exists", message="Email already registered", status_code=409)

        enforce_password_policy(payload.password, self.settings)

        user = AuthUser(
            tenant_id=payload.tenant_id,
            email=payload.email.lower(),
            hashed_password=hash_password(payload.password),
            is_active=True,
            is_email_verified=False,
            failed_login_attempts=0,
            locked_until=None,
            role="viewer",
            permissions=DEFAULT_ROLES["viewer"],
        )
        self.repository.create_user(user)

        verification_token = create_email_verification_token(user.id, self.settings)
        verification_record = EmailVerificationToken(
            user_id=user.id,
            token_hash=hash_token(verification_token),
            expires_at=datetime.now(UTC) + timedelta(hours=24),
        )
        self.repository.save_email_verification(verification_record)

        self.repository.add_security_audit(
            SecurityAuditEvent(
                user_id=user.id,
                tenant_id=user.tenant_id,
                action="register_user",
                resource="auth_user",
                outcome="success",
                details={"email": user.email},
            )
        )
        return SessionInfo(
            user_id=user.id,
            session_id="",
            tenant_id=user.tenant_id,
            role=user.role,
            permissions=user.permissions,
        )

    def login(
        self,
        payload: LoginRequest,
        ip_address: str | None,
        user_agent: str | None,
        geo_country: str | None,
    ) -> LoginResponse:
        user = self.repository.get_user_by_email(payload.email)
        if not user:
            self._audit_login(payload.email, None, payload.tenant_id, False, ip_address, user_agent, geo_country)
            raise ApiError(code="invalid_credentials", message="Invalid credentials", status_code=401)

        if user.tenant_id != payload.tenant_id:
            raise ApiError(code="tenant_mismatch", message="Tenant authorization failed", status_code=403)

        if not user.is_active:
            raise ApiError(code="account_disabled", message="Account is disabled", status_code=403)

        if user.locked_until and user.locked_until > datetime.now(UTC).replace(tzinfo=None):
            raise ApiError(code="account_locked", message="Account temporarily locked", status_code=423)

        if not verify_password(payload.password, user.hashed_password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= self.settings.max_failed_login_attempts:
                user.locked_until = datetime.now(UTC).replace(tzinfo=None) + timedelta(
                    minutes=self.settings.account_lockout_minutes
                )
                self.repository.add_security_audit(
                    SecurityAuditEvent(
                        user_id=user.id,
                        tenant_id=user.tenant_id,
                        action=SecurityEventType.LOCKOUT.value,
                        resource="auth_user",
                        outcome="success",
                        details={"email": user.email},
                    )
                )
            self.repository.update_user(user)
            self._audit_login(user.email, user.id, user.tenant_id, False, ip_address, user_agent, geo_country)
            raise ApiError(code="invalid_credentials", message="Invalid credentials", status_code=401)

        mfa_factor = self.repository.get_mfa_factor(user.id)
        if mfa_factor and mfa_factor.is_enabled:
            trusted = False
            if payload.device_id:
                trusted_device = self.repository.find_trusted_device(user.id, payload.device_id)
                trusted = bool(trusted_device and trusted_device.is_active)
            if not trusted:
                if not payload.mfa_code or not verify_totp_code(mfa_factor.secret_encrypted, payload.mfa_code):
                    self.repository.add_security_audit(
                        SecurityAuditEvent(
                            user_id=user.id,
                            tenant_id=user.tenant_id,
                            action=SecurityEventType.MFA_CHALLENGE.value,
                            resource="mfa",
                            outcome="failed",
                            details={"email": user.email},
                        )
                    )
                    raise ApiError(code="mfa_required", message="Valid MFA code is required", status_code=401)

        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now(UTC).replace(tzinfo=None)
        user.last_login_ip = ip_address
        self.repository.update_user(user)

        session = AuthSession(
            user_id=user.id,
            tenant_id=user.tenant_id,
            status=SessionStatus.ACTIVE.value,
            remember_me=payload.remember_me,
            trusted_browser=bool(payload.device_id),
            device_id=payload.device_id,
            user_agent=user_agent,
            ip_address=ip_address,
            geo_country=geo_country,
            expires_at=datetime.now(UTC).replace(tzinfo=None)
            + timedelta(days=self.settings.jwt_refresh_token_expire_days),
        )
        self.repository.create_session(session)

        claims = {
            "sid": session.id,
            "tenant_id": user.tenant_id,
            "role": user.role,
            "permissions": user.permissions,
            "email_verified": user.is_email_verified,
        }
        access_token = create_access_token(user.id, self.settings, claims=claims)
        refresh_token = create_refresh_token(user.id, self.settings, claims={"sid": session.id})
        self.repository.store_refresh_token(
            RefreshTokenRecord(
                session_id=session.id,
                token_hash=hash_token(refresh_token),
                expires_at=datetime.now(UTC).replace(tzinfo=None)
                + timedelta(days=self.settings.jwt_refresh_token_expire_days),
            )
        )

        if payload.device_id:
            self.repository.add_trusted_device(
                TrustedDevice(
                    user_id=user.id,
                    device_fingerprint=payload.device_id,
                    label="trusted_browser",
                )
            )

        self._audit_login(user.email, user.id, user.tenant_id, True, ip_address, user_agent, geo_country)

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in_seconds=self.settings.jwt_access_token_expire_minutes * 60,
            session_id=session.id,
            mfa_required=False,
        )

    def refresh(self, refresh_token: str) -> LoginResponse:
        payload = decode_token(refresh_token, self.settings)
        if payload.get("type") != "refresh":
            raise ApiError(code="invalid_token", message="Token type is not refresh", status_code=401)

        hashed = hash_token(refresh_token)
        token_record = self.repository.get_refresh_token(hashed)
        if not token_record or token_record.is_revoked:
            raise ApiError(code="revoked_token", message="Refresh token revoked", status_code=401)

        user_id = payload.get("sub")
        session_id = payload.get("sid")
        user = self.repository.get_user_by_id(user_id)
        session = self.repository.get_session(session_id)
        if not user or not session or session.status != SessionStatus.ACTIVE.value:
            raise ApiError(code="invalid_session", message="Session invalid", status_code=401)

        claims = {
            "sid": session.id,
            "tenant_id": user.tenant_id,
            "role": user.role,
            "permissions": user.permissions,
            "email_verified": user.is_email_verified,
        }
        access_token = create_access_token(user.id, self.settings, claims=claims)
        new_refresh_token = create_refresh_token(user.id, self.settings, claims={"sid": session.id})
        token_record.is_revoked = True
        self.repository.store_refresh_token(
            RefreshTokenRecord(
                session_id=session.id,
                token_hash=hash_token(new_refresh_token),
                expires_at=datetime.now(UTC).replace(tzinfo=None)
                + timedelta(days=self.settings.jwt_refresh_token_expire_days),
            )
        )

        self.repository.add_security_audit(
            SecurityAuditEvent(
                user_id=user.id,
                tenant_id=user.tenant_id,
                action=SecurityEventType.TOKEN_REFRESH.value,
                resource="refresh_token",
                outcome="success",
                details={"session_id": session.id},
            )
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in_seconds=self.settings.jwt_access_token_expire_minutes * 60,
            session_id=session.id,
        )

    def logout(self, refresh_token: str) -> None:
        hashed = hash_token(refresh_token)
        token_record = self.repository.get_refresh_token(hashed)
        if token_record:
            token_record.is_revoked = True

    def forgot_password(self, email: str, tenant_id: str) -> str:
        user = self.repository.get_user_by_email(email)
        if not user or user.tenant_id != tenant_id:
            return "If an account exists, reset instructions were generated"

        reset_token = create_password_reset_token(user.id, self.settings)
        self.repository.save_password_reset(
            PasswordResetToken(
                user_id=user.id,
                token_hash=hash_token(reset_token),
                expires_at=datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=30),
            )
        )
        return reset_token

    def reset_password(self, token: str, new_password: str) -> None:
        enforce_password_policy(new_password, self.settings)
        payload = decode_token(token, self.settings)
        if payload.get("type") != "password_reset":
            raise ApiError(code="invalid_token_type", message="Wrong token type", status_code=401)

        hashed = hash_token(token)
        record = self.repository.get_password_reset(hashed)
        if not record or record.is_used:
            raise ApiError(code="invalid_reset_token", message="Invalid or used reset token", status_code=401)

        user = self.repository.get_user_by_id(payload["sub"])
        if not user:
            raise ApiError(code="user_not_found", message="User not found", status_code=404)

        user.hashed_password = hash_password(new_password)
        self.repository.update_user(user)
        record.is_used = True

    def verify_email(self, token: str) -> None:
        payload = decode_token(token, self.settings)
        if payload.get("type") != "email_verification":
            raise ApiError(code="invalid_token_type", message="Wrong token type", status_code=401)

        hashed = hash_token(token)
        record = self.repository.get_email_verification(hashed)
        if not record or record.is_used:
            raise ApiError(code="invalid_verification_token", message="Invalid or used token", status_code=401)

        user = self.repository.get_user_by_id(payload["sub"])
        if not user:
            raise ApiError(code="user_not_found", message="User not found", status_code=404)

        user.is_email_verified = True
        self.repository.update_user(user)
        record.is_used = True

    def setup_mfa(self, user_id: str, provider: str = "google_authenticator") -> tuple[str, list[str]]:
        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise ApiError(code="user_not_found", message="User not found", status_code=404)

        secret = new_totp_secret()
        factor = MfaFactor(user_id=user.id, provider=provider, secret_encrypted=secret, is_enabled=False)
        self.repository.upsert_mfa_factor(factor)
        recovery_codes = generate_recovery_codes()
        return secret, recovery_codes

    def enable_mfa(self, user_id: str, code: str) -> None:
        factor = self.repository.get_mfa_factor(user_id)
        if not factor:
            raise ApiError(code="mfa_not_initialized", message="MFA not initialized", status_code=400)

        if not verify_totp_code(factor.secret_encrypted, code):
            raise ApiError(code="invalid_mfa_code", message="Invalid MFA code", status_code=401)

        factor.is_enabled = True
        self.repository.upsert_mfa_factor(factor)

    def authorize_feature(self, user: AuthUser, feature: str) -> bool:
        if user.role in {"platform_admin", "organization_admin"}:
            return True
        return feature in set(user.permissions)

    def get_session_info_from_access_token(self, token: str) -> SessionInfo:
        payload = decode_token(token, self.settings)
        if payload.get("type") != "access":
            raise ApiError(code="invalid_access_token", message="Wrong token type", status_code=401)

        user_id = payload["sub"]
        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise ApiError(code="user_not_found", message="User not found", status_code=404)

        return SessionInfo(
            user_id=user.id,
            session_id=payload.get("sid", ""),
            tenant_id=payload.get("tenant_id", ""),
            role=payload.get("role", user.role),
            permissions=payload.get("permissions", user.permissions),
        )

    def _audit_login(
        self,
        email: str,
        user_id: str | None,
        tenant_id: str | None,
        success: bool,
        ip_address: str | None,
        user_agent: str | None,
        geo_country: str | None,
    ) -> None:
        suspicious = bool(not success and geo_country and geo_country not in {"US", "CA", "IN", "GB"})
        event_type = SecurityEventType.LOGIN_SUCCESS.value if success else SecurityEventType.LOGIN_FAILURE.value
        if suspicious:
            event_type = SecurityEventType.SUSPICIOUS_LOGIN.value

        self.repository.add_login_audit(
            LoginAuditEvent(
                user_id=user_id,
                tenant_id=tenant_id,
                email=email,
                event_type=event_type,
                ip_address=ip_address,
                user_agent=user_agent,
                geo_country=geo_country,
                is_suspicious=suspicious,
                details={"success": success},
            )
        )
