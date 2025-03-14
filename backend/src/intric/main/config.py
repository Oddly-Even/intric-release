import json
import logging
import os
from typing import Optional

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from intric.definitions import ROOT_DIR

MANIFEST_LOCATION = f"{ROOT_DIR}/.release-please-manifest.json"


def _set_app_version():
    try:
        with open(MANIFEST_LOCATION) as f:
            manifest_data = json.load(f)

        version = manifest_data["."]
        if os.environ.get("DEV", False):
            return f"{version}-dev"

        return version
    except FileNotFoundError:
        return "DEV"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    app_version: str = _set_app_version()

    # Api keys and model urls
    infinity_url: Optional[str] = None
    vllm_model_url: Optional[str] = None
    whisper_model_url: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Model config
    whisper_model_name: str = "whisper-1"

    # Infrastructure dependencies
    postgres_user: str
    postgres_host: str
    postgres_password: str
    postgres_port: int
    postgres_db: str
    redis_host: str
    redis_port: int

    # Mobilityguard
    mobilityguard_discovery_endpoint: Optional[str] = None
    mobilityguard_client_id: Optional[str] = None
    mobilityguard_client_secret: Optional[str] = None
    mobilityguard_tenant_id: Optional[str] = None

    # Max sizes
    upload_file_to_session_max_size: int
    upload_image_to_session_max_size: int
    upload_max_file_size: int
    transcription_max_file_size: int
    max_in_question: int

    # Azure models
    using_azure_models: bool = False
    azure_api_key: Optional[str] = None
    azure_endpoint: Optional[str] = None
    azure_api_version: Optional[str] = None

    # Feature flags
    using_access_management: bool = True
    using_intric_proprietary: bool = False
    hosting_intric_proprietary: bool = False
    using_iam: bool = False

    # Security
    api_prefix: str
    api_key_length: int
    api_key_header_name: str
    jwt_audience: str
    jwt_issuer: str
    jwt_expiry_time: int
    jwt_algorithm: str
    jwt_secret: str
    jwt_token_prefix: str

    # Dev
    testing: bool = False
    dev: bool = False

    # Crawl
    crawl_max_length: int = 60 * 60 * 4  # 4 hour crawls max
    closespider_itemcount: int = 20000
    obey_robots: bool = True
    autothrottle_enabled: bool = True
    using_crawl: bool = True

    @computed_field
    @property
    def sync_database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )


class SettingsProvider:
    """Provider for settings that supports override for testing"""
    _instance = None
    _test_settings = None

    @classmethod
    def get_settings(self) -> Settings:
        """Get the current settings, prioritizing test settings if in test mode"""
        if self._test_settings is not None:
            return self._test_settings

        if self._instance is None:
            self._instance = Settings()

        return self._instance

    @classmethod
    def configure_for_testing(self, **overrides):
        """Set up test-specific settings"""
        base_settings = self.get_settings() if self._test_settings is None else self._instance
        test_db_name = f"{base_settings.postgres_db}_test"

        # Start with a base config and layer on overrides
        test_config = {
            **base_settings.model_dump(),
            "testing": True,
            "postgres_db": test_db_name,
            **overrides
        }

        self._test_settings = Settings.model_validate(test_config)
        return self._test_settings

    @classmethod
    def reset_test_settings(cls):
        """Clear test settings and return to normal settings"""
        cls._test_settings = None


# For backwards compatibility
SETTINGS = SettingsProvider.get_settings()


def get_settings():
    """Get current settings (either test or normal)"""
    return SettingsProvider.get_settings()


def get_loglevel():
    loglevel = os.getenv("LOGLEVEL", "INFO")

    match loglevel:
        case "INFO":
            return logging.INFO
        case "WARNING":
            return logging.WARNING
        case "ERROR":
            return logging.ERROR
        case "CRITICAL":
            return logging.CRITICAL
        case "DEBUG":
            return logging.DEBUG
        case _:
            return logging.INFO
