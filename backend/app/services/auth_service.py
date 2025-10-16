import httpx
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.security import session_manager
from app.models.user import User
from app.schemas.user import UserCreate


class AuthService:
    @staticmethod
    def get_google_auth_url() -> str:
        """Generate Google OAuth authorization URL"""
        params = {
            "client_id": settings.google_client_id,
            "redirect_uri": f"{settings.frontend_url}/auth/callback",
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
        }
        
        param_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"https://accounts.google.com/o/oauth2/v2/auth?{param_string}"
    
    @staticmethod
    async def exchange_code_for_tokens(code: str) -> Dict[str, Any]:
        """Exchange authorization code for access tokens"""
        data = {
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": f"{settings.frontend_url}/auth/callback",
            "grant_type": "authorization_code",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data=data
            )
            response.raise_for_status()
            return response.json()
    
    @staticmethod
    async def get_user_info(access_token: str) -> Dict[str, Any]:
        """Get user information from Google using access token"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return response.json()
    
    @staticmethod
    def create_or_update_user(db: Session, user_info: Dict[str, Any]) -> User:
        """Create or update user in database"""
        google_id = user_info["id"]
        email = user_info["email"]
        name = user_info["name"]
        avatar_url = user_info.get("picture")
        
        # Check if user already exists
        user = db.query(User).filter(User.google_id == google_id).first()
        
        if user:
            # Update existing user
            user.email = email
            user.name = name
            user.avatar_url = avatar_url
            db.commit()
            db.refresh(user)
        else:
            # Create new user
            user_create = UserCreate(
                google_id=google_id,
                email=email,
                name=name,
                avatar_url=avatar_url
            )
            user = User(**user_create.dict())
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return user
    
    @staticmethod
    def create_session(user: User) -> str:
        """Create session for authenticated user"""
        return session_manager.create_session({
            "id": user.id,
            "email": user.email,
            "name": user.name,
        })
    
    @staticmethod
    def delete_session(session_id: str) -> bool:
        """Delete user session"""
        return session_manager.delete_session(session_id)