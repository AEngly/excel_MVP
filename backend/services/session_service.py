"""
Session Service - Manage PDF sessions and embeddings in memory
"""
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# In-memory session storage
# For production, use Redis or database
sessions: Dict[str, Dict[str, Any]] = {}

# Session expiry time (24 hours)
SESSION_EXPIRY = timedelta(hours=24)


def create_session(pdf_text: str, pdf_data: dict, embeddings_data: dict) -> str:
    """
    Create a new PDF session with embeddings

    Args:
        pdf_text: Full extracted PDF text
        pdf_data: Processed PDF data (summary, model data)
        embeddings_data: Chunks and embeddings

    Returns:
        Session ID (UUID)
    """
    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "pdf_text": pdf_text,
        "pdf_data": pdf_data,
        "chunks": embeddings_data["chunks"],
        "embeddings": embeddings_data["embeddings"],
        "chunk_count": embeddings_data["chunk_count"],
        "created_at": datetime.now(),
        "last_accessed": datetime.now()
    }

    print(f"📦 Created session {session_id[:8]}... with {embeddings_data['chunk_count']} chunks")

    return session_id


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve session data by ID

    Args:
        session_id: Session UUID

    Returns:
        Session data or None if not found/expired
    """
    if session_id not in sessions:
        return None

    session = sessions[session_id]

    # Check if expired
    if datetime.now() - session["created_at"] > SESSION_EXPIRY:
        del sessions[session_id]
        print(f"🗑️  Session {session_id[:8]}... expired and deleted")
        return None

    # Update last accessed time
    session["last_accessed"] = datetime.now()

    return session


def delete_session(session_id: str) -> bool:
    """
    Delete a session

    Args:
        session_id: Session UUID

    Returns:
        True if deleted, False if not found
    """
    if session_id in sessions:
        del sessions[session_id]
        print(f"🗑️  Session {session_id[:8]}... deleted")
        return True
    return False


def cleanup_expired_sessions():
    """
    Remove expired sessions (run periodically)
    """
    now = datetime.now()
    expired = [
        sid for sid, session in sessions.items()
        if now - session["created_at"] > SESSION_EXPIRY
    ]

    for sid in expired:
        del sessions[sid]

    if expired:
        print(f"🗑️  Cleaned up {len(expired)} expired sessions")


def get_session_count() -> int:
    """
    Get total number of active sessions
    """
    return len(sessions)
