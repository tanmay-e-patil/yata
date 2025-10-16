import httpx
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from .auth import oauth_client
from .config import settings


class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class YataAPIClient:
    def __init__(self):
        self.base_url = settings.api_base_url
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        token = oauth_client.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    async def create_todo(self, todo: TodoCreate) -> Dict[str, Any]:
        """Create a new todo"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/",
                json=todo.dict(),
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def list_todos(self) -> List[Dict[str, Any]]:
        """Get all todos"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def get_todo(self, todo_id: str) -> Dict[str, Any]:
        """Get a specific todo"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{todo_id}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def update_todo(self, todo_id: str, todo: TodoUpdate) -> Dict[str, Any]:
        """Update a todo"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/{todo_id}",
                json=todo.dict(exclude_unset=True),
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
    
    async def delete_todo(self, todo_id: str) -> Dict[str, Any]:
        """Delete a todo"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/{todo_id}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()


yata_client = YataAPIClient()