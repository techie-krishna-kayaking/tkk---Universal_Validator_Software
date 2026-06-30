from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field


class OAuthProvider(StrEnum):
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    AZURE_AD = "azure_ad"
    OKTA = "okta"
    OPENID_CONNECT = "openid_connect"
    LDAP = "ldap"
    SAML = "saml"


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    tenant_id: str = Field(min_length=2)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    tenant_id: str
    remember_me: bool = False
    device_id: str | None = None
    mfa_code: str | None = None


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr
    tenant_id: str


class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str


class EmailVerificationRequest(BaseModel):
    token: str


class MfaSetupResponse(BaseModel):
    secret: str
    otpauth_url: str


class MfaVerifyRequest(BaseModel):
    code: str


class OAuthAuthorizeResponse(BaseModel):
    provider: OAuthProvider
    authorization_url: str


class OAuthCallbackRequest(BaseModel):
    provider: OAuthProvider
    code: str
    state: str
    tenant_id: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    session_id: str
    mfa_required: bool = False


class SessionInfo(BaseModel):
    user_id: str
    session_id: str
    tenant_id: str
    role: str
    permissions: list[str]


class LogoutRequest(BaseModel):
    refresh_token: str


class FeatureAuthorizationRequest(BaseModel):
    feature: str


class AuthorizationDecision(BaseModel):
    allowed: bool
    reason: str | None = None
