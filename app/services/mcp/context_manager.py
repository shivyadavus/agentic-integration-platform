"""
Context manager for Model Context Protocol implementation.

This module provides persistent context management across AI conversations,
maintaining state, memory, and contextual information for integration sessions.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict

from app.core.logging import LoggerMixin
from app.core.exceptions import ValidationError


@dataclass
class ContextItem:
    """Represents a single context item."""
    
    id: str
    type: str  # "message", "tool_result", "integration", "entity", "pattern"
    content: Any
    timestamp: datetime
    importance: float = 1.0  # 0.0 to 1.0
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        if self.expires_at:
            data["expires_at"] = self.expires_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContextItem":
        """Create from dictionary."""
        data = data.copy()
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        if data.get("expires_at"):
            data["expires_at"] = datetime.fromisoformat(data["expires_at"])
        return cls(**data)
    
    def is_expired(self) -> bool:
        """Check if context item has expired."""
        return self.expires_at is not None and datetime.utcnow() > self.expires_at


@dataclass
class ContextWindow:
    """Represents a context window with size and retention policies."""
    
    max_items: int = 100
    max_age_hours: int = 24
    importance_threshold: float = 0.1
    
    def should_retain(self, item: ContextItem) -> bool:
        """Check if an item should be retained in context."""
        if item.is_expired():
            return False
        
        if item.importance < self.importance_threshold:
            return False
        
        age = datetime.utcnow() - item.timestamp
        if age > timedelta(hours=self.max_age_hours):
            return False
        
        return True


class ContextManager(LoggerMixin):
    """
    Manages persistent context for AI conversations.
    
    Provides context storage, retrieval, summarization, and cleanup
    with configurable retention policies and importance scoring.
    """
    
    def __init__(self, session_id: str, context_window: Optional[ContextWindow] = None):
        """
        Initialize context manager.
        
        Args:
            session_id: Unique session identifier
            context_window: Context retention configuration
        """
        self.session_id = session_id
        self.context_window = context_window or ContextWindow()
        self._context_items: List[ContextItem] = []
        self._summary: Optional[str] = None
        self._last_cleanup = datetime.utcnow()
    
    def add_context(
        self,
        content: Any,
        context_type: str,
        importance: float = 1.0,
        expires_in_hours: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a context item.
        
        Args:
            content: Context content
            context_type: Type of context
            importance: Importance score (0.0 to 1.0)
            expires_in_hours: Hours until expiration
            metadata: Additional metadata
            
        Returns:
            str: Context item ID
        """
        item_id = str(uuid.uuid4())
        expires_at = None
        
        if expires_in_hours:
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        item = ContextItem(
            id=item_id,
            type=context_type,
            content=content,
            timestamp=datetime.utcnow(),
            importance=importance,
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        self._context_items.append(item)
        
        # Trigger cleanup if needed
        self._maybe_cleanup()
        
        self.logger.debug(
            f"Added context item: {item_id}",
            type=context_type,
            importance=importance,
            session_id=self.session_id
        )
        
        return item_id
    
    def get_context(
        self,
        context_type: Optional[str] = None,
        min_importance: float = 0.0,
        limit: Optional[int] = None
    ) -> List[ContextItem]:
        """
        Get context items matching criteria.
        
        Args:
            context_type: Filter by context type
            min_importance: Minimum importance threshold
            limit: Maximum number of items
            
        Returns:
            List[ContextItem]: Matching context items
        """
        items = []
        
        for item in self._context_items:
            if item.is_expired():
                continue
            
            if context_type and item.type != context_type:
                continue
            
            if item.importance < min_importance:
                continue
            
            items.append(item)
        
        # Sort by importance and recency
        items.sort(
            key=lambda x: (x.importance, x.timestamp),
            reverse=True
        )
        
        if limit:
            items = items[:limit]
        
        return items
    
    def get_recent_context(
        self,
        hours: int = 1,
        context_type: Optional[str] = None
    ) -> List[ContextItem]:
        """
        Get recent context items.
        
        Args:
            hours: Hours to look back
            context_type: Filter by context type
            
        Returns:
            List[ContextItem]: Recent context items
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        items = []
        for item in self._context_items:
            if item.timestamp >= cutoff:
                if context_type is None or item.type == context_type:
                    items.append(item)
        
        return sorted(items, key=lambda x: x.timestamp, reverse=True)
    
    def update_context_importance(self, item_id: str, importance: float) -> bool:
        """
        Update the importance of a context item.
        
        Args:
            item_id: Context item ID
            importance: New importance score
            
        Returns:
            bool: True if updated successfully
        """
        for item in self._context_items:
            if item.id == item_id:
                item.importance = importance
                self.logger.debug(f"Updated context importance: {item_id} -> {importance}")
                return True
        
        return False
    
    def remove_context(self, item_id: str) -> bool:
        """
        Remove a context item.
        
        Args:
            item_id: Context item ID
            
        Returns:
            bool: True if removed successfully
        """
        for i, item in enumerate(self._context_items):
            if item.id == item_id:
                del self._context_items[i]
                self.logger.debug(f"Removed context item: {item_id}")
                return True
        
        return False
    
    def clear_context(self, context_type: Optional[str] = None) -> int:
        """
        Clear context items.
        
        Args:
            context_type: Optional type filter
            
        Returns:
            int: Number of items cleared
        """
        if context_type is None:
            count = len(self._context_items)
            self._context_items.clear()
            self._summary = None
        else:
            original_count = len(self._context_items)
            self._context_items = [
                item for item in self._context_items
                if item.type != context_type
            ]
            count = original_count - len(self._context_items)
        
        self.logger.info(f"Cleared {count} context items", type=context_type)
        return count
    
    def get_context_summary(self, max_length: int = 1000) -> str:
        """
        Get a summary of the current context.
        
        Args:
            max_length: Maximum summary length
            
        Returns:
            str: Context summary
        """
        if not self._context_items:
            return "No context available."
        
        # Get high-importance items
        important_items = self.get_context(min_importance=0.7, limit=20)
        
        if not important_items:
            important_items = self.get_context(limit=10)
        
        summary_parts = []
        
        # Group by type
        by_type: Dict[str, List[ContextItem]] = {}
        for item in important_items:
            if item.type not in by_type:
                by_type[item.type] = []
            by_type[item.type].append(item)
        
        # Create summary for each type
        for context_type, items in by_type.items():
            if context_type == "message":
                # Summarize recent messages
                recent_messages = [
                    str(item.content) for item in items[-5:]
                ]
                if recent_messages:
                    summary_parts.append(
                        f"Recent conversation: {' | '.join(recent_messages)}"
                    )
            
            elif context_type == "integration":
                # Summarize integrations
                integrations = [
                    f"{item.metadata.get('name', 'Unknown')}" for item in items
                ]
                if integrations:
                    summary_parts.append(
                        f"Working on integrations: {', '.join(integrations)}"
                    )
            
            elif context_type == "entity":
                # Summarize entities
                entities = [
                    f"{item.metadata.get('name', 'Unknown')}" for item in items
                ]
                if entities:
                    summary_parts.append(
                        f"Referenced entities: {', '.join(entities)}"
                    )
            
            else:
                # Generic summary
                summary_parts.append(
                    f"{context_type.title()}: {len(items)} items"
                )
        
        summary = ". ".join(summary_parts)
        
        # Truncate if too long
        if len(summary) > max_length:
            summary = summary[:max_length - 3] + "..."
        
        return summary
    
    def _maybe_cleanup(self) -> None:
        """Perform cleanup if needed."""
        now = datetime.utcnow()
        
        # Cleanup every 10 minutes
        if now - self._last_cleanup < timedelta(minutes=10):
            return
        
        self._cleanup()
        self._last_cleanup = now
    
    def _cleanup(self) -> None:
        """Clean up expired and low-importance context items."""
        original_count = len(self._context_items)
        
        # Remove expired items
        self._context_items = [
            item for item in self._context_items
            if self.context_window.should_retain(item)
        ]
        
        # Limit by max items
        if len(self._context_items) > self.context_window.max_items:
            # Sort by importance and recency, keep the best
            self._context_items.sort(
                key=lambda x: (x.importance, x.timestamp),
                reverse=True
            )
            self._context_items = self._context_items[:self.context_window.max_items]
        
        removed_count = original_count - len(self._context_items)
        
        if removed_count > 0:
            self.logger.debug(
                f"Cleaned up {removed_count} context items",
                remaining=len(self._context_items)
            )
    
    def export_context(self) -> Dict[str, Any]:
        """
        Export context for persistence.
        
        Returns:
            Dict[str, Any]: Serializable context data
        """
        return {
            "session_id": self.session_id,
            "context_window": asdict(self.context_window),
            "context_items": [item.to_dict() for item in self._context_items],
            "summary": self._summary,
            "last_cleanup": self._last_cleanup.isoformat(),
        }
    
    def import_context(self, data: Dict[str, Any]) -> None:
        """
        Import context from persistence.
        
        Args:
            data: Context data to import
        """
        self.session_id = data["session_id"]
        
        if "context_window" in data:
            self.context_window = ContextWindow(**data["context_window"])
        
        self._context_items = [
            ContextItem.from_dict(item_data)
            for item_data in data.get("context_items", [])
        ]
        
        self._summary = data.get("summary")
        
        if "last_cleanup" in data:
            self._last_cleanup = datetime.fromisoformat(data["last_cleanup"])
        
        # Cleanup after import
        self._cleanup()
        
        self.logger.info(
            f"Imported context for session {self.session_id}",
            items=len(self._context_items)
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get context statistics.
        
        Returns:
            Dict[str, Any]: Context statistics
        """
        by_type: Dict[str, int] = {}
        total_importance = 0.0
        
        for item in self._context_items:
            by_type[item.type] = by_type.get(item.type, 0) + 1
            total_importance += item.importance
        
        avg_importance = (
            total_importance / len(self._context_items)
            if self._context_items else 0.0
        )
        
        return {
            "session_id": self.session_id,
            "total_items": len(self._context_items),
            "items_by_type": by_type,
            "average_importance": avg_importance,
            "oldest_item": (
                min(item.timestamp for item in self._context_items).isoformat()
                if self._context_items else None
            ),
            "newest_item": (
                max(item.timestamp for item in self._context_items).isoformat()
                if self._context_items else None
            ),
        }
