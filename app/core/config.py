from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "Authorization Service API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

# JWT Security
    SECRET_KEY: str 
    ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    REFRESH_TOKEN_EXPIRE_DAYS: int
    OTP_EXPIRE_MINUTES: int 
    RESEND_COOLDOWN_SECONDS: int 
    #  Database URL
    DATABASE_URL: str
    # Core Backend 
    BACKEND_CORS_ORIGINS: List[str] 
    DEBUG: bool 
    ENVIRONMENT: Optional[str] 
    LOG_LEVEL: str = "INFO"

    R2_ENDPOINT_URL: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = ""
    R2_PUBLIC_URL: str = ""

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def sanitize_database_url(cls, value):
        if value is None or not isinstance(value, str):
            return value

        value = value.strip()

        if value.startswith("postgres://"):
            value = "postgresql://" + value[len("postgres://"):]

        parsed = urlparse(value)
        if parsed.query:
            query_params = dict(parse_qsl(parsed.query, keep_blank_values=True))
            query_params.pop("pgbouncer", None)
            new_query = urlencode(query_params, doseq=True)
            parsed = parsed._replace(query=new_query)
            value = urlunparse(parsed)

        return value

    @property
    def cors_origins(self) -> List[str]:
        # If BACKEND_CORS_ORIGINS is a string, parse it
        if isinstance(self.BACKEND_CORS_ORIGINS, str):
            return json.loads(self.BACKEND_CORS_ORIGINS)
        return self.BACKEND_CORS_ORIGINS

settings = Settings()
