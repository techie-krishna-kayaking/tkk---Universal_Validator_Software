from app.config.settings import Settings


def test_allowed_origins_parsing_multiple_values() -> None:
    settings = Settings(ALLOWED_ORIGINS="http://a.com,http://b.com")
    assert settings.allowed_origins == ["http://a.com", "http://b.com"]


def test_allowed_origins_wildcard() -> None:
    settings = Settings(ALLOWED_ORIGINS="*")
    assert settings.allowed_origins == ["*"]
