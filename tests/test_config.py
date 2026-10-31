from app.core.config import Settings


def test_database_url_with_pgbouncer_param_is_sanitized():
    settings = Settings(
        SECRET_KEY="test-secret",
        DATABASE_URL="postgresql://user:pass@host:5432/db?pgbouncer=true&sslmode=require",
        ACCESS_TOKEN_EXPIRE_MINUTES=60,
        REFRESH_TOKEN_EXPIRE_DAYS=60,
        OTP_EXPIRE_MINUTES=60,
        ALGORITHM="HS256",
        RESEND_COOLDOWN_SECONDS=60,
        BACKEND_CORS_ORIGINS=["http://localhost"],
        DEBUG=True,
        ENVIRONMENT="test",
    )
    assert settings.DATABASE_URL == "postgresql://user:pass@host:5432/db?sslmode=require"


def test_database_url_with_leading_whitespace_is_trimmed():
    settings = Settings(
        SECRET_KEY="test-secret",
        DATABASE_URL=" postgresql://user:pass@host:5432/db",
        ACCESS_TOKEN_EXPIRE_MINUTES=60,
        REFRESH_TOKEN_EXPIRE_DAYS=60,
        OTP_EXPIRE_MINUTES=60,
        ALGORITHM="HS256",
        RESEND_COOLDOWN_SECONDS=60,
        BACKEND_CORS_ORIGINS=["http://localhost"],
        DEBUG=True,
        ENVIRONMENT="test",
    )
    assert settings.DATABASE_URL == "postgresql://user:pass@host:5432/db"


def test_database_url_with_postgres_scheme_is_converted():
    settings = Settings(
        SECRET_KEY="test-secret",
        DATABASE_URL="postgres://user:pass@host:5432/db",
        ACCESS_TOKEN_EXPIRE_MINUTES=60,
        REFRESH_TOKEN_EXPIRE_DAYS=60,
        OTP_EXPIRE_MINUTES=60,
        ALGORITHM="HS256",
        RESEND_COOLDOWN_SECONDS=60,
        BACKEND_CORS_ORIGINS=["http://localhost"],
        DEBUG=True,
        ENVIRONMENT="test",
    )
    assert settings.DATABASE_URL == "postgresql://user:pass@host:5432/db"
