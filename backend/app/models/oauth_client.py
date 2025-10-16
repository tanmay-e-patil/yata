import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base


class OAuthClient(Base):
    __tablename__ = "oauth_clients"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String, unique=True, nullable=False, index=True)
    client_secret = Column(String, nullable=False)
    client_name = Column(String, nullable=False)
    scopes = Column(Text, nullable=False)  # JSON string of allowed scopes
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<OAuthClient(id={self.id}, client_id={self.client_id})>"