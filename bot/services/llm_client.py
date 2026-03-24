"""
LLM Client for Intent Recognition

Uses tool calling to let the LLM decide which backend API to call.
Same pattern as Lab 6, but embedded in the Telegram bot.
"""

import httpx
from typing import Any, Optional


class LLMClient:
    """Client for LLM API with tool calling support."""
    
    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
        return self._client
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    async def chat_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        max_iterations: int = 5,
    ) -> str:
        """
        Chat with LLM using tool calling.
        
        Args:
            messages: Conversation history
            tools: List of tool schemas
            max_iterations: Maximum tool call iterations
        
        Returns:
            Final response from LLM
        """
        client = await self._get_client()
        
        for iteration in range(max_iterations):
            # Call LLM
            response = await client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "tools": tools,
                    "tool_choice": "auto",
                },
            )
            response.raise_for_status()
            data = response.json()
            
            choice = data["choices"][0]["message"]
            
            # Check if LLM wants to call tools
            if "tool_calls" in choice and choice["tool_calls"]:
                tool_calls = choice["tool_calls"]
                
                # Execute tools and collect results
                tool_results = []
                for tool_call in tool_calls:
                    func_name = tool_call["function"]["name"]
                    func_args = tool_call["function"]["arguments"]
                    
                    # Parse arguments
                    import json
                    try:
                        args = json.loads(func_args) if func_args else {}
                    except json.JSONDecodeError:
                        args = {}
                    
                    # Execute the tool
                    result = await self._execute_tool(func_name, args)
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": result,
                    })
                
                # Add assistant message and tool results to conversation
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": tool_calls,
                })
                messages.extend(tool_results)
                
            else:
                # LLM returned final answer
                return choice.get("content", "I don't have information to answer that.")
        
        # Max iterations reached
        return "I'm having trouble finding the answer. Please try rephrasing your question."
    
    async def _execute_tool(self, name: str, args: dict[str, Any]) -> str:
        """
        Execute a tool and return result as string.
        
        Tools are delegated to the LMS API client.
        """
        # Import here to avoid circular dependency
        from .lms_api import get_client
        from ..config import load_settings
        
        settings = load_settings()
        lms_client = get_client(settings.lms_api_base_url, settings.lms_api_key)
        
        try:
            if name == "get_items":
                items = await lms_client.get("/items/")
                return f"Found {len(items)} items: {items[:5]}..."  # Truncate for context
            
            elif name == "get_learners":
                learners = await lms_client.get("/learners/")
                return f"Found {len(learners)} learners"
            
            elif name == "get_scores":
                lab = args.get("lab", "")
                scores = await lms_client.get(f"/analytics/scores?lab={lab}")
                return f"Scores for {lab}: {scores}"
            
            elif name == "get_pass_rates":
                lab = args.get("lab", "")
                rates = await lms_client.get(f"/analytics/pass-rates?lab={lab}")
                return f"Pass rates for {lab}: {rates}"
            
            elif name == "get_timeline":
                lab = args.get("lab", "")
                timeline = await lms_client.get(f"/analytics/timeline?lab={lab}")
                return f"Timeline for {lab}: {timeline}"
            
            elif name == "get_groups":
                lab = args.get("lab", "")
                groups = await lms_client.get(f"/analytics/groups?lab={lab}")
                return f"Groups for {lab}: {groups}"
            
            elif name == "get_top_learners":
                lab = args.get("lab", "")
                limit = args.get("limit", 5)
                top = await lms_client.get(f"/analytics/top-learners?lab={lab}&limit={limit}")
                return f"Top {limit} learners for {lab}: {top}"
            
            elif name == "get_completion_rate":
                lab = args.get("lab", "")
                rate = await lms_client.get(f"/analytics/completion-rate?lab={lab}")
                return f"Completion rate for {lab}: {rate}"
            
            elif name == "trigger_sync":
                result = await lms_client.get("/pipeline/sync", )
                return f"Sync triggered: {result}"
            
            else:
                return f"Unknown tool: {name}"
        
        except Exception as e:
            return f"Tool error: {str(e)}"


def get_llm_client(base_url: str, api_key: str, model: str) -> LLMClient:
    """Get or create the global LLM client."""
    return LLMClient(base_url, api_key, model)
