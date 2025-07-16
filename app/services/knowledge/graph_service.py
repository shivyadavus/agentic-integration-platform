"""
Knowledge graph service for managing Neo4j operations.

This module provides high-level operations for managing the knowledge graph,
including entity and relationship CRUD operations, graph queries, and analytics.
"""

import asyncio
from typing import Any, Dict, List, Optional, Tuple
from contextlib import asynccontextmanager

from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from neo4j.exceptions import Neo4jError

from app.core.config import settings
from app.core.exceptions import KnowledgeGraphError
from app.core.logging import LoggerMixin
from app.models.knowledge import Entity, Relationship, EntityType, RelationshipType


class KnowledgeGraphService(LoggerMixin):
    """
    Service for managing the Neo4j knowledge graph.
    
    Provides high-level operations for entities, relationships, and graph queries
    used by the agentic integration platform.
    """
    
    def __init__(self):
        """Initialize the knowledge graph service."""
        self._driver: Optional[AsyncDriver] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the Neo4j connection."""
        if self._initialized:
            return
        
        try:
            self._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
                max_connection_lifetime=3600,
                max_connection_pool_size=50,
                connection_acquisition_timeout=60,
            )
            
            # Test connection
            await self.health_check()
            
            # Create indexes and constraints
            await self._create_schema()
            
            self._initialized = True
            self.logger.info("Knowledge graph service initialized successfully")
            
        except Exception as e:
            raise KnowledgeGraphError(
                f"Failed to initialize knowledge graph: {str(e)}",
                operation="initialize"
            )
    
    async def close(self) -> None:
        """Close the Neo4j connection."""
        if self._driver:
            await self._driver.close()
            self._driver = None
            self._initialized = False
            self.logger.info("Knowledge graph connection closed")
    
    @asynccontextmanager
    async def get_session(self):
        """Get a Neo4j session context manager."""
        if not self._initialized:
            await self.initialize()
        
        if not self._driver:
            raise KnowledgeGraphError("Driver not initialized", operation="get_session")
        
        session = self._driver.session()
        try:
            yield session
        finally:
            await session.close()
    
    async def health_check(self) -> bool:
        """
        Check if the knowledge graph is healthy.

        Returns:
            bool: True if healthy
        """
        try:
            # Don't use get_session() here to avoid recursion during initialization
            if not self._driver:
                return False

            session = self._driver.session()
            try:
                result = await session.run("RETURN 1 as health")
                record = await result.single()
                return record["health"] == 1
            finally:
                await session.close()
        except Exception as e:
            self.logger.error("Knowledge graph health check failed", error=str(e))
            return False
    
    async def _create_schema(self) -> None:
        """Create Neo4j schema (indexes and constraints)."""
        schema_queries = [
            # Entity constraints and indexes
            "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
            "CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name)",
            "CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.entity_type)",
            "CREATE INDEX entity_system IF NOT EXISTS FOR (e:Entity) ON (e.system_id)",
            
            # Relationship constraints and indexes
            "CREATE CONSTRAINT relationship_id IF NOT EXISTS FOR (r:Relationship) REQUIRE r.id IS UNIQUE",
            "CREATE INDEX relationship_type IF NOT EXISTS FOR (r:Relationship) ON (r.relationship_type)",
            "CREATE INDEX relationship_confidence IF NOT EXISTS FOR (r:Relationship) ON (r.confidence_score)",
            
            # Pattern constraints and indexes
            "CREATE CONSTRAINT pattern_id IF NOT EXISTS FOR (p:Pattern) REQUIRE p.id IS UNIQUE",
            "CREATE INDEX pattern_type IF NOT EXISTS FOR (p:Pattern) ON (p.pattern_type)",
            "CREATE INDEX pattern_usage IF NOT EXISTS FOR (p:Pattern) ON (p.usage_count)",
        ]
        
        # Use driver directly to avoid recursion during initialization
        if not self._driver:
            raise KnowledgeGraphError("Driver not initialized", operation="_create_schema")

        session = self._driver.session()
        try:
            for query in schema_queries:
                try:
                    await session.run(query)
                except Neo4jError as e:
                    # Ignore constraint/index already exists errors
                    if "already exists" not in str(e).lower():
                        self.logger.warning(f"Schema creation warning: {e}")
        finally:
            await session.close()
        
        self.logger.info("Knowledge graph schema created/updated")
    
    async def create_entity(self, entity: Entity) -> str:
        """
        Create an entity in the knowledge graph.
        
        Args:
            entity: Entity to create
            
        Returns:
            str: Created entity ID
        """
        query = """
        CREATE (e:Entity {
            id: $id,
            name: $name,
            entity_type: $entity_type,
            semantic_label: $semantic_label,
            canonical_name: $canonical_name,
            aliases: $aliases,
            schema_definition: $schema_definition,
            data_type: $data_type,
            constraints: $constraints,
            system_id: $system_id,
            api_path: $api_path,
            embedding_vector: $embedding_vector,
            embedding_model: $embedding_model,
            usage_count: $usage_count,
            confidence_score: $confidence_score,
            quality_score: $quality_score,
            verified: $verified,
            created_at: datetime($created_at),
            updated_at: datetime($updated_at)
        })
        RETURN e.id as entity_id
        """
        
        try:
            async with self.get_session() as session:
                result = await session.run(query, {
                    "id": str(entity.id),
                    "name": entity.name,
                    "entity_type": entity.entity_type.value,
                    "semantic_label": entity.semantic_label,
                    "canonical_name": entity.canonical_name,
                    "aliases": entity.aliases or [],
                    "schema_definition": entity.schema_definition,
                    "data_type": entity.data_type,
                    "constraints": entity.constraints,
                    "system_id": str(entity.system_id) if entity.system_id else None,
                    "api_path": entity.api_path,
                    "embedding_vector": entity.embedding_vector,
                    "embedding_model": entity.embedding_model,
                    "usage_count": entity.usage_count,
                    "confidence_score": entity.confidence_score,
                    "quality_score": entity.quality_score,
                    "verified": entity.verified,
                    "created_at": entity.created_at.isoformat(),
                    "updated_at": entity.updated_at.isoformat(),
                })
                
                record = await result.single()
                entity_id = record["entity_id"]
                
                self.logger.info(f"Created entity in knowledge graph: {entity_id}")
                return entity_id
                
        except Neo4jError as e:
            raise KnowledgeGraphError(
                f"Failed to create entity: {str(e)}",
                operation="create_entity",
                context={"entity_name": entity.name}
            )
    
    async def create_relationship(
        self,
        source_entity_id: str,
        target_entity_id: str,
        relationship_type: RelationshipType,
        properties: Optional[Dict[str, Any]] = None,
        confidence_score: float = 1.0,
        strength: float = 1.0
    ) -> str:
        """
        Create a relationship between two entities.
        
        Args:
            source_entity_id: Source entity ID
            target_entity_id: Target entity ID
            relationship_type: Type of relationship
            properties: Additional relationship properties
            confidence_score: Confidence in the relationship
            strength: Strength of the relationship
            
        Returns:
            str: Created relationship ID
        """
        import uuid
        from datetime import datetime
        
        relationship_id = str(uuid.uuid4())
        
        query = """
        MATCH (source:Entity {id: $source_id})
        MATCH (target:Entity {id: $target_id})
        CREATE (source)-[r:RELATES {
            id: $relationship_id,
            relationship_type: $relationship_type,
            properties: $properties,
            confidence_score: $confidence_score,
            strength: $strength,
            usage_count: 0,
            success_count: 0,
            created_at: datetime($created_at)
        }]->(target)
        RETURN r.id as relationship_id
        """
        
        try:
            async with self.get_session() as session:
                result = await session.run(query, {
                    "source_id": source_entity_id,
                    "target_id": target_entity_id,
                    "relationship_id": relationship_id,
                    "relationship_type": relationship_type.value,
                    "properties": properties or {},
                    "confidence_score": confidence_score,
                    "strength": strength,
                    "created_at": datetime.utcnow().isoformat(),
                })
                
                record = await result.single()
                if not record:
                    raise KnowledgeGraphError(
                        "Failed to create relationship - entities not found",
                        operation="create_relationship"
                    )
                
                rel_id = record["relationship_id"]
                
                self.logger.info(
                    f"Created relationship in knowledge graph: {rel_id}",
                    source_id=source_entity_id,
                    target_id=target_entity_id,
                    type=relationship_type.value
                )
                
                return rel_id
                
        except Neo4jError as e:
            raise KnowledgeGraphError(
                f"Failed to create relationship: {str(e)}",
                operation="create_relationship",
                context={
                    "source_id": source_entity_id,
                    "target_id": target_entity_id,
                    "type": relationship_type.value
                }
            )
    
    async def find_entities(
        self,
        entity_type: Optional[EntityType] = None,
        name_pattern: Optional[str] = None,
        system_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Find entities matching criteria.
        
        Args:
            entity_type: Filter by entity type
            name_pattern: Filter by name pattern (case-insensitive)
            system_id: Filter by system ID
            limit: Maximum number of results
            
        Returns:
            List[Dict[str, Any]]: Matching entities
        """
        conditions = []
        params = {"limit": limit}
        
        if entity_type:
            conditions.append("e.entity_type = $entity_type")
            params["entity_type"] = entity_type.value
        
        if name_pattern:
            conditions.append("toLower(e.name) CONTAINS toLower($name_pattern)")
            params["name_pattern"] = name_pattern
        
        if system_id:
            conditions.append("e.system_id = $system_id")
            params["system_id"] = system_id
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"""
        MATCH (e:Entity)
        {where_clause}
        RETURN e
        ORDER BY e.usage_count DESC, e.name
        LIMIT $limit
        """
        
        try:
            async with self.get_session() as session:
                result = await session.run(query, params)
                entities = []
                
                async for record in result:
                    entity_data = dict(record["e"])
                    entities.append(entity_data)
                
                return entities
                
        except Neo4jError as e:
            raise KnowledgeGraphError(
                f"Failed to find entities: {str(e)}",
                operation="find_entities"
            )
    
    async def find_related_entities(
        self,
        entity_id: str,
        relationship_types: Optional[List[RelationshipType]] = None,
        max_depth: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Find entities related to a given entity.
        
        Args:
            entity_id: Source entity ID
            relationship_types: Filter by relationship types
            max_depth: Maximum traversal depth
            
        Returns:
            List[Dict[str, Any]]: Related entities with relationship info
        """
        type_filter = ""
        params = {"entity_id": entity_id, "max_depth": max_depth}
        
        if relationship_types:
            type_values = [rt.value for rt in relationship_types]
            type_filter = "WHERE r.relationship_type IN $relationship_types"
            params["relationship_types"] = type_values
        
        query = f"""
        MATCH (source:Entity {{id: $entity_id}})
        MATCH (source)-[r:RELATES*1..{max_depth}]->(target:Entity)
        {type_filter}
        RETURN DISTINCT target, r[-1] as relationship
        ORDER BY r[-1].strength DESC, r[-1].confidence_score DESC
        """
        
        try:
            async with self.get_session() as session:
                result = await session.run(query, params)
                related_entities = []
                
                async for record in result:
                    entity_data = dict(record["target"])
                    relationship_data = dict(record["relationship"])
                    
                    related_entities.append({
                        "entity": entity_data,
                        "relationship": relationship_data
                    })
                
                return related_entities
                
        except Neo4jError as e:
            raise KnowledgeGraphError(
                f"Failed to find related entities: {str(e)}",
                operation="find_related_entities",
                context={"entity_id": entity_id}
            )
    
    async def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Get knowledge graph statistics.

        Returns:
            Dict[str, Any]: Graph statistics
        """
        queries = {
            "total_entities": "MATCH (e:Entity) RETURN count(e) as count",
            "total_relationships": "MATCH ()-[r:RELATES]->() RETURN count(r) as count",
            "entity_types": """
                MATCH (e:Entity)
                RETURN e.entity_type as type, count(e) as count
                ORDER BY count DESC
            """,
            "relationship_types": """
                MATCH ()-[r:RELATES]->()
                RETURN r.relationship_type as type, count(r) as count
                ORDER BY count DESC
            """,
            "top_entities": """
                MATCH (e:Entity)
                RETURN e.name as name, e.usage_count as usage_count
                ORDER BY e.usage_count DESC
                LIMIT 10
            """,
        }

        stats = {}

        try:
            async with self.get_session() as session:
                for stat_name, query in queries.items():
                    result = await session.run(query)

                    if stat_name in ["total_entities", "total_relationships"]:
                        record = await result.single()
                        stats[stat_name] = record["count"]
                    else:
                        records = []
                        async for record in result:
                            records.append(dict(record))
                        stats[stat_name] = records

            return stats

        except Neo4jError as e:
            raise KnowledgeGraphError(
                f"Failed to get graph statistics: {str(e)}",
                operation="get_graph_statistics"
            )

    async def get_all_relationships(self) -> List[Relationship]:
        """
        Get all relationships from the knowledge graph.

        Returns:
            List[Relationship]: List of all relationships
        """
        try:
            query = """
            MATCH ()-[r:RELATES]->()
            RETURN r.id as id,
                   r.source_entity_id as source_entity_id,
                   r.target_entity_id as target_entity_id,
                   r.relationship_type as relationship_type,
                   r.properties as properties,
                   r.confidence_score as confidence_score,
                   r.strength as strength,
                   r.usage_count as usage_count,
                   r.success_count as success_count,
                   r.created_at as created_at
            ORDER BY r.created_at DESC
            """

            async with self.get_session() as session:
                result = await session.run(query)
                records = await result.data()

                relationships = []
                for record in records:
                    relationship = Relationship(
                        id=record["id"],
                        source_entity_id=record["source_entity_id"],
                        target_entity_id=record["target_entity_id"],
                        relationship_type=RelationshipType(record["relationship_type"]),
                        properties=record["properties"] or {},
                        confidence_score=record["confidence_score"] or 0.0,
                        strength=record["strength"] or 0.0,
                        usage_count=record["usage_count"] or 0,
                        success_count=record["success_count"] or 0,
                        created_at=record["created_at"]
                    )
                    relationships.append(relationship)

                return relationships

        except Exception as e:
            raise KnowledgeGraphError(
                f"Failed to get all relationships: {str(e)}",
                operation="get_all_relationships"
            )


# Global knowledge graph service instance
knowledge_graph_service = KnowledgeGraphService()
