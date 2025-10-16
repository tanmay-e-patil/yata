import time
import httpx
from typing import Optional
from .config import settings


class OAuthClient:
    def __init__(self):
        self.client_id = settings.oauth_client_id
        self.client_secret = settings.oauth_client_secret
        self.token_url = settings.oauth_token_url
        self._token = None
        self._token_expires_at = 0
    
    def get_access_token(self) -> str:
        """Get valid access token, refreshing if necessary"""
        current_time = time.time()
        
        # Check if token is valid
        if self._token and current_time < self._token_expires_at:
            return self._token["access_token"]
        
        # Fetch new token with JSON body
        with httpx.Client() as client:
            response = client.post(
                self.token_url,
                auth=(self.client_id, self.client_secret),
                json={
                    "grant_type": "client_credentials",
                    "scope": "todos:read todos:write"
                }
            )
            response.raise_for_status()
            token = response.json()
        
        # Handle different token response formats
        if "access_token" not in token:
            raise KeyError(f"'access_token' not found in token response: {token}")
        
        # Store token and expiration
        self._token = token
        self._token_expires_at = current_time + token.get("expires_in", 3600) - 60  # Refresh 1 min early
        
        return token["access_token"]


oauth_client = OAuthClient()