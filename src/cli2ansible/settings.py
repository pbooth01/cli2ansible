"""Application settings using Pydantic."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/cli2ansible"
    )

    # Object Storage (S3/MinIO)
    s3_endpoint: str = Field(default="http://localhost:9000")
    s3_access_key: str = Field(default="minioadmin")
    s3_secret_key: str = Field(default="minioadmin")
    s3_bucket: str = Field(default="cli2ansible-artifacts")

    # Application
    log_level: str = Field(default="INFO")
    debug: bool = Field(default=False)

    # LLM (Anthropic Claude)
    anthropic_api_key: str = Field(default="")
    max_commands_for_cleaning: int = Field(default=500)


settings = Settings()
