"""
Configuration settings for the PensionFund Officer Dashboard application.
Uses Pydantic Settings for environment variable management.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "PensionFund Officer Dashboard"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # MongoDB Atlas
    mongodb_url: str = "mongodb+srv://<user>:<password>@<cluster>.mongodb.net/<db>"
    mongodb_db_name: str = "PensionFund_db"
    mongodb_max_pool_size: int = 50
    mongodb_min_pool_size: int = 10

    # Atlas Search Indexes
    members_search_index: str = "members_search_index"
    members_vector_index: str = "members_vector_index"
    employers_search_index: str = "employers_search_index"
    employers_vector_index: str = "employers_vector_index"

    # Anthropic API (for Voyage AI embeddings)
    anthropic_api_key: Optional[str] = None
    voyage_model: str = "voyage-large-2"
    voyage_dimensions: int = 512

    # Search Settings
    default_search_limit: int = 20
    max_search_limit: int = 100
    vector_num_candidates: int = 100

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Materialized Views Refresh Schedule (cron expressions)
    refresh_member_demographics_cron: str = "*/15 * * * *"  # Every 15 minutes
    refresh_member_balances_cron: str = "0 * * * *"  # Hourly
    refresh_member_contributions_cron: str = "0 2 * * *"  # Daily at 2 AM
    refresh_member_compliance_cron: str = "*/30 * * * *"  # Every 30 minutes
    refresh_employer_profiles_cron: str = "0 */6 * * *"  # Every 6 hours
    refresh_employer_compliance_cron: str = "0 */3 * * *"  # Every 3 hours
    refresh_employer_workforce_cron: str = "0 3 * * *"  # Daily at 3 AM
    refresh_employer_submissions_cron: str = "0 4 * * *"  # Daily at 4 AM

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Create global settings instance
settings = Settings()
