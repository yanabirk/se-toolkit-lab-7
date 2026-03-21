"""
Configuration loader for the LMS Bot.

Loads secrets from .env.bot.secret using pydantic-settings.
This pattern keeps secrets out of code and makes configuration explicit.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Find .env.bot.secret in parent directory (relative to this file)
BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR / ".env.bot.secret"


class BotSettings(BaseSettings):
    """Bot configuration settings."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram Bot Token
    bot_token: str = ""

    # LMS Backend API
    lms_api_base_url: str = "http://localhost:42002"
    lms_api_key: str = "secret"

    # LLM API (for Task 3)
    llm_api_key: str = ""
    llm_api_base_url: str = ""
    llm_api_model: str = ""


def load_settings() -> BotSettings:
    """Load and return bot settings."""
    return BotSettings()
