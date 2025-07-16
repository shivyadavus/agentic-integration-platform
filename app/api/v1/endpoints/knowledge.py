"""
Knowledge Graph API endpoints.

These endpoints provide access to the knowledge graph for querying patterns,
schemas, and semantic mappings that power the agentic integration system.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_db, 
    get_knowledge_graph_service, 
    get_vector_service, 
    get_pattern_service
)
from app.services.knowledge.graph_service import KnowledgeGraphService
from app.services.knowledge.vector_service import VectorService
from app.services.knowledge.pattern_service import PatternService
from app.schemas.knowledge import (
    PatternSearchRequest,
    PatternSearchResponse,
    SchemaQueryRequest,
    SchemaQueryResponse,
    SemanticSearchRequest,
    SemanticSearchResponse,
    EntityCreateRequest,
    EntityResponse,
    RelationshipCreateRequest,
    RelationshipResponse
)

router = APIRouter()


@router.post("/patterns/search", response_model=PatternSearchResponse)
async def search_patterns(
    search_request: PatternSearchRequest,
    db: AsyncSession = Depends(get_db),
    pattern_service: PatternService = Depends(get_pattern_service)
):
    """
    Search for integration patterns using semantic similarity.
    
    This endpoint enables the MCP agent to find relevant patterns
    from the knowledge base to assist with integration planning.
    """
    try:
        # Find applicable patterns
        patterns = await pattern_service.find_applicable_patterns(
            db=db,
            source_system_type=search_request.source_system_type,
            target_system_type=search_request.target_system_type,
            integration_description=search_request.description,
            limit=search_request.limit
        )
        
        return PatternSearchResponse(
            query=search_request.description,
            patterns=patterns,
            total_found=len(patterns)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pattern search failed: {str(e)}"
        )


@router.get("/patterns/{pattern_id}")
async def get_pattern(
    pattern_id: UUID,
    db: AsyncSession = Depends(get_db),
    pattern_service: PatternService = Depends(get_pattern_service)
):
    """Get detailed information about a specific pattern."""
    try:
        pattern = await pattern_service.get_pattern(db, pattern_id)
        if not pattern:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pattern not found"
            )
        return pattern
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve pattern: {str(e)}"
        )


@router.post("/schemas/query", response_model=SchemaQueryResponse)
async def query_schemas(
    query_request: SchemaQueryRequest,
    kg_service: KnowledgeGraphService = Depends(get_knowledge_graph_service)
):
    """
    Query system schemas and data mappings from the knowledge graph.
    
    This endpoint helps the MCP agent understand system capabilities
    and data structures for integration planning.
    """
    try:
        # Query entities by type (system schemas)
        entities = await kg_service.find_entities_by_type(
            entity_type="schema",
            properties={"system_type": query_request.system_type} if query_request.system_type else None,
            limit=query_request.limit
        )
        
        # Get related mappings
        mappings = []
        for entity in entities:
            related = await kg_service.find_related_entities(
                entity_id=entity["id"],
                relationship_type="MAPS_TO",
                limit=10
            )
            mappings.extend(related)
        
        return SchemaQueryResponse(
            system_type=query_request.system_type,
            schemas=entities,
            mappings=mappings,
            total_found=len(entities)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Schema query failed: {str(e)}"
        )


@router.post("/semantic/search", response_model=SemanticSearchResponse)
async def semantic_search(
    search_request: SemanticSearchRequest,
    vector_service: VectorService = Depends(get_vector_service)
):
    """
    Perform semantic search across all knowledge entities.
    
    This endpoint enables natural language queries against the
    entire knowledge base for contextual information retrieval.
    """
    try:
        # Generate embedding for the query
        query_embedding = await vector_service.generate_embedding(search_request.query)
        
        # Search entities
        results = await vector_service.search_similar_entities(
            query_embedding=query_embedding,
            limit=search_request.limit,
            min_score=search_request.min_similarity_score,
            filters=search_request.filters
        )
        
        return SemanticSearchResponse(
            query=search_request.query,
            results=results,
            total_found=len(results)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic search failed: {str(e)}"
        )


@router.post("/entities", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
async def create_entity(
    entity_request: EntityCreateRequest,
    kg_service: KnowledgeGraphService = Depends(get_knowledge_graph_service),
    vector_service: VectorService = Depends(get_vector_service)
):
    """
    Create a new entity in the knowledge graph.
    
    This endpoint allows adding new systems, patterns, or other
    entities to expand the knowledge base.
    """
    try:
        # Simple direct database insertion to work with existing schema
        import uuid
        import json
        from datetime import datetime
        from sqlalchemy import text
        from app.database import get_db

        entity_id = str(uuid.uuid4())

        # Get database session
        async for db in get_db():
            # Insert directly into the existing table structure
            query = text("""
                INSERT INTO kg_entities (
                    id, name, entity_type, description, properties,
                    created_at, updated_at, version
                ) VALUES (
                    :id, :name, :entity_type, :description, :properties,
                    :created_at, :updated_at, :version
                )
            """)

            await db.execute(query, {
                "id": entity_id,
                "name": entity_request.properties.get('name', 'Unnamed Entity'),
                "entity_type": entity_request.entity_type,
                "description": entity_request.properties.get('description'),
                "properties": json.dumps(entity_request.properties),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "version": 1
            })

            await db.commit()
            break
        
        return EntityResponse(
            id=entity_id,
            entity_type=entity_request.entity_type,
            properties=entity_request.properties
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create entity: {str(e)}"
        )


@router.get("/entities", response_model=List[EntityResponse])
async def get_entities():
    """
    Get all entities from the knowledge graph.
    """
    try:
        from sqlalchemy import text
        from app.database import get_db
        import json

        async for db in get_db():
            query = text("SELECT id, name, entity_type, description, properties FROM kg_entities ORDER BY created_at DESC")
            result = await db.execute(query)
            rows = result.fetchall()

            entities = []
            for row in rows:
                # Properties are already parsed by SQLAlchemy JSONB
                properties = row.properties if row.properties else {}
                entities.append(EntityResponse(
                    id=str(row.id),
                    entity_type=row.entity_type,
                    properties=properties
                ))

            return entities

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch entities: {str(e)}"
        )


@router.get("/relationships", response_model=List[Dict[str, Any]])
async def get_relationships(
    kg_service: KnowledgeGraphService = Depends(get_knowledge_graph_service)
):
    """
    Get all relationships from the knowledge graph.
    """
    try:
        relationships = await kg_service.get_all_relationships()
        return [
            {
                "id": rel.id,
                "source_entity_id": rel.source_entity_id,
                "target_entity_id": rel.target_entity_id,
                "relationship_type": rel.relationship_type,
                "confidence_score": rel.confidence_score,
                "properties": rel.properties or {}
            }
            for rel in relationships
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch relationships: {str(e)}"
        )


@router.post("/relationships", response_model=RelationshipResponse, status_code=status.HTTP_201_CREATED)
async def create_relationship(
    relationship_request: RelationshipCreateRequest,
    kg_service: KnowledgeGraphService = Depends(get_knowledge_graph_service)
):
    """
    Create a new relationship between entities in the knowledge graph.
    
    This endpoint enables building connections between systems,
    patterns, and other entities to enhance semantic understanding.
    """
    try:
        relationship_id = await kg_service.create_relationship(
            source_id=relationship_request.source_id,
            target_id=relationship_request.target_id,
            relationship_type=relationship_request.relationship_type,
            properties=relationship_request.properties
        )
        
        return RelationshipResponse(
            id=relationship_id,
            source_id=relationship_request.source_id,
            target_id=relationship_request.target_id,
            relationship_type=relationship_request.relationship_type,
            properties=relationship_request.properties
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create relationship: {str(e)}"
        )


@router.get("/stats")
async def get_knowledge_stats(
    kg_service: KnowledgeGraphService = Depends(get_knowledge_graph_service)
):
    """
    Get statistics about the knowledge graph.
    
    This endpoint provides insights into the current state
    of the knowledge base for monitoring and analytics.
    """
    try:
        stats = await kg_service.get_graph_statistics()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve stats: {str(e)}"
        )
