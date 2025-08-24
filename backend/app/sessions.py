import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import redis.asyncio as redis
from .config import settings


class SessionManager:
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url)
        self.session_prefix = "session:"
        self.expire_hours = settings.session_expire_hours
    
    async def create_session(self, user_id: int, user_data: Dict[str, Any]) -> str:
        """Create a new session for a user"""
        session_id = str(uuid.uuid4())
        session_key = f"{self.session_prefix}{session_id}"
        
        session_data = {
            "user_id": user_id,
            "user_data": user_data,
            "created_at": datetime.utcnow().isoformat(),
            "last_accessed": datetime.utcnow().isoformat()
        }
        
        # Store session in Redis with expiration
        await self.redis_client.setex(
            session_key,
            timedelta(hours=self.expire_hours),
            json.dumps(session_data)
        )
        
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by session ID"""
        session_key = f"{self.session_prefix}{session_id}"
        session_data = await self.redis_client.get(session_key)
        
        if not session_data:
            return None
        
        # Parse session data
        session = json.loads(session_data)
        
        # Update last accessed time
        session["last_accessed"] = datetime.utcnow().isoformat()
        await self.redis_client.setex(
            session_key,
            timedelta(hours=self.expire_hours),
            json.dumps(session)
        )
        
        return session
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        session_key = f"{self.session_prefix}{session_id}"
        result = await self.redis_client.delete(session_key)
        return result > 0
    
    async def refresh_session(self, session_id: str) -> bool:
        """Refresh session expiration"""
        session_key = f"{self.session_prefix}{session_id}"
        session_data = await self.redis_client.get(session_key)
        
        if not session_data:
            return False
        
        # Extend session expiration
        await self.redis_client.setex(
            session_key,
            timedelta(hours=self.expire_hours),
            session_data
        )
        
        return True
    
    async def get_user_sessions(self, user_id: int) -> list:
        """Get all active sessions for a user"""
        sessions = []
        pattern = f"{self.session_prefix}*"
        
        async for key in self.redis_client.scan_iter(match=pattern):
            session_data = await self.redis_client.get(key)
            if session_data:
                session = json.loads(session_data)
                if session.get("user_id") == user_id:
                    session_id = key.replace(self.session_prefix, "")
                    sessions.append({
                        "session_id": session_id,
                        "created_at": session.get("created_at"),
                        "last_accessed": session.get("last_accessed")
                    })
        
        return sessions
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions (Redis handles this automatically)"""
        # Redis automatically expires keys, but we can add custom cleanup logic here
        pass


# Global session manager instance
session_manager = SessionManager()
