from urllib.parse import urlencode

from app.config.settings import Settings
from app.schemas.auth import OAuthProvider


class FederatedAuthService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def authorization_url(self, provider: OAuthProvider, redirect_uri: str, state: str) -> str:
        base_url = self._provider_authorize_url(provider)
        params = {
            "response_type": "code",
            "client_id": self._provider_client_id(provider),
            "redirect_uri": redirect_uri,
            "scope": "openid profile email",
            "state": state,
        }
        return f"{base_url}?{urlencode(params)}"

    def _provider_client_id(self, provider: OAuthProvider) -> str:
        mapping = {
            OAuthProvider.GOOGLE: self.settings.oauth_google_client_id,
            OAuthProvider.MICROSOFT: self.settings.oauth_microsoft_client_id,
            OAuthProvider.AZURE_AD: self.settings.oauth_azure_ad_client_id,
            OAuthProvider.OKTA: self.settings.oauth_okta_client_id,
            OAuthProvider.OPENID_CONNECT: self.settings.oauth_okta_client_id,
            OAuthProvider.LDAP: "ldap_optional",
            OAuthProvider.SAML: "saml_future_ready",
        }
        return mapping[provider]

    def _provider_authorize_url(self, provider: OAuthProvider) -> str:
        mapping = {
            OAuthProvider.GOOGLE: "https://accounts.google.com/o/oauth2/v2/auth",
            OAuthProvider.MICROSOFT: "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            OAuthProvider.AZURE_AD: "https://login.microsoftonline.com/organizations/oauth2/v2.0/authorize",
            OAuthProvider.OKTA: "https://example.okta.com/oauth2/default/v1/authorize",
            OAuthProvider.OPENID_CONNECT: "https://oidc.example.com/authorize",
            OAuthProvider.LDAP: "https://ldap-auth.local/authorize",
            OAuthProvider.SAML: "https://saml-auth.local/authorize",
        }
        return mapping[provider]
