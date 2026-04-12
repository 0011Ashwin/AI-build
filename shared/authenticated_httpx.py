"""
Authenticated HTTPX Client for Google Cloud APIs
Handles authentication and API calls
"""

from typing import Dict, Any, Optional
import httpx
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials


class AuthenticatedHTTPXClient:
    """
    HTTPX client with Google Cloud authentication
    """
    
    def __init__(self, service_account_json: Optional[str] = None):
        self.service_account_json = service_account_json
        self.credentials = None
        self.client = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with Google Cloud"""
        try:
            if self.service_account_json:
                self.credentials = Credentials.from_service_account_file(
                    self.service_account_json
                )
            # In production, use Application Default Credentials
            self.client = httpx.AsyncClient()
        except Exception as e:
            print(f"Authentication warning: {e}")
            self.client = httpx.AsyncClient()
    
    async def get(self, url: str, **kwargs) -> httpx.Response:
        """Make authenticated GET request"""
        if self.credentials:
            request = Request()
            self.credentials.refresh(request)
            headers = kwargs.get("headers", {})
            headers["Authorization"] = f"Bearer {self.credentials.token}"
            kwargs["headers"] = headers
        
        return await self.client.get(url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> httpx.Response:
        """Make authenticated POST request"""
        if self.credentials:
            request = Request()
            self.credentials.refresh(request)
            headers = kwargs.get("headers", {})
            headers["Authorization"] = f"Bearer {self.credentials.token}"
            kwargs["headers"] = headers
        
        return await self.client.post(url, **kwargs)
    
    async def close(self) -> None:
        """Close client"""
        if self.client:
            await self.client.aclose()


class VertexAIClient:
    """Client for Vertex AI API calls"""
    
    def __init__(self, project_id: str, region: str = "us-central1"):
        self.project_id = project_id
        self.region = region
        self.endpoint = f"https://{region}-aiplatform.googleapis.com/v1"
    
    async def call_gemini_model(
        self,
        model_name: str,
        messages: list,
        system_prompt: Optional[str] = None
    ) -> str:
        """Call Gemini model via Vertex AI API"""
        # In production, use actual Vertex AI SDK
        endpoint = f"{self.endpoint}/projects/{self.project_id}/locations/{self.region}/endpoints/predict"
        
        return {
            "response": "Mock response from Gemini model",
            "model": model_name,
            "tokens_used": 150
        }
