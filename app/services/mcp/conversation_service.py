"""
Conversation service for Model Context Protocol implementation.

This module manages AI conversations with persistent context, tool integration,
and conversational continuity across sessions.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.ai import ConversationSession, Message, MessageRole, ConversationStatus
from app.models.user import User
from app.services.ai.base import AIService, AIMessage, AIModelConfig
from app.services.ai.factory import AIServiceFactory
from app.services.mcp.context_manager import ContextManager
from app.services.mcp.tool_registry import ToolRegistry
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import LoggerMixin


class ConversationService(LoggerMixin):
    """
    Service for managing AI conversations with MCP support.
    
    Provides conversation lifecycle management, context persistence,
    and tool integration for the agentic integration platform.
    """
    
    def __init__(
        self,
        ai_service: Optional[AIService] = None,
        tool_registry: Optional[ToolRegistry] = None
    ):
        """
        Initialize conversation service.
        
        Args:
            ai_service: AI service for generating responses
            tool_registry: Tool registry for function calls
        """
        self.ai_service = ai_service or AIServiceFactory.get_default_service()
        self.tool_registry = tool_registry or ToolRegistry()
        self._context_managers: Dict[str, ContextManager] = {}
    
    async def create_conversation(
        self,
        db: AsyncSession,
        user_id: Optional[uuid.UUID] = None,
        title: Optional[str] = None,
        system_prompt: Optional[str] = None,
        integration_id: Optional[uuid.UUID] = None,
        ai_model_id: Optional[uuid.UUID] = None,
        **kwargs: Any
    ) -> ConversationSession:
        """
        Create a new conversation session.
        
        Args:
            db: Database session
            user_id: User ID
            title: Conversation title
            system_prompt: System prompt
            integration_id: Associated integration ID
            ai_model_id: AI model ID
            **kwargs: Additional conversation properties
            
        Returns:
            ConversationSession: Created conversation
        """
        conversation = ConversationSession(
            title=title,
            system_prompt=system_prompt,
            user_id=user_id,
            integration_id=integration_id,
            ai_model_id=ai_model_id,
            **kwargs
        )
        
        db.add(conversation)
        await db.flush()  # Get the ID
        
        # Initialize context manager
        context_manager = ContextManager(session_id=str(conversation.id))
        self._context_managers[str(conversation.id)] = context_manager
        
        # Add system prompt to context if provided
        if system_prompt:
            context_manager.add_context(
                content=system_prompt,
                context_type="system_prompt",
                importance=1.0
            )
        
        await db.commit()
        
        self.logger.info(
            f"Created conversation: {conversation.id}",
            user_id=str(user_id) if user_id else None,
            title=title
        )
        
        return conversation
    
    async def get_conversation(
        self,
        db: AsyncSession,
        conversation_id: uuid.UUID
    ) -> ConversationSession:
        """
        Get a conversation by ID.
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            
        Returns:
            ConversationSession: The conversation
            
        Raises:
            NotFoundError: If conversation not found
        """
        query = (
            select(ConversationSession)
            .where(ConversationSession.id == conversation_id)
            .options(selectinload(ConversationSession.messages))
        )
        
        result = await db.execute(query)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise NotFoundError(
                f"Conversation not found: {conversation_id}",
                resource_type="conversation"
            )
        
        # Initialize context manager if not exists
        if str(conversation_id) not in self._context_managers:
            context_manager = ContextManager(session_id=str(conversation_id))
            self._context_managers[str(conversation_id)] = context_manager
            
            # Load existing messages into context
            await self._load_conversation_context(conversation, context_manager)
        
        return conversation
    
    async def _load_conversation_context(
        self,
        conversation: ConversationSession,
        context_manager: ContextManager
    ) -> None:
        """
        Load existing conversation messages into context.
        
        Args:
            conversation: Conversation session
            context_manager: Context manager to populate
        """
        for message in conversation.messages:
            importance = 0.8 if message.role == MessageRole.USER else 0.6
            
            context_manager.add_context(
                content={
                    "role": message.role.value,
                    "content": message.content,
                    "function_name": message.function_name,
                    "function_arguments": message.function_arguments,
                },
                context_type="message",
                importance=importance,
                metadata={
                    "message_id": str(message.id),
                    "created_at": message.created_at.isoformat(),
                    "tokens": message.total_tokens,
                }
            )
    
    async def send_message(
        self,
        db: AsyncSession,
        conversation_id: uuid.UUID,
        content: str,
        role: MessageRole = MessageRole.USER,
        function_name: Optional[str] = None,
        function_arguments: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Message:
        """
        Send a message in a conversation.
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            content: Message content
            role: Message role
            function_name: Function name for function calls
            function_arguments: Function arguments
            **kwargs: Additional message properties
            
        Returns:
            Message: Created message
        """
        conversation = await self.get_conversation(db, conversation_id)
        
        # Create message
        message = Message(
            conversation_session_id=conversation_id,
            role=role,
            content=content,
            function_name=function_name,
            function_arguments=function_arguments,
            **kwargs
        )
        
        db.add(message)
        conversation.message_count += 1
        
        # Add to context
        context_manager = self._context_managers[str(conversation_id)]
        importance = 0.9 if role == MessageRole.USER else 0.7
        
        context_manager.add_context(
            content={
                "role": role.value,
                "content": content,
                "function_name": function_name,
                "function_arguments": function_arguments,
            },
            context_type="message",
            importance=importance,
            metadata={
                "message_id": str(message.id),
                "created_at": datetime.utcnow().isoformat(),
            }
        )
        
        await db.commit()
        
        self.logger.debug(
            f"Added message to conversation: {conversation_id}",
            role=role.value,
            content_length=len(content)
        )
        
        return message
    
    async def generate_response(
        self,
        db: AsyncSession,
        conversation_id: uuid.UUID,
        user_message: str,
        use_tools: bool = True,
        stream: bool = False
    ) -> Message:
        """
        Generate AI response for a conversation.
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            user_message: User's message
            use_tools: Whether to use available tools
            stream: Whether to stream the response
            
        Returns:
            Message: AI response message
        """
        conversation = await self.get_conversation(db, conversation_id)
        context_manager = self._context_managers[str(conversation_id)]
        
        # Add user message
        await self.send_message(
            db, conversation_id, user_message, MessageRole.USER
        )
        
        # Prepare AI messages
        ai_messages = await self._prepare_ai_messages(conversation, context_manager)
        
        # Prepare AI configuration
        config = AIModelConfig(
            model=self.ai_service.default_model,
            temperature=conversation.temperature,
            max_tokens=conversation.max_tokens,
            system_prompt=conversation.system_prompt,
        )
        
        # Add tools if enabled
        if use_tools:
            config.functions = self.tool_registry.get_function_definitions()
            config.function_call = "auto"
        
        try:
            # Generate response
            if stream:
                return await self._generate_streaming_response(
                    db, conversation, ai_messages, config, context_manager
                )
            else:
                return await self._generate_single_response(
                    db, conversation, ai_messages, config, context_manager
                )
        
        except Exception as e:
            self.logger.error(
                f"Failed to generate response for conversation {conversation_id}",
                error=str(e),
                exc_info=True
            )
            
            # Create error message
            error_message = await self.send_message(
                db,
                conversation_id,
                f"I encountered an error: {str(e)}",
                MessageRole.ASSISTANT
            )
            
            return error_message
    
    async def _prepare_ai_messages(
        self,
        conversation: ConversationSession,
        context_manager: ContextManager
    ) -> List[AIMessage]:
        """
        Prepare messages for AI request.
        
        Args:
            conversation: Conversation session
            context_manager: Context manager
            
        Returns:
            List[AIMessage]: Prepared AI messages
        """
        ai_messages = []
        
        # Add system prompt if available
        if conversation.system_prompt:
            ai_messages.append(AIMessage(
                role="system",
                content=conversation.system_prompt
            ))
        
        # Get recent context messages
        context_messages = context_manager.get_context(
            context_type="message",
            limit=20  # Last 20 messages
        )
        
        # Convert to AI messages
        for context_item in reversed(context_messages):  # Chronological order
            message_data = context_item.content
            ai_messages.append(AIMessage(
                role=message_data["role"],
                content=message_data["content"],
                function_name=message_data.get("function_name"),
                function_arguments=message_data.get("function_arguments"),
            ))
        
        return ai_messages
    
    async def _generate_single_response(
        self,
        db: AsyncSession,
        conversation: ConversationSession,
        ai_messages: List[AIMessage],
        config: AIModelConfig,
        context_manager: ContextManager
    ) -> Message:
        """Generate a single AI response."""
        response = await self.ai_service.generate_response(ai_messages, config)
        
        # Handle function calls
        if response.function_calls:
            for function_call in response.function_calls:
                # Execute tool
                tool_result = await self.tool_registry.execute_tool(
                    function_call["name"],
                    function_call.get("arguments", {})
                )
                
                # Add tool result to context
                context_manager.add_context(
                    content=tool_result,
                    context_type="tool_result",
                    importance=0.8,
                    metadata={
                        "function_name": function_call["name"],
                        "arguments": function_call.get("arguments", {}),
                    }
                )
        
        # Create response message
        response_message = Message(
            conversation_session_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=response.content,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            processing_time_ms=response.processing_time_ms,
            model_used=response.model
        )

        db.add(response_message)
        conversation.message_count += 1

        # Add to context
        context_manager.add_context(
            content={
                "role": MessageRole.ASSISTANT.value,
                "content": response.content,
            },
            context_type="message",
            importance=0.7,
            metadata={
                "message_id": str(response_message.id),
                "created_at": datetime.utcnow().isoformat(),
                "tokens": response.total_tokens,
            }
        )
        
        # Update conversation statistics
        conversation.total_tokens_used += response.total_tokens
        await db.commit()
        
        return response_message
    
    async def _generate_streaming_response(
        self,
        db: AsyncSession,
        conversation: ConversationSession,
        ai_messages: List[AIMessage],
        config: AIModelConfig,
        context_manager: ContextManager
    ) -> Message:
        """Generate a streaming AI response."""
        # For now, fall back to single response
        # TODO: Implement true streaming with incremental message updates
        return await self._generate_single_response(
            db, conversation, ai_messages, config, context_manager
        )
    
    async def update_conversation_status(
        self,
        db: AsyncSession,
        conversation_id: uuid.UUID,
        status: ConversationStatus
    ) -> ConversationSession:
        """
        Update conversation status.
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            status: New status
            
        Returns:
            ConversationSession: Updated conversation
        """
        conversation = await self.get_conversation(db, conversation_id)
        conversation.status = status
        
        await db.commit()
        
        self.logger.info(
            f"Updated conversation status: {conversation_id} -> {status.value}"
        )
        
        return conversation
    
    async def get_conversation_context_summary(
        self,
        conversation_id: uuid.UUID
    ) -> str:
        """
        Get context summary for a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            str: Context summary
        """
        context_manager = self._context_managers.get(str(conversation_id))
        
        if not context_manager:
            return "No context available."
        
        return context_manager.get_context_summary()
    
    async def add_conversation_context(
        self,
        conversation_id: uuid.UUID,
        content: Any,
        context_type: str,
        importance: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add context to a conversation.
        
        Args:
            conversation_id: Conversation ID
            content: Context content
            context_type: Type of context
            importance: Importance score
            metadata: Additional metadata
            
        Returns:
            str: Context item ID
        """
        context_manager = self._context_managers.get(str(conversation_id))
        
        if not context_manager:
            context_manager = ContextManager(session_id=str(conversation_id))
            self._context_managers[str(conversation_id)] = context_manager
        
        return context_manager.add_context(
            content=content,
            context_type=context_type,
            importance=importance,
            metadata=metadata
        )
    
    async def cleanup_conversation_context(
        self,
        conversation_id: uuid.UUID
    ) -> None:
        """
        Clean up conversation context.
        
        Args:
            conversation_id: Conversation ID
        """
        context_manager = self._context_managers.get(str(conversation_id))
        
        if context_manager:
            context_manager._cleanup()
            self.logger.debug(f"Cleaned up context for conversation: {conversation_id}")
    
    def get_active_conversations(self) -> List[str]:
        """
        Get list of active conversation IDs.
        
        Returns:
            List[str]: Active conversation IDs
        """
        return list(self._context_managers.keys())
