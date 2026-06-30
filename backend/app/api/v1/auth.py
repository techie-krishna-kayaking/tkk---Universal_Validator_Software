from fastapi import APIRouter, Depends, Header, Request, status

from app.dependencies.auth import get_auth_service, require_permission, require_tenant_access
from app.schemas.auth import (
    AuthorizationDecision,
    EmailVerificationRequest,
    FeatureAuthorizationRequest,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    MfaSetupResponse,
    MfaVerifyRequest,
    OAuthAuthorizeResponse,
    OAuthCallbackRequest,
    OAuthProvider,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    RegisterRequest,
    SessionInfo,
    TokenRefreshRequest,
)
from app.services.auth_service import AuthService
from app.services.federated_auth_service import FederatedAuthService
from app.utils.request_context import client_ip, geo_country, user_agent

public_router = APIRouter(prefix="/auth", tags=["auth-public"])
protected_router = APIRouter(prefix="/auth", tags=["auth-protected"], dependencies=[Depends(require_tenant_access)])


@public_router.post("/register", response_model=SessionInfo, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)) -> SessionInfo:
    return auth_service.register_user(payload)


@public_router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    return auth_service.login(
        payload,
        ip_address=client_ip(request),
        user_agent=user_agent(request),
        geo_country=geo_country(request),
    )


@public_router.post("/refresh", response_model=LoginResponse)
async def refresh(payload: TokenRefreshRequest, auth_service: AuthService = Depends(get_auth_service)) -> LoginResponse:
    return auth_service.refresh(payload.refresh_token)


@public_router.post("/forgot-password")
async def forgot_password(
    payload: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    token = auth_service.forgot_password(payload.email, payload.tenant_id)
    return {"message": "If an account exists, reset instructions were generated", "token": token}


@public_router.post("/reset-password")
async def reset_password(
    payload: PasswordResetConfirmRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    auth_service.reset_password(payload.token, payload.new_password)
    return {"message": "Password reset complete"}


@public_router.post("/verify-email")
async def verify_email(
    payload: EmailVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    auth_service.verify_email(payload.token)
    return {"message": "Email verification complete"}


@public_router.get("/oauth/{provider}/authorize", response_model=OAuthAuthorizeResponse)
async def oauth_authorize(
    provider: str,
    redirect_uri: str,
    state: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> OAuthAuthorizeResponse:
    federated = FederatedAuthService(auth_service.settings)
    provider_enum = OAuthProvider(provider)
    authorization_url = federated.authorization_url(provider=provider_enum, redirect_uri=redirect_uri, state=state)
    return OAuthAuthorizeResponse(provider=provider_enum, authorization_url=authorization_url)


@public_router.post("/oauth/callback", response_model=LoginResponse)
async def oauth_callback(
    payload: OAuthCallbackRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    synthetic_login = LoginRequest(
        email=f"{payload.provider.value}_user@federated.local",
        password="FederatedLogin!123",
        tenant_id=payload.tenant_id,
        remember_me=True,
    )
    existing = auth_service.repository.get_user_by_email(synthetic_login.email)
    if not existing:
        auth_service.register_user(
            RegisterRequest(
                email=synthetic_login.email,
                password=synthetic_login.password,
                tenant_id=payload.tenant_id,
            )
        )
    return auth_service.login(
        synthetic_login,
        ip_address=client_ip(request),
        user_agent=user_agent(request),
        geo_country=geo_country(request),
    )


@protected_router.post("/logout")
async def logout(payload: LogoutRequest, auth_service: AuthService = Depends(get_auth_service)) -> dict:
    auth_service.logout(payload.refresh_token)
    return {"message": "Logout complete"}


@protected_router.get("/session", response_model=SessionInfo)
async def session_info(
    authorization: str = Header(alias="Authorization"),
    auth_service: AuthService = Depends(get_auth_service),
) -> SessionInfo:
    token = authorization.split(" ", 1)[1]
    return auth_service.get_session_info_from_access_token(token)


@protected_router.post("/mfa/setup", response_model=MfaSetupResponse)
async def mfa_setup(
    authorization: str = Header(alias="Authorization"),
    auth_service: AuthService = Depends(get_auth_service),
) -> MfaSetupResponse:
    token = authorization.split(" ", 1)[1]
    session = auth_service.get_session_info_from_access_token(token)
    secret, _codes = auth_service.setup_mfa(session.user_id, provider="google_authenticator")
    otpauth = f"otpauth://totp/tkk-uv:{session.user_id}?secret={secret}&issuer=tkk-uv"
    return MfaSetupResponse(secret=secret, otpauth_url=otpauth)


@protected_router.post("/mfa/verify")
async def mfa_verify(
    payload: MfaVerifyRequest,
    authorization: str = Header(alias="Authorization"),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    token = authorization.split(" ", 1)[1]
    session = auth_service.get_session_info_from_access_token(token)
    auth_service.enable_mfa(session.user_id, payload.code)
    return {"message": "MFA enabled"}


@protected_router.post("/authorize/feature", response_model=AuthorizationDecision)
async def authorize_feature(
    payload: FeatureAuthorizationRequest,
    auth_service: AuthService = Depends(get_auth_service),
    session: SessionInfo = Depends(session_info),
) -> AuthorizationDecision:
    user = auth_service.repository.get_user_by_id(session.user_id)
    if not user:
        return AuthorizationDecision(allowed=False, reason="user_not_found")
    allowed = auth_service.authorize_feature(user, payload.feature)
    return AuthorizationDecision(allowed=allowed, reason=None if allowed else "feature_forbidden")


@protected_router.get("/rbac/probe", dependencies=[Depends(require_permission("can_view_reports"))])
async def rbac_probe() -> dict:
    return {"message": "Permission granted"}
