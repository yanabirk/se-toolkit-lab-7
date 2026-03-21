"""
LMS Telegram Bot - Entry Point

Usage:
    uv run bot.py --test "/start"    # Test mode: print response to stdout
    uv run bot.py                     # Production: connect to Telegram
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from handlers.commands import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)


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


def handle_message(message: str) -> str:
    """
    Route incoming message to appropriate handler.
    
    This is the core routing logic - same function used in test mode and Telegram.
    """
    if message == "/start":
        return handle_start()
    elif message == "/help":
        return handle_help()
    elif message == "/health":
        return handle_health()
    elif message == "/labs":
        return handle_labs()
    elif message.startswith("/scores"):
        parts = message.split(maxsplit=1)
        lab_id = parts[1] if len(parts) > 1 else ""
        return handle_scores(lab_id)
    else:
        return "Unknown command. Use /help to see available commands."


def main() -> None:
    """Main entry point."""
    args = parse_args()
    
    if args.test:
        # Test mode: process message and print to stdout
        response = handle_message(args.test)
        print(response)
        sys.exit(0)
    else:
        # Production mode: connect to Telegram
        # TODO: Implement Telegram polling in Task 2
        print("Production mode not yet implemented. Use --test for testing.")
        sys.exit(1)


if __name__ == "__main__":
    main()
