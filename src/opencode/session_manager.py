"""
OpenCode session management.
"""

import json
import os
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SessionInfo:
    """OpenCode session information."""
    session_id: str
    name: str
    model: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    messages: int = 0
    tokens_used: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "name": self.name,
            "model": self.model,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "messages": self.messages,
            "tokens_used": self.tokens_used,
            "metadata": self.metadata
        }


class SessionManager:
    """Manage OpenCode sessions."""
    
    def __init__(self, sessions_dir: str = "~/.opencode/sessions"):
        self.sessions_dir = os.path.expanduser(sessions_dir)
        self.sessions: Dict[str, SessionInfo] = {}
        self._load_sessions()
    
    def _load_sessions(self):
        """Load sessions from disk."""
        if not os.path.exists(self.sessions_dir):
            os.makedirs(self.sessions_dir, exist_ok=True)
            return
        
        try:
            for filename in os.listdir(self.sessions_dir):
                if filename.endswith(".json"):
                    filepath = os.path.join(self.sessions_dir, filename)
                    with open(filepath, "r") as f:
                        data = json.load(f)
                        session = SessionInfo(
                            session_id=data["session_id"],
                            name=data["name"],
                            model=data["model"],
                            created_at=datetime.fromisoformat(data["created_at"]),
                            updated_at=datetime.fromisoformat(data["updated_at"]),
                            messages=data.get("messages", 0),
                            tokens_used=data.get("tokens_used", 0),
                            metadata=data.get("metadata", {})
                        )
                        self.sessions[session.session_id] = session
        except Exception as e:
            print(f"⚠️  Failed to load sessions: {e}")
    
    def _save_session(self, session: SessionInfo):
        """Save session to disk."""
        os.makedirs(self.sessions_dir, exist_ok=True)
        
        try:
            filepath = os.path.join(self.sessions_dir, f"{session.session_id}.json")
            with open(filepath, "w") as f:
                json.dump(session.to_dict(), f, indent=2)
        except Exception as e:
            print(f"❌ Failed to save session: {e}")
    
    def create_session(
        self,
        session_id: str,
        name: str,
        model: str,
        metadata: Dict[str, Any] = None
    ) -> SessionInfo:
        """Create new session."""
        session = SessionInfo(
            session_id=session_id,
            name=name,
            model=model,
            metadata=metadata or {}
        )
        self.sessions[session_id] = session
        self._save_session(session)
        return session
    
    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Get session."""
        return self.sessions.get(session_id)
    
    def list_sessions(self) -> List[SessionInfo]:
        """List all sessions."""
        return list(self.sessions.values())
    
    def update_session(
        self,
        session_id: str,
        messages: int = None,
        tokens_used: int = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[SessionInfo]:
        """Update session."""
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        if messages is not None:
            session.messages = messages
        if tokens_used is not None:
            session.tokens_used = tokens_used
        if metadata is not None:
            session.metadata.update(metadata)
        
        session.updated_at = datetime.now()
        self._save_session(session)
        return session
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            filepath = os.path.join(self.sessions_dir, f"{session_id}.json")
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as e:
                print(f"⚠️  Failed to delete session file: {e}")
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        total_messages = sum(s.messages for s in self.sessions.values())
        total_tokens = sum(s.tokens_used for s in self.sessions.values())
        
        return {
            "total_sessions": len(self.sessions),
            "total_messages": total_messages,
            "total_tokens_used": total_tokens,
            "average_messages_per_session": (
                total_messages / len(self.sessions) if self.sessions else 0
            ),
            "average_tokens_per_session": (
                total_tokens / len(self.sessions) if self.sessions else 0
            )
        }
