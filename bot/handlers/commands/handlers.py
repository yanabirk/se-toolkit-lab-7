"""
Command Handlers - Business Logic Layer

These handlers are async functions that call the LMS backend API.
They work in --test mode, unit tests, and Telegram.
"""

import asyncio
from typing import Optional

# Use absolute imports to avoid circular dependency
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.lms_api import get_client, close_client
from config import load_settings


def _get_client():
    """Get API client from settings."""
    settings = load_settings()
    return get_client(settings.lms_api_base_url, settings.lms_api_key)


async def handle_start() -> str:
    """Handle /start command."""
    return "Welcome to LMS Bot! Use /help to see available commands."


async def handle_help() -> str:
    """Handle /help command."""
    return (
        "Available commands:\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores <lab_id> - Get scores for a lab"
    )


async def handle_health() -> str:
    """Handle /health command."""
    client = _get_client()
    result = await client.health_check()

    if result["healthy"]:
        return f"Backend is healthy. {result['item_count']} items available."
    else:
        return f"Backend error: {result['error']}"


async def handle_labs() -> str:
    """Handle /labs command."""
    client = _get_client()
    try:
        labs = await client.get_labs()
        if not labs:
            return "No labs available."

        lines = ["Available labs:"]
        for lab in labs:
            # Try different field names for the lab title
            name = lab.get("title") or lab.get("name") or lab.get("id", "Unknown")
            lines.append(f"- {name}")
        return "\n".join(lines)
    except Exception as e:
        return f"Backend error: {str(e)}"


async def handle_scores(lab_id: Optional[str] = None) -> str:
    """
    Handle /scores command.

    Args:
        lab_id: Lab identifier (e.g., "lab-04")
    """
    if not lab_id:
        return "Please specify a lab ID. Usage: /scores lab-04"

    client = _get_client()
    try:
        data = await client.get_pass_rates(lab_id)
        if not data:
            return f"No pass rate data found for {lab_id}."

        lines = [f"Pass rates for {lab_id}:"]

        # Handle different response formats
        if isinstance(data, list):
            for item in data:
                task_name = item.get("task_name", item.get("task", "Unknown task"))
                pass_rate = item.get("pass_rate", item.get("average", 0)) * 100
                attempts = item.get("attempts", 0)
                lines.append(f"- {task_name}: {pass_rate:.1f}% ({attempts} attempts)")
        elif isinstance(data, dict):
            rates = data.get("pass_rates", data.get("rates", {}))
            for task_name, rate in rates.items():
                if isinstance(rate, dict):
                    pass_rate = rate.get("pass_rate", rate.get("average", 0)) * 100
                    attempts = rate.get("attempts", 0)
                else:
                    pass_rate = rate * 100
                    attempts = 0
                lines.append(f"- {task_name}: {pass_rate:.1f}% ({attempts} attempts)")

        return "\n".join(lines)
    except Exception as e:
        return f"Backend error: {str(e)}"
