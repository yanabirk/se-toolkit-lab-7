"""
LMS API Client

HTTP client for the LMS backend API.
Uses Bearer token authentication.
"""

import httpx
from typing import Optional, Any


class LMSAPIClient:
    """Client for the LMS backend API."""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with auth headers."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=10.0,
            )
        return self._client
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    async def get(self, endpoint: str) -> dict[str, Any]:
        """
        Make GET request to the API.
        
        Args:
            endpoint: API endpoint (e.g., "/items/", "/analytics/pass-rates")
        
        Returns:
            JSON response as dict
        
        Raises:
            httpx.HTTPError: On HTTP errors
            httpx.ConnectError: On connection errors
        """
        client = await self._get_client()
        response = await client.get(endpoint)
        response.raise_for_status()
        return response.json()
    
    async def health_check(self) -> dict[str, Any]:
        """
        Check backend health by calling /items/ endpoint.
        
        Returns:
            Dict with 'healthy' bool and 'item_count' int
        """
        try:
            items = await self.get("/items/")
            return {
                "healthy": True,
                "item_count": len(items) if isinstance(items, list) else 0,
            }
        except httpx.ConnectError as e:
            return {
                "healthy": False,
                "error": f"connection refused ({self.base_url}). Check that the services are running.",
                "original_error": str(e),
            }
        except httpx.HTTPStatusError as e:
            return {
                "healthy": False,
                "error": f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.",
                "original_error": str(e),
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "original_error": str(e),
            }
    
    async def get_labs(self) -> list[dict[str, Any]]:
        """
        Get list of labs from /items/ endpoint.
        
        Returns:
            List of lab items
        """
        items = await self.get("/items/")
        if isinstance(items, list):
            return items
        return []
    
    async def get_pass_rates(self, lab_id: str) -> dict[str, Any]:
        """
        Get pass rates for a specific lab.
        
        Args:
            lab_id: Lab identifier (e.g., "lab-04")
        
        Returns:
            Dict with pass rate data
        """
        return await self.get(f"/analytics/pass-rates?lab={lab_id}")


# Global client instance (created on demand)
_api_client: Optional[LMSAPIClient] = None


def get_client(base_url: str, api_key: str) -> LMSAPIClient:
    """Get or create the global API client."""
    global _api_client
    if _api_client is None:
        _api_client = LMSAPIClient(base_url, api_key)
    return _api_client


async def close_client() -> None:
    """Close the global API client."""
    global _api_client
    if _api_client:
        await _api_client.close()
        _api_client = None
