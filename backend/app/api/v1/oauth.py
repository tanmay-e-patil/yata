from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.core.database import get_db
from app.core.config import settings
from app.services.oauth_service import OAuthService
from pydantic import BaseModel
import json

router = APIRouter()
security = HTTPBasic()


class TokenRequest(BaseModel):
    grant_type: str = "client_credentials"
    scope: str = ""


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    scope: str


@router.post("/token", response_model=TokenResponse)
async def create_token(
    token_request: TokenRequest,
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """OAuth 2.0 token endpoint"""
    # Validate grant type
    if token_request.grant_type != "client_credentials":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported grant type"
        )
    
    # Authenticate client
    client = OAuthService.authenticate_client(
        db, credentials.username, credentials.password
    )
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Parse scopes
    requested_scopes = token_request.scope.split() if token_request.scope else []
    allowed_scopes = json.loads(client.scopes)
    
    # Validate requested scopes
    for scope in requested_scopes:
        if scope not in allowed_scopes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid scope: {scope}"
            )
    
    # Generate token
    token = OAuthService.generate_token(db, client, requested_scopes)
    
    return TokenResponse(
        access_token=token.access_token,
        token_type=token.token_type,
        expires_in=settings.oauth_token_expire_seconds,
        scope=" ".join(requested_scopes)
    )


@router.post("/clients")
async def create_client(
    client_name: str,
    scopes: str,
    db: Session = Depends(get_db)
):
    """Create a new OAuth client (for development/setup)"""
    scope_list = scopes.split() if scopes else ["todos:read", "todos:write"]
    client = OAuthService.create_client(db, client_name, scope_list)
    
    return {
        "client_id": client.client_id,
        "client_secret": client.client_secret,
        "client_name": client.client_name,
        "scopes": json.loads(client.scopes)
    }