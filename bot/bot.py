"""
LMS Telegram Bot - Entry Point

Usage:
    uv run bot.py --test "/start"    # Test mode: print response to stdout
    uv run bot.py                     # Production: connect to Telegram
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from config import load_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="MESSAGE",
        help="Test mode: process message and print response to stdout",
    )
    return parser.parse_args()


async def handle_message(message: str) -> str:
    """
    Route incoming message to appropriate handler.

    This is the core routing logic - same function used in test mode and Telegram.
    """
    if message == "/start":
        return await handle_start()
    elif message == "/help":
        return await handle_help()
    elif message == "/health":
        return await handle_health()
    elif message == "/labs":
        return await handle_labs()
    elif message.startswith("/scores"):
        parts = message.split(maxsplit=1)
        lab_id = parts[1] if len(parts) > 1 else ""
        return await handle_scores(lab_id)
    else:
        return "Unknown command. Use /help to see available commands."


async def run_telegram_bot() -> None:
    """Run the bot in production mode with Telegram."""
    try:
        from aiogram import Bot, Dispatcher, types
    except ImportError:
        logger.error("aiogram not installed. Run: uv sync")
        sys.exit(1)

    settings = load_settings()

    if not settings.bot_token:
        logger.error("BOT_TOKEN not set in .env.bot.secret")
        sys.exit(1)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    @dp.message(lambda msg: msg.text == "/start")
    async def cmd_start(message: types.Message) -> None:
        """Handle /start command."""
        response = await handle_start()
        await message.answer(response)

    @dp.message(lambda msg: msg.text == "/help")
    async def cmd_help(message: types.Message) -> None:
        """Handle /help command."""
        response = await handle_help()
        await message.answer(response)

    @dp.message(lambda msg: msg.text == "/health")
    async def cmd_health(message: types.Message) -> None:
        """Handle /health command."""
        response = await handle_health()
        await message.answer(response)

    @dp.message(lambda msg: msg.text == "/labs")
    async def cmd_labs(message: types.Message) -> None:
        """Handle /labs command."""
        response = await handle_labs()
        await message.answer(response)

    @dp.message(lambda msg: msg.text and msg.text.startswith("/scores"))
    async def cmd_scores(message: types.Message) -> None:
        """Handle /scores command."""
        text = message.text if message.text else "/scores"
        parts = text.split(maxsplit=1)
        lab_id = parts[1] if len(parts) > 1 else ""
        response = await handle_scores(lab_id)
        await message.answer(response)

    @dp.message()
    async def handle_unknown(message: types.Message) -> None:
        """Handle unknown commands/messages."""
        if message.text:
            response = await handle_message(message.text)
            await message.answer(response)

    logger.info("Bot started. Polling...")
    await dp.start_polling(bot)


def main() -> None:
    """Main entry point."""
    args = parse_args()

    if args.test:
        # Test mode: process message and print to stdout
        response = asyncio.run(handle_message(args.test))
        print(response)
        sys.exit(0)
    else:
        # Production mode: connect to Telegram
        asyncio.run(run_telegram_bot())


if __name__ == "__main__":
    main()
