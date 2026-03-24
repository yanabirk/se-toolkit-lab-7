"""
Configuration loader for the LMS Bot.

Loads secrets from .env.bot.secret using pydantic-settings.
This pattern keeps secrets out of code and makes configuration explicit.
In Docker, environment variables come from docker-compose.yml.
"""

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Find .env.bot.secret in parent directory (relative to this file)
# Only used when running locally (not in Docker)
BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR / ".env.bot.secret"


class BotSettings(BaseSettings):
    """Bot configuration settings."""

    model_config = SettingsConfigDict(
        # Only use env file if it exists (local development)
        # In Docker, environment variables are injected directly
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
        # Support both snake_case and UPPER_CASE env var names
        populate_by_name=True,
    )

    # Telegram Bot Token
    bot_token: str = Field(default="")

    # LMS Backend API
    # In Docker, this should be http://backend:8000 (service name, not localhost)
    lms_api_base_url: str = Field(default="http://localhost:42002")
    lms_api_key: str = Field(default="secret")

    # LLM API (for Task 3)
    llm_api_key: str = Field(default="")
    llm_api_base_url: str = Field(default="")
    llm_api_model: str = Field(default="")


def load_settings() -> BotSettings:
    """Load and return bot settings."""
    return BotSettings()
