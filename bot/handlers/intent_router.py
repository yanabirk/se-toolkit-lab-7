"""
Intent Router - LLM-powered natural language routing

Routes user messages to appropriate handlers using LLM tool calling.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.llm_client import get_llm_client
from services.tools import TOOLS, SYSTEM_PROMPT
from config import load_settings


async def route_natural_language(message: str) -> str:
    """
    Route natural language message using LLM.
    
    Args:
        message: User's natural language query
    
    Returns:
        Response text
    """
    settings = load_settings()
    
    # Check if LLM is configured
    if not settings.llm_api_key or not settings.llm_api_base_url:
        return "LLM is not configured. Please use slash commands like /help, /labs, /scores."
    
    llm = get_llm_client(
        settings.llm_api_base_url,
        settings.llm_api_key,
        settings.llm_api_model or "llama3.2",
    )
    
    # Build conversation
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message},
    ]
    
    try:
        response = await llm.chat_with_tools(messages, TOOLS)
        return response
    except Exception as e:
        # Debug output to stderr
        print(f"[llm_error] {str(e)}", file=sys.stderr)
        return f"LLM error: {str(e)}. Try using a slash command like /help."
