import json
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.oauth_client import OAuthClient
from app.models.oauth_token import OAuthToken


class OAuthService:
    @staticmethod
    def create_client(
        db: Session, 
        client_name: str, 
        scopes: List[str]
    ) -> OAuthClient:
        """Create a new OAuth client"""
        client = OAuthClient(
            client_id=secrets.token_urlsafe(32),
            client_secret=secrets.token_urlsafe(64),
            client_name=client_name,
            scopes=json.dumps(scopes)
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        return client
    
    @staticmethod
    def authenticate_client(
        db: Session, 
        client_id: str, 
        client_secret: str
    ) -> Optional[OAuthClient]:
        """Authenticate OAuth client"""
        return db.query(OAuthClient).filter(
            OAuthClient.client_id == client_id,
            OAuthClient.client_secret == client_secret,
            OAuthClient.is_active == True
        ).first()
    
    @staticmethod
    def generate_token(
        db: Session, 
        client: OAuthClient, 
        scopes: List[str]
    ) -> OAuthToken:
        """Generate access token for client"""
        # Deactivate existing tokens for this client
        db.query(OAuthToken).filter(
            OAuthToken.client_id == client.client_id,
            OAuthToken.is_active == True
        ).update({"is_active": False})
        
        # Create new token
        token = OAuthToken(
            client_id=client.client_id,
            access_token=secrets.token_urlsafe(32),
            expires_at=datetime.utcnow() + timedelta(seconds=settings.oauth_token_expire_seconds),
            scopes=json.dumps(scopes)
        )
        db.add(token)
        db.commit()
        db.refresh(token)
        return token
    
    @staticmethod
    def validate_token(
        db: Session, 
        access_token: str
    ) -> Optional[OAuthToken]:
        """Validate access token"""
        token = db.query(OAuthToken).filter(
            OAuthToken.access_token == access_token,
            OAuthToken.is_active == True,
            OAuthToken.expires_at > datetime.utcnow()
        ).first()
        return token