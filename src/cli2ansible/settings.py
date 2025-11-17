"""Application settings using Pydantic."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/cli2ansible"
    )

    # Object Storage Provider Selection
    storage_provider: Literal["s3", "azure"] = Field(default="s3")

    # Object Storage (S3/MinIO)
    s3_endpoint: str = Field(default="http://localhost:9000")
    s3_access_key: str = Field(default="minioadmin")
    s3_secret_key: str = Field(default="minioadmin")
    s3_bucket: str = Field(default="cli2ansible-artifacts")

    # Object Storage (Azure Blob Storage)
    azure_connection_string: str = Field(default="")
    azure_container: str = Field(default="cli2ansible-artifacts")
    azure_account_name: str = Field(default="")
    azure_account_key: str = Field(default="")

    # Application
    log_level: str = Field(default="INFO")
    debug: bool = Field(default=False)

    # LLM (Anthropic Claude)
    anthropic_api_key: str = Field(default="")

    # LLM (OpenAI)
    openai_api_key: str = Field(default="")

    # LLM Provider Selection
    llm_provider: Literal["anthropic", "openai"] = Field(default="anthropic")

    max_commands_for_cleaning: int = Field(default=500)


settings = Settings()
