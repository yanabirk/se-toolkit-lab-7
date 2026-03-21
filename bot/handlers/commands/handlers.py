"""
Command Handlers - Business Logic Layer

These handlers are pure functions: they take input and return text.
No Telegram dependency - same functions work in --test mode, unit tests, and Telegram.
"""


def handle_start() -> str:
    """Handle /start command."""
    return "Welcome to LMS Bot! Use /help to see available commands."


def handle_help() -> str:
    """Handle /help command."""
    return (
        "Available commands:\n"
        "/start - Welcome message\n"
        "/help - Show this help\n"
        "/health - Check backend status\n"
        "/labs - List available labs\n"
        "/scores <lab_id> - Get scores for a lab"
    )


def handle_health() -> str:
    """Handle /health command."""
    # TODO: In Task 2, call backend API
    return "Backend status: OK (placeholder)"


def handle_labs() -> str:
    """Handle /labs command."""
    # TODO: In Task 2, fetch from backend API
    return "Available labs: lab-01, lab-02, lab-03, lab-04 (placeholder)"


def handle_scores(lab_id: str) -> str:
    """
    Handle /scores command.
    
    Args:
        lab_id: Lab identifier (e.g., "lab-04")
    """
    # TODO: In Task 2, fetch from backend API
    if not lab_id:
        return "Please specify a lab ID. Usage: /scores lab-04"
    return f"Scores for {lab_id}: 100/100 (placeholder)"
