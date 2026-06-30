from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.profiles import EnvironmentProfile, LogFormat


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="tkk-UniversalValidator API", alias="APP_NAME")
    app_version: str = Field(default="0.2.0", alias="APP_VERSION")
    app_env: EnvironmentProfile = Field(default=EnvironmentProfile.LOCAL, alias="APP_ENV")
    app_debug: bool = Field(default=False, alias="APP_DEBUG")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")

    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    request_id_header: str = Field(default="X-Request-ID", alias="REQUEST_ID_HEADER")

    allowed_origins_raw: str = Field(default="*", alias="ALLOWED_ORIGINS")
    enable_gzip: bool = Field(default=True, alias="ENABLE_GZIP")
    enable_security_headers: bool = Field(default=True, alias="ENABLE_SECURITY_HEADERS")
    enable_rate_limit_hooks: bool = Field(default=True, alias="ENABLE_RATE_LIMIT_HOOKS")
    csrf_enabled: bool = Field(default=True, alias="CSRF_ENABLED")
    csrf_header_name: str = Field(default="X-CSRF-Token", alias="CSRF_HEADER_NAME")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: LogFormat = Field(default=LogFormat.JSON, alias="LOG_FORMAT")

    database_url: str = Field(default="", alias="DATABASE_URL")
    database_enabled: bool = Field(default=False, alias="DATABASE_ENABLED")
    database_required: bool = Field(default=False, alias="DATABASE_REQUIRED")

    redis_url: str = Field(default="", alias="REDIS_URL")
    redis_enabled: bool = Field(default=False, alias="REDIS_ENABLED")
    redis_required: bool = Field(default=False, alias="REDIS_REQUIRED")

    celery_broker_url: str = Field(default="", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="", alias="CELERY_RESULT_BACKEND")
    celery_enabled: bool = Field(default=False, alias="CELERY_ENABLED")
    celery_required: bool = Field(default=False, alias="CELERY_REQUIRED")

    openapi_url: str = Field(default="/openapi.json", alias="OPENAPI_URL")
    docs_url: str = Field(default="/docs", alias="DOCS_URL")
    redoc_url: str = Field(default="/redoc", alias="REDOC_URL")

    jwt_secret_key: str = Field(default="change_me_please_use_32_characters_min", alias="JWT_SECRET_KEY")
    jwt_issuer: str = Field(default="tkk-uv", alias="JWT_ISSUER")
    jwt_audience: str = Field(default="tkk-uv-api", alias="JWT_AUDIENCE")
    jwt_access_token_expire_minutes: int = Field(default=15, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_days: int = Field(default=30, alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS")

    password_min_length: int = Field(default=12, alias="PASSWORD_MIN_LENGTH")
    password_require_upper: bool = Field(default=True, alias="PASSWORD_REQUIRE_UPPER")
    password_require_lower: bool = Field(default=True, alias="PASSWORD_REQUIRE_LOWER")
    password_require_number: bool = Field(default=True, alias="PASSWORD_REQUIRE_NUMBER")
    password_require_special: bool = Field(default=True, alias="PASSWORD_REQUIRE_SPECIAL")

    max_failed_login_attempts: int = Field(default=5, alias="MAX_FAILED_LOGIN_ATTEMPTS")
    account_lockout_minutes: int = Field(default=15, alias="ACCOUNT_LOCKOUT_MINUTES")

    auth_rate_limit_attempts: int = Field(default=10, alias="AUTH_RATE_LIMIT_ATTEMPTS")
    auth_rate_limit_window_seconds: int = Field(default=60, alias="AUTH_RATE_LIMIT_WINDOW_SECONDS")

    oauth_google_client_id: str = Field(default="", alias="OAUTH_GOOGLE_CLIENT_ID")
    oauth_google_client_secret: str = Field(default="", alias="OAUTH_GOOGLE_CLIENT_SECRET")
    oauth_microsoft_client_id: str = Field(default="", alias="OAUTH_MICROSOFT_CLIENT_ID")
    oauth_microsoft_client_secret: str = Field(default="", alias="OAUTH_MICROSOFT_CLIENT_SECRET")
    oauth_azure_ad_client_id: str = Field(default="", alias="OAUTH_AZURE_AD_CLIENT_ID")
    oauth_azure_ad_client_secret: str = Field(default="", alias="OAUTH_AZURE_AD_CLIENT_SECRET")
    oauth_okta_client_id: str = Field(default="", alias="OAUTH_OKTA_CLIENT_ID")
    oauth_okta_client_secret: str = Field(default="", alias="OAUTH_OKTA_CLIENT_SECRET")

    ldap_enabled: bool = Field(default=False, alias="LDAP_ENABLED")
    saml_enabled: bool = Field(default=False, alias="SAML_ENABLED")

    config_encryption_key: str = Field(
        default="change_me_config_encryption_key_32_char_min",
        alias="CONFIG_ENCRYPTION_KEY",
    )
    secret_cache_ttl_seconds: int = Field(default=300, alias="SECRET_CACHE_TTL_SECONDS")
    config_env_prefix: str = Field(default="CFG_", alias="CONFIG_ENV_PREFIX")
    dotenv_source_path: str = Field(default=".env", alias="DOTENV_SOURCE_PATH")
    yaml_source_path: str = Field(default="config/examples/config_sources.yaml", alias="YAML_SOURCE_PATH")

    aws_secrets_manager_blob: str = Field(default="", alias="AWS_SECRETS_MANAGER_BLOB")
    azure_key_vault_blob: str = Field(default="", alias="AZURE_KEY_VAULT_BLOB")
    google_secret_manager_blob: str = Field(default="", alias="GOOGLE_SECRET_MANAGER_BLOB")
    hashicorp_vault_blob: str = Field(default="", alias="HASHICORP_VAULT_BLOB")

    @property
    def allowed_origins(self) -> List[str]:
        if self.allowed_origins_raw.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins_raw.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
