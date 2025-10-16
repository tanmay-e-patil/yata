import redis
import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.core.config import settings

# Initialize Redis client
redis_client = redis.from_url(settings.redis_url, decode_responses=True)


class SessionManager:
    @staticmethod
    def create_session(user_data: Dict[str, Any]) -> str:
        """Create a new session in Redis"""
        session_id = str(uuid.uuid4())
        session_data = {
            "user_id": str(user_data["id"]),
            "email": user_data["email"],
            "name": user_data["name"],
            "created_at": datetime.utcnow().isoformat(),
        }
        
        # Store session in Redis with expiration
        redis_client.setex(
            f"session:{session_id}",
            timedelta(hours=settings.session_expire_hours),
            json.dumps(session_data)
        )
        
        return session_id
    
    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data from Redis"""
        session_data = redis_client.get(f"session:{session_id}")
        if session_data:
            return json.loads(session_data)
        return None
    
    @staticmethod
    def delete_session(session_id: str) -> bool:
        """Delete session from Redis"""
        result = redis_client.delete(f"session:{session_id}")
        return result > 0
    
    @staticmethod
    def refresh_session(session_id: str) -> bool:
        """Refresh session expiration"""
        exists = redis_client.exists(f"session:{session_id}")
        if exists:
            redis_client.expire(
                f"session:{session_id}",
                timedelta(hours=settings.session_expire_hours)
            )
            return True
        return False


session_manager = SessionManager()