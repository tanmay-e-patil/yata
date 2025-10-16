from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    email: str
    name: str
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    google_id: str


class UserResponse(UserBase):
    id: str
    
    class Config:
        from_attributes = True