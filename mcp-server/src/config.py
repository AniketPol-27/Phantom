"""
Configuration management for the Phantom MCP server.

Loads environment variables and provides a typed settings object
that the rest of the application uses.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8080
    log_level: str = "INFO"

    # FHIR server (fallback for local dev when SHARP context is absent)
    default_fhir_base_url: str = "https://hapi.fhir.org/baseR4"

    # External APIs
    rxnorm_api_base: str = "https://rxnav.nlm.nih.gov/REST"
    rxnorm_timeout_seconds: int = 10

    openfda_api_base: str = "https://api.fda.gov"
    openfda_timeout_seconds: int = 10

    # Patient model cache
    model_cache_ttl_seconds: int = 1800

    # MCP authentication (optional)
    mcp_auth_token: str = ""

    # Development mode
    dev_mode: bool = True


@lru_cache
def get_settings() -> Settings:
    """
    Returns the singleton settings instance.

    Cached so we don't re-read the .env file on every call.
    """
    return Settings()