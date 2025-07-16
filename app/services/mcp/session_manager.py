"""
Session manager for Model Context Protocol implementation.

This module manages conversation sessions, context persistence,
and session lifecycle for the agentic integration platform.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.models.ai import ConversationSession, ConversationStatus
from app.services.mcp.context_manager import ContextManager
from app.services.mcp.conversation_service import ConversationService
from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import LoggerMixin


class SessionManager(LoggerMixin):
    """
    Manages conversation sessions and context persistence.
    
    Provides session lifecycle management, context serialization,
    and cleanup for the Model Context Protocol implementation.
    """
    
    def __init__(
        self,
        conversation_service: Optional[ConversationService] = None,
        persistence_dir: Optional[Path] = None
    ):
        """
        Initialize session manager.
        
        Args:
            conversation_service: Conversation service
            persistence_dir: Directory for context persistence
        """
        self.conversation_service = conversation_service or ConversationService()
        self.persistence_dir = persistence_dir or Path("./data/sessions")
        self.persistence_dir.mkdir(parents=True, exist_ok=True)
        
        # Active sessions cache
        self._active_sessions: Dict[str, ConversationSession] = {}
        self._context_managers: Dict[str, ContextManager] = {}
    
    async def create_session(
        self,
        db: AsyncSession,
        user_id: Optional[uuid.UUID] = None,
        title: Optional[str] = None,
        system_prompt: Optional[str] = None,
        integration_id: Optional[uuid.UUID] = None,
        **kwargs: Any
    ) -> ConversationSession:
        """
        Create a new conversation session.
        
        Args:
            db: Database session
            user_id: User ID
            title: Session title
            system_prompt: System prompt
            integration_id: Associated integration ID
            **kwargs: Additional session properties
            
        Returns:
            ConversationSession: Created session
        """
        session = await self.conversation_service.create_conversation(
            db=db,
            user_id=user_id,
            title=title,
            system_prompt=system_prompt,
            integration_id=integration_id,
            **kwargs
        )
        
        # Add to active sessions
        self._active_sessions[str(session.id)] = session
        
        # Initialize context manager
        context_manager = ContextManager(session_id=str(session.id))
        self._context_managers[str(session.id)] = context_manager
        
        self.logger.info(
            f"Created session: {session.id}",
            user_id=str(user_id) if user_id else None,
            title=title
        )
        
        return session
    
    async def get_session(
        self,
        db: AsyncSession,
        session_id: uuid.UUID
    ) -> ConversationSession:
        """
        Get a session by ID.
        
        Args:
            db: Database session
            session_id: Session ID
            
        Returns:
            ConversationSession: The session
        """
        session_str = str(session_id)
        
        # Check cache first
        if session_str in self._active_sessions:
            return self._active_sessions[session_str]
        
        # Load from database
        session = await self.conversation_service.get_conversation(db, session_id)
        
        # Add to cache
        self._active_sessions[session_str] = session
        
        # Load or create context manager
        if session_str not in self._context_managers:
            context_manager = ContextManager(session_id=session_str)
            
            # Try to load persisted context
            await self._load_session_context(session_str, context_manager)
            
            self._context_managers[session_str] = context_manager
        
        return session
    
    async def update_session(
        self,
        db: AsyncSession,
        session_id: uuid.UUID,
        **updates: Any
    ) -> ConversationSession:
        """
        Update a session.
        
        Args:
            db: Database session
            session_id: Session ID
            **updates: Fields to update
            
        Returns:
            ConversationSession: Updated session
        """
        session = await self.get_session(db, session_id)
        
        # Update fields
        for field, value in updates.items():
            if hasattr(session, field):
                setattr(session, field, value)
        
        session.updated_at = datetime.utcnow()
        
        await db.commit()
        
        # Update cache
        self._active_sessions[str(session_id)] = session
        
        self.logger.info(f"Updated session: {session_id}")
        return session
    
    async def close_session(
        self,
        db: AsyncSession,
        session_id: uuid.UUID,
        save_context: bool = True
    ) -> None:
        """
        Close a session.
        
        Args:
            db: Database session
            session_id: Session ID
            save_context: Whether to save context to disk
        """
        session_str = str(session_id)
        
        # Update session status
        await self.conversation_service.update_conversation_status(
            db, session_id, ConversationStatus.COMPLETED
        )
        
        # Save context if requested
        if save_context and session_str in self._context_managers:
            await self._save_session_context(
                session_str,
                self._context_managers[session_str]
            )
        
        # Remove from cache
        self._active_sessions.pop(session_str, None)
        self._context_managers.pop(session_str, None)
        
        self.logger.info(f"Closed session: {session_id}")
    
    async def archive_session(
        self,
        db: AsyncSession,
        session_id: uuid.UUID
    ) -> None:
        """
        Archive a session.
        
        Args:
            db: Database session
            session_id: Session ID
        """
        await self.conversation_service.update_conversation_status(
            db, session_id, ConversationStatus.ARCHIVED
        )
        
        # Save context before archiving
        session_str = str(session_id)
        if session_str in self._context_managers:
            await self._save_session_context(
                session_str,
                self._context_managers[session_str]
            )
        
        # Remove from active cache
        self._active_sessions.pop(session_str, None)
        self._context_managers.pop(session_str, None)
        
        self.logger.info(f"Archived session: {session_id}")
    
    async def list_user_sessions(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        status: Optional[ConversationStatus] = None,
        limit: int = 50
    ) -> List[ConversationSession]:
        """
        List sessions for a user.
        
        Args:
            db: Database session
            user_id: User ID
            status: Optional status filter
            limit: Maximum results
            
        Returns:
            List[ConversationSession]: User sessions
        """
        query = (
            select(ConversationSession)
            .where(ConversationSession.user_id == user_id)
            .order_by(ConversationSession.updated_at.desc())
            .limit(limit)
        )
        
        if status:
            query = query.where(ConversationSession.status == status)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_active_sessions(self) -> List[str]:
        """
        Get list of active session IDs.
        
        Returns:
            List[str]: Active session IDs
        """
        return list(self._active_sessions.keys())
    
    async def cleanup_expired_sessions(
        self,
        db: AsyncSession,
        max_age_hours: int = 24
    ) -> int:
        """
        Clean up expired sessions.
        
        Args:
            db: Database session
            max_age_hours: Maximum session age in hours
            
        Returns:
            int: Number of sessions cleaned up
        """
        cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        # Find expired sessions
        query = (
            select(ConversationSession)
            .where(ConversationSession.updated_at < cutoff)
            .where(ConversationSession.status == ConversationStatus.ACTIVE)
        )
        
        result = await db.execute(query)
        expired_sessions = result.scalars().all()
        
        cleanup_count = 0
        
        for session in expired_sessions:
            try:
                await self.close_session(db, session.id, save_context=True)
                cleanup_count += 1
            except Exception as e:
                self.logger.error(
                    f"Failed to cleanup session {session.id}",
                    error=str(e)
                )
        
        self.logger.info(f"Cleaned up {cleanup_count} expired sessions")
        return cleanup_count
    
    async def _save_session_context(
        self,
        session_id: str,
        context_manager: ContextManager
    ) -> None:
        """
        Save session context to disk.
        
        Args:
            session_id: Session ID
            context_manager: Context manager to save
        """
        try:
            context_file = self.persistence_dir / f"{session_id}.json"
            context_data = context_manager.export_context()
            
            with open(context_file, "w") as f:
                json.dump(context_data, f, indent=2)
            
            self.logger.debug(f"Saved context for session: {session_id}")
            
        except Exception as e:
            self.logger.error(
                f"Failed to save context for session {session_id}",
                error=str(e)
            )
    
    async def _load_session_context(
        self,
        session_id: str,
        context_manager: ContextManager
    ) -> None:
        """
        Load session context from disk.
        
        Args:
            session_id: Session ID
            context_manager: Context manager to populate
        """
        try:
            context_file = self.persistence_dir / f"{session_id}.json"
            
            if context_file.exists():
                with open(context_file, "r") as f:
                    context_data = json.load(f)
                
                context_manager.import_context(context_data)
                
                self.logger.debug(f"Loaded context for session: {session_id}")
            
        except Exception as e:
            self.logger.error(
                f"Failed to load context for session {session_id}",
                error=str(e)
            )
    
    async def get_session_statistics(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Get session statistics.
        
        Args:
            db: Database session
            
        Returns:
            Dict[str, Any]: Session statistics
        """
        # Total sessions
        total_query = select(ConversationSession)
        total_result = await db.execute(total_query)
        total_sessions = len(total_result.scalars().all())
        
        # Active sessions
        active_query = (
            select(ConversationSession)
            .where(ConversationSession.status == ConversationStatus.ACTIVE)
        )
        active_result = await db.execute(active_query)
        active_sessions = len(active_result.scalars().all())
        
        # Sessions by status
        from sqlalchemy import func
        status_query = (
            select(ConversationSession.status, func.count(ConversationSession.id))
            .group_by(ConversationSession.status)
        )
        status_result = await db.execute(status_query)
        status_counts = {
            status.value: count
            for status, count in status_result.all()
        }
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "cached_sessions": len(self._active_sessions),
            "status_distribution": status_counts,
            "context_managers": len(self._context_managers),
        }
    
    async def export_session(
        self,
        db: AsyncSession,
        session_id: uuid.UUID
    ) -> Dict[str, Any]:
        """
        Export a complete session with context.
        
        Args:
            db: Database session
            session_id: Session ID
            
        Returns:
            Dict[str, Any]: Complete session data
        """
        session = await self.get_session(db, session_id)
        session_str = str(session_id)
        
        # Get context if available
        context_data = None
        if session_str in self._context_managers:
            context_data = self._context_managers[session_str].export_context()
        
        return {
            "session": {
                "id": str(session.id),
                "title": session.title,
                "status": session.status.value,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "message_count": session.message_count,
                "total_tokens_used": session.total_tokens_used,
                "user_id": str(session.user_id) if session.user_id else None,
                "integration_id": str(session.integration_id) if session.integration_id else None,
            },
            "messages": [
                {
                    "id": str(msg.id),
                    "role": msg.role.value,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                    "input_tokens": msg.input_tokens,
                    "output_tokens": msg.output_tokens,
                }
                for msg in session.messages
            ],
            "context": context_data,
        }


# Global session manager instance
session_manager = SessionManager()
