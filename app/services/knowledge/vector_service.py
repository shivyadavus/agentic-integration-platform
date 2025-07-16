"""
Vector service for semantic search and embeddings.

This module provides vector database operations using Qdrant for storing
and searching entity embeddings for semantic similarity.
"""

import asyncio
from typing import Any, Dict, List, Optional

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance, VectorParams, CreateCollection, PointStruct,
    Filter, FieldCondition, MatchValue, SearchRequest
)
# from sentence_transformers import SentenceTransformer  # Temporarily disabled

from app.core.config import settings
from app.core.exceptions import ExternalServiceError
from app.core.logging import LoggerMixin


class VectorService(LoggerMixin):
    """
    Service for vector operations and semantic search.
    
    Manages embeddings generation, storage, and similarity search
    using Qdrant vector database and sentence transformers.
    """
    
    def __init__(self):
        """Initialize the vector service."""
        self._client: Optional[AsyncQdrantClient] = None
        self._embedding_model = None  # Optional[SentenceTransformer] = None  # Temporarily disabled
        self._initialized = False
        
        # Collection names
        self.entities_collection = "entities"
        self.patterns_collection = "patterns"
        
        # Model configuration
        self.model_name = settings.embedding_model
        self.vector_dimension = settings.vector_dimension
    
    async def initialize(self) -> None:
        """Initialize the vector service."""
        if self._initialized:
            return
        
        try:
            # Initialize Qdrant client
            self._client = AsyncQdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
                api_key=settings.qdrant_api_key,
                timeout=60,
            )
            
            # Initialize embedding model
            # self._embedding_model = SentenceTransformer(self.model_name)  # Temporarily disabled
            self._embedding_model = None  # Mock for now
            
            # Create collections
            await self._create_collections()
            
            self._initialized = True
            self.logger.info("Vector service initialized successfully")
            
        except Exception as e:
            raise ExternalServiceError(
                f"Failed to initialize vector service: {str(e)}",
                service_name="Qdrant"
            )
    
    async def _create_collections(self) -> None:
        """Create Qdrant collections if they don't exist."""
        collections = [
            (self.entities_collection, "Entity embeddings for semantic search"),
            (self.patterns_collection, "Pattern embeddings for pattern matching"),
        ]
        
        for collection_name, description in collections:
            try:
                # Check if collection exists
                collections_info = await self._client.get_collections()
                existing_names = [col.name for col in collections_info.collections]
                
                if collection_name not in existing_names:
                    await self._client.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(
                            size=self.vector_dimension,
                            distance=Distance.COSINE
                        )
                    )
                    self.logger.info(f"Created collection: {collection_name}")
                
            except Exception as e:
                self.logger.error(f"Failed to create collection {collection_name}: {e}")
                raise
    
    async def ensure_initialized(self) -> None:
        """Ensure the service is initialized."""
        if not self._initialized:
            await self.initialize()
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            List[float]: Embedding vector
        """
        await self.ensure_initialized()
        
        try:
            # Mock embedding generation for now
            if self._embedding_model is None:
                # Return a mock embedding vector of the expected dimension
                import random
                return [random.random() for _ in range(self.vector_dimension)]

            # Run embedding generation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                self._embedding_model.encode,
                text
            )

            return embedding.tolist()

        except Exception as e:
            raise ExternalServiceError(
                f"Failed to generate embedding: {str(e)}",
                service_name="EmbeddingModel"
            )
    
    async def store_entity_embedding(
        self,
        entity_id: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> None:
        """
        Store entity embedding in vector database.
        
        Args:
            entity_id: Unique entity identifier
            embedding: Embedding vector
            metadata: Additional metadata
        """
        await self.ensure_initialized()
        
        try:
            point = PointStruct(
                id=entity_id,
                vector=embedding,
                payload=metadata
            )
            
            await self._client.upsert(
                collection_name=self.entities_collection,
                points=[point]
            )
            
            self.logger.debug(f"Stored embedding for entity: {entity_id}")
            
        except Exception as e:
            raise ExternalServiceError(
                f"Failed to store entity embedding: {str(e)}",
                service_name="Qdrant",
                service_error=str(e)
            )
    
    async def update_entity_embedding(
        self,
        entity_id: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> None:
        """
        Update entity embedding in vector database.
        
        Args:
            entity_id: Entity identifier
            embedding: Updated embedding vector
            metadata: Updated metadata
        """
        # Upsert handles both create and update
        await self.store_entity_embedding(entity_id, embedding, metadata)
    
    async def delete_entity_embedding(self, entity_id: str) -> None:
        """
        Delete entity embedding from vector database.
        
        Args:
            entity_id: Entity identifier
        """
        await self.ensure_initialized()
        
        try:
            await self._client.delete(
                collection_name=self.entities_collection,
                points_selector=[entity_id]
            )
            
            self.logger.debug(f"Deleted embedding for entity: {entity_id}")
            
        except Exception as e:
            self.logger.warning(f"Failed to delete entity embedding: {e}")
    
    async def search_similar_entities(
        self,
        query_embedding: List[float],
        limit: int = 10,
        min_score: float = 0.0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar entities using vector similarity.
        
        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results
            min_score: Minimum similarity score
            filters: Optional filters for metadata
            
        Returns:
            List[Dict[str, Any]]: Similar entities with scores
        """
        await self.ensure_initialized()
        
        try:
            # Build filter conditions
            filter_conditions = []
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        filter_conditions.append(
                            FieldCondition(
                                key=key,
                                match=MatchValue(value=value)
                            )
                        )
            
            query_filter = Filter(must=filter_conditions) if filter_conditions else None
            
            # Perform search
            search_result = await self._client.search(
                collection_name=self.entities_collection,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=min_score,
                query_filter=query_filter
            )
            
            # Format results
            results = []
            for hit in search_result:
                results.append({
                    "entity_id": hit.id,
                    "score": hit.score,
                    "metadata": hit.payload,
                    "distance": 1 - hit.score  # Convert similarity to distance
                })
            
            return results
            
        except Exception as e:
            raise ExternalServiceError(
                f"Failed to search similar entities: {str(e)}",
                service_name="Qdrant"
            )
    
    async def store_pattern_embedding(
        self,
        pattern_id: str,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> None:
        """
        Store pattern embedding in vector database.
        
        Args:
            pattern_id: Unique pattern identifier
            embedding: Embedding vector
            metadata: Pattern metadata
        """
        await self.ensure_initialized()
        
        try:
            point = PointStruct(
                id=pattern_id,
                vector=embedding,
                payload=metadata
            )
            
            await self._client.upsert(
                collection_name=self.patterns_collection,
                points=[point]
            )
            
            self.logger.debug(f"Stored embedding for pattern: {pattern_id}")
            
        except Exception as e:
            raise ExternalServiceError(
                f"Failed to store pattern embedding: {str(e)}",
                service_name="Qdrant"
            )
    
    async def search_similar_patterns(
        self,
        query_embedding: List[float],
        limit: int = 5,
        min_score: float = 0.7,
        pattern_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar integration patterns.
        
        Args:
            query_embedding: Query embedding vector
            limit: Maximum number of results
            min_score: Minimum similarity score
            pattern_type: Filter by pattern type
            
        Returns:
            List[Dict[str, Any]]: Similar patterns with scores
        """
        await self.ensure_initialized()
        
        try:
            # Build filter
            filter_conditions = []
            if pattern_type:
                filter_conditions.append(
                    FieldCondition(
                        key="pattern_type",
                        match=MatchValue(value=pattern_type)
                    )
                )
            
            query_filter = Filter(must=filter_conditions) if filter_conditions else None
            
            # Perform search
            search_result = await self._client.search(
                collection_name=self.patterns_collection,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=min_score,
                query_filter=query_filter
            )
            
            # Format results
            results = []
            for hit in search_result:
                results.append({
                    "pattern_id": hit.id,
                    "score": hit.score,
                    "metadata": hit.payload,
                    "distance": 1 - hit.score
                })
            
            return results
            
        except Exception as e:
            raise ExternalServiceError(
                f"Failed to search similar patterns: {str(e)}",
                service_name="Qdrant"
            )
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        Get information about a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dict[str, Any]: Collection information
        """
        await self.ensure_initialized()
        
        try:
            info = await self._client.get_collection(collection_name)
            return {
                "name": collection_name,
                "vectors_count": info.vectors_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "points_count": info.points_count,
                "segments_count": info.segments_count,
                "status": info.status.value,
                "optimizer_status": info.optimizer_status.ok,
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance.value,
            }
            
        except Exception as e:
            raise ExternalServiceError(
                f"Failed to get collection info: {str(e)}",
                service_name="Qdrant"
            )
    
    async def health_check(self) -> bool:
        """
        Check if the vector service is healthy.
        
        Returns:
            bool: True if healthy
        """
        try:
            await self.ensure_initialized()
            
            # Test with a simple embedding generation
            test_embedding = await self.generate_embedding("health check")
            
            # Test vector database connection
            collections = await self._client.get_collections()
            
            return len(test_embedding) == self.vector_dimension
            
        except Exception as e:
            self.logger.error(f"Vector service health check failed: {e}")
            return False
    
    async def close(self) -> None:
        """Close the vector service connections."""
        if self._client:
            await self._client.close()
            self._client = None
        
        self._embedding_model = None
        self._initialized = False
        self.logger.info("Vector service closed")


# Global vector service instance
vector_service = VectorService()
