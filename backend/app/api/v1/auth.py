from fastapi import APIRouter, HTTPException, status, Response, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.core.database import get_db
from app.core.config import settings
from app.services.auth_service import AuthService
from app.schemas.user import UserResponse
from app.api.deps import get_current_active_user

router = APIRouter()


@router.get("/google/login")
async def google_login():
    """Redirect to Google OAuth login"""
    auth_url = AuthService.get_google_auth_url()
    return RedirectResponse(url=auth_url)


@router.get("/google/callback", response_model=UserResponse)
async def google_callback(
    code: str,
    response: Response,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    try:
        # Exchange code for tokens
        tokens = await AuthService.exchange_code_for_tokens(code)
        access_token = tokens.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to obtain access token"
            )
        
        # Get user information
        user_info = await AuthService.get_user_info(access_token)
        
        # Create or update user in database
        user = AuthService.create_or_update_user(db, user_info)
        
        # Create session
        session_id = AuthService.create_session(user)
        
        # Set session cookie
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=settings.session_expire_hours * 3600,
            httponly=True,
            samesite="lax"
        )
        
        return UserResponse.from_orm(user)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/logout")
async def logout(
    response: Response,
    session_id: str = None
):
    """Logout user"""
    if session_id:
        AuthService.delete_session(session_id)
    
    # Clear session cookie
    response.delete_cookie(key="session_id")
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get current user information"""
    return current_user