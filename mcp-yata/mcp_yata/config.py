from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # OAuth settings (for client credentials flow)
    oauth_client_id: Optional[str] = None
    oauth_client_secret: Optional[str] = None
    oauth_token_url: str = "http://backend:8000/api/v1/oauth/token"
    
    # Personal token settings (simplified auth)
    personal_access_token: Optional[str] = None
    
    # API settings
    api_base_url: str = "http://backend:8000/api/v1/oauth-todos"
    
    # MCP settings
    server_name: str = "mcp-yata"
    server_version: str = "1.0.0"
    
    # Auth mode: "oauth" or "personal"
    auth_mode: str = "oauth"
    
    class Config:
        env_file = ".env"


settings = Settings()