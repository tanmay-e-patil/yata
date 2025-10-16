import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import User
from app.models.personal_token import PersonalToken


class PersonalTokenService:
    @staticmethod
    def create_token(
        db: Session, 
        user: User, 
        name: str, 
        expires_in_days: int = 30
    ) -> tuple[PersonalToken, str]:
        """Create a personal access token for a user"""
        
        # Check if user has reached the token limit
        active_tokens = db.query(PersonalToken).filter(
            PersonalToken.user_id == user.id,
            PersonalToken.is_active == True,
            PersonalToken.expires_at > datetime.utcnow()
        ).count()
        
        max_tokens = getattr(settings, 'max_personal_tokens_per_user', 10)
        if active_tokens >= max_tokens:
            raise ValueError(f"Maximum number of active tokens reached ({max_tokens})")
        
        # Generate token
        token = secrets.token_urlsafe(64)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Set expiration
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create token record
        personal_token = PersonalToken(
            name=name,
            token_hash=token_hash,
            user_id=user.id,
            expires_at=expires_at
        )
        
        db.add(personal_token)
        db.commit()
        db.refresh(personal_token)
        
        return personal_token, token
    
    @staticmethod
    def validate_token(db: Session, token: str) -> Optional[PersonalToken]:
        """Validate a personal token and return the token object"""
        
        # Hash the token to compare with stored hash
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Find token in database
        token_obj = db.query(PersonalToken).filter(
            PersonalToken.token_hash == token_hash,
            PersonalToken.is_active == True,
            PersonalToken.expires_at > datetime.utcnow()
        ).first()
        
        if token_obj:
            # Update last used timestamp
            token_obj.last_used_at = datetime.utcnow()
            db.commit()
        
        return token_obj
    
    @staticmethod
    def revoke_token(db: Session, token_id: str, user: User) -> bool:
        """Revoke a personal token"""
        
        token = db.query(PersonalToken).filter(
            PersonalToken.id == token_id,
            PersonalToken.user_id == user.id,
            PersonalToken.is_active == True
        ).first()
        
        if not token:
            return False
        
        token.is_active = False
        db.commit()
        
        return True
    
    @staticmethod
    def list_tokens(db: Session, user: User) -> List[PersonalToken]:
        """List all active tokens for a user"""
        
        return db.query(PersonalToken).filter(
            PersonalToken.user_id == user.id,
            PersonalToken.is_active == True
        ).order_by(PersonalToken.created_at.desc()).all()
    
    @staticmethod
    def cleanup_expired_tokens(db: Session) -> int:
        """Clean up expired tokens and return count of cleaned tokens"""
        
        expired_tokens = db.query(PersonalToken).filter(
            PersonalToken.expires_at < datetime.utcnow()
        ).all()
        
        count = len(expired_tokens)
        
        for token in expired_tokens:
            token.is_active = False
        
        db.commit()
        
        return count
    
    @staticmethod
    def get_token_usage_stats(db: Session, user: User) -> dict:
        """Get usage statistics for a user's tokens"""
        
        active_tokens = db.query(PersonalToken).filter(
            PersonalToken.user_id == user.id,
            PersonalToken.is_active == True,
            PersonalToken.expires_at > datetime.utcnow()
        ).all()
        
        total_tokens = db.query(PersonalToken).filter(
            PersonalToken.user_id == user.id
        ).count()
        
        recently_used = db.query(PersonalToken).filter(
            PersonalToken.user_id == user.id,
            PersonalToken.last_used_at > datetime.utcnow() - timedelta(days=7)
        ).count()
        
        return {
            "active_tokens": len(active_tokens),
            "total_tokens": total_tokens,
            "recently_used": recently_used,
            "max_allowed": getattr(settings, 'max_personal_tokens_per_user', 10)
        }