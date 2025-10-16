import time
import httpx
from typing import Optional
from .config import settings


class SimpleAuthClient:
    """Simple authentication using personal access tokens"""
    
    def __init__(self):
        self.personal_token = settings.personal_access_token
        self.api_base_url = settings.api_base_url
    
    def get_headers(self) -> dict:
        """Get headers with authentication"""
        if not self.personal_token:
            raise ValueError("No personal access token configured")
        
        return {
            "Authorization": f"Bearer {self.personal_token}",
            "Content-Type": "application/json"
        }
    
    async def create_todo(self, todo_data: dict) -> dict:
        """Create a new todo"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_base_url}/",
                json=todo_data,
                headers=self.get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def list_todos(self) -> list:
        """Get all todos"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base_url}/",
                headers=self.get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def get_todo(self, todo_id: str) -> dict:
        """Get a specific todo"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base_url}/{todo_id}",
                headers=self.get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def update_todo(self, todo_id: str, todo_data: dict) -> dict:
        """Update a todo"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.api_base_url}/{todo_id}",
                json=todo_data,
                headers=self.get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def delete_todo(self, todo_id: str) -> dict:
        """Delete a todo"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.api_base_url}/{todo_id}",
                headers=self.get_headers()
            )
            response.raise_for_status()
            return response.json()


simple_client = SimpleAuthClient()