from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App settings
    app_name: str = "Yata Todo App"
    debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production"
    
    # Database settings
    database_url: str = "postgresql://postgres:postgres@localhost:5432/yata_dev"
    
    # Redis settings
    redis_url: str = "redis://localhost:6379"
    
    # OAuth settings
    google_client_id: str = ""
    google_client_secret: str = ""
    frontend_url: str = "http://localhost:3000"
    
    # Session settings
    session_expire_hours: int = 24
    
    # OAuth settings
    oauth_token_expire_seconds: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"


settings = Settings()