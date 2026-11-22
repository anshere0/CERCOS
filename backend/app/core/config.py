"""Application configuration settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings loaded from environment or .env."""

    DATABASE_URL: str = "postgresql+psycopg://cercos:change_me@localhost:5432/cercos"
    OSRM_URL: str = "http://localhost:5000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
