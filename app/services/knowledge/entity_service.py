"""
Entity service for managing knowledge graph entities.

This module provides high-level operations for creating, updating, and querying
entities in the knowledge graph with semantic understanding.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.models.knowledge import Entity, EntityType, Relationship, RelationshipType
from app.services.knowledge.graph_service import knowledge_graph_service
from app.services.knowledge.vector_service import VectorService
from app.core.exceptions import NotFoundError, ValidationError, KnowledgeGraphError
from app.core.logging import LoggerMixin


class EntityService(LoggerMixin):
    """
    Service for managing knowledge graph entities.
    
    Provides high-level operations for entity lifecycle management,
    semantic search, and relationship discovery.
    """
    
    def __init__(self, vector_service: Optional[VectorService] = None):
        """
        Initialize the entity service.
        
        Args:
            vector_service: Vector service for semantic operations
        """
        self.vector_service = vector_service or VectorService()
    
    async def create_entity(
        self,
        db: AsyncSession,
        name: str,
        entity_type: EntityType,
        description: Optional[str] = None,
        system_id: Optional[uuid.UUID] = None,
        schema_definition: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Entity:
        """
        Create a new entity in both database and knowledge graph.
        
        Args:
            db: Database session
            name: Entity name
            entity_type: Type of entity
            description: Entity description
            system_id: Associated system ID
            schema_definition: Schema information
            **kwargs: Additional entity properties
            
        Returns:
            Entity: Created entity
        """
        try:
            # Create entity in database
            entity = Entity(
                name=name,
                entity_type=entity_type,
                description=description,
                system_id=system_id,
                schema_definition=schema_definition,
                **kwargs
            )
            
            db.add(entity)
            await db.flush()  # Get the ID
            
            # Generate semantic embedding
            if description or name:
                text_for_embedding = f"{name}. {description or ''}"
                embedding = await self.vector_service.generate_embedding(text_for_embedding)
                entity.embedding_vector = embedding
                entity.embedding_model = self.vector_service.model_name
            
            # Create in knowledge graph
            await knowledge_graph_service.create_entity(entity)
            
            # Store in vector database for semantic search
            if entity.embedding_vector:
                await self.vector_service.store_entity_embedding(
                    entity_id=str(entity.id),
                    embedding=entity.embedding_vector,
                    metadata={
                        "name": entity.name,
                        "type": entity.entity_type.value,
                        "description": entity.description,
                        "system_id": str(entity.system_id) if entity.system_id else None,
                    }
                )
            
            await db.commit()
            
            self.logger.info(
                "Created entity",
                entity_id=str(entity.id),
                name=entity.name,
                type=entity.entity_type.value
            )
            
            return entity
            
        except Exception as e:
            await db.rollback()
            raise KnowledgeGraphError(
                f"Failed to create entity: {str(e)}",
                operation="create_entity",
                context={"name": name, "type": entity_type.value}
            )
    
    async def get_entity(self, db: AsyncSession, entity_id: uuid.UUID) -> Entity:
        """
        Get an entity by ID.
        
        Args:
            db: Database session
            entity_id: Entity ID
            
        Returns:
            Entity: The entity
            
        Raises:
            NotFoundError: If entity not found
        """
        query = select(Entity).where(Entity.id == entity_id)
        result = await db.execute(query)
        entity = result.scalar_one_or_none()
        
        if not entity:
            raise NotFoundError(f"Entity not found: {entity_id}", resource_type="entity")
        
        return entity
    
    async def update_entity(
        self,
        db: AsyncSession,
        entity_id: uuid.UUID,
        **updates: Any
    ) -> Entity:
        """
        Update an entity.
        
        Args:
            db: Database session
            entity_id: Entity ID
            **updates: Fields to update
            
        Returns:
            Entity: Updated entity
        """
        entity = await self.get_entity(db, entity_id)
        
        # Update fields
        for field, value in updates.items():
            if hasattr(entity, field):
                setattr(entity, field, value)
        
        entity.updated_at = datetime.now(timezone.utc)
        
        # Regenerate embedding if content changed
        content_fields = ["name", "description", "semantic_label"]
        if any(field in updates for field in content_fields):
            text_for_embedding = f"{entity.name}. {entity.description or ''}"
            embedding = await self.vector_service.generate_embedding(text_for_embedding)
            entity.embedding_vector = embedding
            
            # Update vector database
            await self.vector_service.update_entity_embedding(
                entity_id=str(entity.id),
                embedding=embedding,
                metadata={
                    "name": entity.name,
                    "type": entity.entity_type.value,
                    "description": entity.description,
                    "system_id": str(entity.system_id) if entity.system_id else None,
                }
            )
        
        await db.commit()
        
        self.logger.info(f"Updated entity: {entity_id}")
        return entity
    
    async def delete_entity(self, db: AsyncSession, entity_id: uuid.UUID) -> None:
        """
        Delete an entity.
        
        Args:
            db: Database session
            entity_id: Entity ID
        """
        entity = await self.get_entity(db, entity_id)
        
        # Delete from vector database
        await self.vector_service.delete_entity_embedding(str(entity_id))
        
        # Delete from database (relationships will be cascade deleted)
        await db.delete(entity)
        await db.commit()
        
        self.logger.info(f"Deleted entity: {entity_id}")
    
    async def search_entities(
        self,
        db: AsyncSession,
        query: str,
        entity_type: Optional[EntityType] = None,
        system_id: Optional[uuid.UUID] = None,
        limit: int = 20
    ) -> List[Entity]:
        """
        Search entities using semantic similarity.
        
        Args:
            db: Database session
            query: Search query
            entity_type: Filter by entity type
            system_id: Filter by system ID
            limit: Maximum results
            
        Returns:
            List[Entity]: Matching entities
        """
        # Generate query embedding
        query_embedding = await self.vector_service.generate_embedding(query)
        
        # Search vector database
        similar_entities = await self.vector_service.search_similar_entities(
            query_embedding=query_embedding,
            limit=limit * 2,  # Get more to allow for filtering
            filters={
                "type": entity_type.value if entity_type else None,
                "system_id": str(system_id) if system_id else None,
            }
        )
        
        # Get entity IDs
        entity_ids = [uuid.UUID(result["entity_id"]) for result in similar_entities]
        
        if not entity_ids:
            return []
        
        # Fetch full entities from database
        query_stmt = select(Entity).where(Entity.id.in_(entity_ids))
        
        if entity_type:
            query_stmt = query_stmt.where(Entity.entity_type == entity_type)
        
        if system_id:
            query_stmt = query_stmt.where(Entity.system_id == system_id)
        
        result = await db.execute(query_stmt)
        entities = result.scalars().all()
        
        # Sort by similarity score
        entity_scores = {result["entity_id"]: result["score"] for result in similar_entities}
        entities = sorted(
            entities,
            key=lambda e: entity_scores.get(str(e.id), 0),
            reverse=True
        )
        
        return entities[:limit]
    
    async def find_similar_entities(
        self,
        db: AsyncSession,
        entity_id: uuid.UUID,
        limit: int = 10,
        min_similarity: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find entities similar to a given entity.
        
        Args:
            db: Database session
            entity_id: Reference entity ID
            limit: Maximum results
            min_similarity: Minimum similarity threshold
            
        Returns:
            List[Dict[str, Any]]: Similar entities with similarity scores
        """
        entity = await self.get_entity(db, entity_id)
        
        if not entity.embedding_vector:
            return []
        
        # Search for similar entities
        similar_entities = await self.vector_service.search_similar_entities(
            query_embedding=entity.embedding_vector,
            limit=limit + 1,  # +1 to exclude self
            min_score=min_similarity
        )
        
        # Filter out the entity itself
        similar_entities = [
            result for result in similar_entities 
            if result["entity_id"] != str(entity_id)
        ][:limit]
        
        if not similar_entities:
            return []
        
        # Get full entity data
        entity_ids = [uuid.UUID(result["entity_id"]) for result in similar_entities]
        query_stmt = select(Entity).where(Entity.id.in_(entity_ids))
        result = await db.execute(query_stmt)
        entities = {str(e.id): e for e in result.scalars().all()}
        
        # Combine with similarity scores
        results = []
        for similar in similar_entities:
            entity_data = entities.get(similar["entity_id"])
            if entity_data:
                results.append({
                    "entity": entity_data,
                    "similarity_score": similar["score"],
                    "distance": similar.get("distance", 0)
                })
        
        return results
    
    async def create_relationship(
        self,
        db: AsyncSession,
        source_entity_id: uuid.UUID,
        target_entity_id: uuid.UUID,
        relationship_type: RelationshipType,
        properties: Optional[Dict[str, Any]] = None,
        confidence_score: float = 1.0,
        strength: float = 1.0
    ) -> Relationship:
        """
        Create a relationship between entities.
        
        Args:
            db: Database session
            source_entity_id: Source entity ID
            target_entity_id: Target entity ID
            relationship_type: Type of relationship
            properties: Additional properties
            confidence_score: Confidence in relationship
            strength: Relationship strength
            
        Returns:
            Relationship: Created relationship
        """
        # Verify entities exist
        await self.get_entity(db, source_entity_id)
        await self.get_entity(db, target_entity_id)
        
        # Create relationship in database
        relationship = Relationship(
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            relationship_type=relationship_type,
            properties=properties,
            confidence_score=confidence_score,
            strength=strength
        )
        
        db.add(relationship)
        await db.flush()
        
        # Create in knowledge graph
        await knowledge_graph_service.create_relationship(
            source_entity_id=str(source_entity_id),
            target_entity_id=str(target_entity_id),
            relationship_type=relationship_type,
            properties=properties,
            confidence_score=confidence_score,
            strength=strength
        )
        
        await db.commit()
        
        self.logger.info(
            "Created relationship",
            relationship_id=str(relationship.id),
            source_id=str(source_entity_id),
            target_id=str(target_entity_id),
            type=relationship_type.value
        )
        
        return relationship
    
    async def get_entity_relationships(
        self,
        db: AsyncSession,
        entity_id: uuid.UUID,
        relationship_type: Optional[RelationshipType] = None
    ) -> List[Relationship]:
        """
        Get relationships for an entity.
        
        Args:
            db: Database session
            entity_id: Entity ID
            relationship_type: Filter by relationship type
            
        Returns:
            List[Relationship]: Entity relationships
        """
        query = select(Relationship).where(
            (Relationship.source_entity_id == entity_id) |
            (Relationship.target_entity_id == entity_id)
        )
        
        if relationship_type:
            query = query.where(Relationship.relationship_type == relationship_type)
        
        query = query.options(
            selectinload(Relationship.source_entity),
            selectinload(Relationship.target_entity)
        )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update_entity_usage(
        self,
        db: AsyncSession,
        entity_id: uuid.UUID
    ) -> None:
        """
        Update entity usage statistics.
        
        Args:
            db: Database session
            entity_id: Entity ID
        """
        query = (
            update(Entity)
            .where(Entity.id == entity_id)
            .values(
                usage_count=Entity.usage_count + 1,
                last_used_at=datetime.now(timezone.utc)
            )
        )
        
        await db.execute(query)
        await db.commit()
        
        self.logger.debug(f"Updated usage for entity: {entity_id}")
