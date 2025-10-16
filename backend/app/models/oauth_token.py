import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String, ForeignKey("oauth_clients.client_id"), nullable=False)
    access_token = Column(String, unique=True, nullable=False, index=True)
    token_type = Column(String, default="Bearer")
    expires_at = Column(DateTime(timezone=True), nullable=False)
    scopes = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship with OAuthClient
    client = relationship("OAuthClient", backref="tokens")

    def __repr__(self):
        return f"<OAuthToken(id={self.id}, client_id={self.client_id})>"