from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.models.user import User
from app.models.personal_token import PersonalToken
from app.api.deps import get_current_user
from app.services.personal_token_service import PersonalTokenService
from pydantic import BaseModel

router = APIRouter()


class PersonalTokenCreate(BaseModel):
    name: str
    expires_in_days: Optional[int] = 30


class PersonalTokenResponse(BaseModel):
    id: str
    name: str
    token: str
    expires_at: datetime
    created_at: datetime


class PersonalTokenInfo(BaseModel):
    id: str
    name: str
    expires_at: datetime
    created_at: datetime
    last_used_at: Optional[datetime] = None


def validate_personal_token(token: str, db: Session) -> Optional[User]:
    """Validate a personal token and return the associated user"""
    token_obj = PersonalTokenService.validate_token(db, token)
    
    if not token_obj:
        return None
    
    # Get user
    user = db.query(User).filter(User.id == token_obj.user_id).first()
    return user


@router.post("/tokens", response_model=PersonalTokenResponse)
async def create_token(
    token_data: PersonalTokenCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new personal access token"""
    
    try:
        personal_token, plain_token = PersonalTokenService.create_token(
            db, current_user, token_data.name, token_data.expires_in_days
        )
        
        return PersonalTokenResponse(
            id=personal_token.id,
            name=personal_token.name,
            token=plain_token,  # Only return the token once
            expires_at=personal_token.expires_at,
            created_at=personal_token.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/tokens", response_model=List[PersonalTokenInfo])
async def list_tokens(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all personal tokens for the current user"""
    
    tokens = PersonalTokenService.list_tokens(db, current_user)
    
    return [
        PersonalTokenInfo(
            id=token.id,
            name=token.name,
            expires_at=token.expires_at,
            created_at=token.created_at,
            last_used_at=token.last_used_at
        )
        for token in tokens
    ]


@router.get("/tokens/stats")
async def get_token_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get usage statistics for personal tokens"""
    
    stats = PersonalTokenService.get_token_usage_stats(db, current_user)
    return stats


@router.delete("/tokens/{token_id}")
async def revoke_token(
    token_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke a personal token"""
    
    success = PersonalTokenService.revoke_token(db, token_id, current_user)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    return {"message": "Token revoked successfully"}