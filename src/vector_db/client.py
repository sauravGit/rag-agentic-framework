"""
Vector Database module for the Enhanced MLOps Framework for Agentic AI RAG Workflows.

This module provides integration with vector databases for storing and retrieving
embeddings for RAG workflows in medical customer support scenarios.
"""

import os
import logging
from typing import Dict, Any, Optional, List, Union
import time
import json
import numpy as np
from pydantic import BaseModel, Field

from ..core import FrameworkException, ServiceRegistry, MetricsCollector
from ..core.config import VectorDBConfig, ConfigManager

logger = logging.getLogger(__name__)

class VectorDBDocument(BaseModel):
    """Model for a document in the vector database."""
    
    id: str = Field(..., description="Unique identifier for the document")
    text: str = Field(..., description="Text content of the document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata for the document")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding of the document")

class SearchResult(BaseModel):
    """Model for a search result from the vector database."""
    
    document: VectorDBDocument = Field(..., description="The document that matched the search")
    score: float = Field(..., description="Similarity score for the match")
    rank: int = Field(..., description="Rank of the result in the search results")

class SearchRequest(BaseModel):
    """Model for a search request to the vector database."""
    
    query: str = Field(..., description="Query text to search for")
    query_embedding: Optional[List[float]] = Field(None, description="Vector embedding of the query")
    filter: Dict[str, Any] = Field(default_factory=dict, description="Metadata filter for the search")
    top_k: int = Field(5, description="Number of results to return")

class VectorDBClient:
    """Client for interacting with vector databases."""
    
    def __init__(self, config: VectorDBConfig = None):
        """Initialize the vector database client with configuration."""
        if config is None:
            config_manager = ConfigManager()
            app_config = config_manager.get_config()
            config = app_config.vector_db
        
        self.config = config
        self.metrics = MetricsCollector()
        
        # Initialize the appropriate vector database client based on the provider
        self.provider = config.provider.lower()
        
        if self.provider == "elasticsearch":
            self.client = self._init_elasticsearch()
        elif self.provider == "pinecone":
            self.client = self._init_pinecone()
        elif self.provider == "vertex_matching_engine":
            self.client = self._init_vertex_matching_engine()
        else:
            raise FrameworkException(
                f"Unsupported vector database provider: {self.provider}",
                code="UNSUPPORTED_VECTOR_DB"
            )
        
        # Register with service registry
        service_registry = ServiceRegistry()
        service_registry.register("vector_db_client", self)
        
        logger.info(f"Vector Database Client initialized with provider: {self.provider}")
    
    def _init_elasticsearch(self):
        """Initialize Elasticsearch client."""
        # This is a mock implementation
        # In a real system, this would initialize an actual Elasticsearch client
        logger.info("Initializing Elasticsearch client")
        return MockVectorDB("elasticsearch", self.config)
    
    def _init_pinecone(self):
        """Initialize Pinecone client."""
        # This is a mock implementation
        # In a real system, this would initialize an actual Pinecone client
        logger.info("Initializing Pinecone client")
        return MockVectorDB("pinecone", self.config)
    
    def _init_vertex_matching_engine(self):
        """Initialize Vertex AI Matching Engine client."""
        # This is a mock implementation
        # In a real system, this would initialize an actual Vertex AI client
        logger.info("Initializing Vertex AI Matching Engine client")
        return MockVectorDB("vertex_matching_engine", self.config)
    
    def index_document(self, document: VectorDBDocument) -> str:
        """Index a document in the vector database."""
        start_time = time.time()
        
        try:
            # Ensure the document has an embedding
            if document.embedding is None:
                raise FrameworkException(
                    "Document must have an embedding to be indexed",
                    code="MISSING_EMBEDDING"
                )
            
            # Index the document
            doc_id = self.client.index_document(document)
            
            # Record metrics
            indexing_time = time.time() - start_time
            self.metrics.record(
                "document_indexing_duration",
                indexing_time,
                {"provider": self.provider}
            )
            
            return doc_id
            
        except Exception as e:
            logger.error(f"Error indexing document: {e}")
            
            # Record error metric
            self.metrics.record(
                "document_indexing_error",
                1,
                {"provider": self.provider, "error_type": type(e).__name__}
            )
            
            raise FrameworkException(
                f"Failed to index document: {str(e)}",
                code="INDEXING_ERROR",
                details={"document_id": document.id}
            )
    
    def batch_index_documents(self, documents: List[VectorDBDocument]) -> List[str]:
        """Index multiple documents in the vector database."""
        start_time = time.time()
        
        try:
            # Ensure all documents have embeddings
            for doc in documents:
                if doc.embedding is None:
                    raise FrameworkException(
                        f"Document {doc.id} must have an embedding to be indexed",
                        code="MISSING_EMBEDDING"
                    )
            
            # Batch index the documents
            doc_ids = self.client.batch_index_documents(documents)
            
            # Record metrics
            indexing_time = time.time() - start_time
            self.metrics.record(
                "batch_indexing_duration",
                indexing_time,
                {"provider": self.provider, "document_count": len(documents)}
            )
            
            return doc_ids
            
        except Exception as e:
            logger.error(f"Error batch indexing documents: {e}")
            
            # Record error metric
            self.metrics.record(
                "batch_indexing_error",
                1,
                {"provider": self.provider, "error_type": type(e).__name__}
            )
            
            raise FrameworkException(
                f"Failed to batch index documents: {str(e)}",
                code="BATCH_INDEXING_ERROR"
            )
    
    def search(self, request: SearchRequest) -> List[SearchResult]:
        """Search the vector database."""
        start_time = time.time()
        
        try:
            # Ensure the request has either a query or a query embedding
            if not request.query and not request.query_embedding:
                raise FrameworkException(
                    "Search request must have either a query or a query embedding",
                    code="INVALID_SEARCH_REQUEST"
                )
            
            # Perform the search
            results = self.client.search(request)
            
            # Record metrics
            search_time = time.time() - start_time
            self.metrics.record(
                "vector_search_duration",
                search_time,
                {"provider": self.provider, "result_count": len(results)}
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching vector database: {e}")
            
            # Record error metric
            self.metrics.record(
                "vector_search_error",
                1,
                {"provider": self.provider, "error_type": type(e).__name__}
            )
            
            raise FrameworkException(
                f"Failed to search vector database: {str(e)}",
                code="SEARCH_ERROR",
                details={"query": request.query}
            )
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document from the vector database."""
        try:
            # Delete the document
            success = self.client.delete_document(document_id)
            
            # Record metric
            self.metrics.record(
                "document_deletion",
                1,
                {"provider": self.provider, "success": success}
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            
            # Record error metric
            self.metrics.record(
                "document_deletion_error",
                1,
                {"provider": self.provider, "error_type": type(e).__name__}
            )
            
            raise FrameworkException(
                f"Failed to delete document: {str(e)}",
                code="DELETION_ERROR",
                details={"document_id": document_id}
            )
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the vector database."""
        status = "healthy"
        message = "Vector Database is healthy"
        
        try:
            # Check connection to the vector database
            self.client.health_check()
        except Exception as e:
            status = "unhealthy"
            message = f"Health check failed: {str(e)}"
        
        return {
            "status": status,
            "message": message,
            "timestamp": time.time(),
            "details": {
                "provider": self.provider,
                "index_name": self.config.index_name
            }
        }

class MockVectorDB:
    """Mock implementation of a vector database client for development and testing."""
    
    def __init__(self, provider: str, config: VectorDBConfig):
        """Initialize the mock vector database."""
        self.provider = provider
        self.config = config
        self.documents = {}  # In-memory storage for documents
        logger.info(f"Initialized mock {provider} vector database")
    
    def index_document(self, document: VectorDBDocument) -> str:
        """Index a document in the mock vector database."""
        # Store the document in memory
        self.documents[document.id] = document
        logger.info(f"Indexed document with ID: {document.id}")
        return document.id
    
    def batch_index_documents(self, documents: List[VectorDBDocument]) -> List[str]:
        """Index multiple documents in the mock vector database."""
        doc_ids = []
        for doc in documents:
            self.documents[doc.id] = doc
            doc_ids.append(doc.id)
        logger.info(f"Batch indexed {len(documents)} documents")
        return doc_ids
    
    def search(self, request: SearchRequest) -> List[SearchResult]:
        """Search the mock vector database."""
        # This is a simplified implementation that doesn't actually use vector similarity
        # In a real system, this would perform actual vector similarity search
        
        # If we have a query embedding, use it for similarity search
        if request.query_embedding:
            # Mock similarity calculation
            results = []
            for i, (doc_id, doc) in enumerate(self.documents.items()):
                if doc.embedding:
                    # Calculate cosine similarity (simplified)
                    similarity = 0.5 + (0.5 * np.random.random())  # Random similarity between 0.5 and 1.0
                    
                    # Apply filters if specified
                    if request.filter:
                        # Check if document metadata matches all filter criteria
                        matches_filter = all(
                            key in doc.metadata and doc.metadata[key] == value
                            for key, value in request.filter.items()
                        )
                        if not matches_filter:
                            continue
                    
                    results.append(SearchResult(
                        document=doc,
                        score=similarity,
                        rank=i + 1
                    ))
            
            # Sort by score and limit to top_k
            results.sort(key=lambda x: x.score, reverse=True)
            results = results[:request.top_k]
            
            # Update ranks
            for i, result in enumerate(results):
                result.rank = i + 1
            
            return results
        
        # If we only have a text query, do a simple text search
        else:
            query_lower = request.query.lower()
            results = []
            for i, (doc_id, doc) in enumerate(self.documents.items()):
                # Check if query is in document text
                if query_lower in doc.text.lower():
                    # Calculate a mock relevance score
                    score = 0.5 + (0.5 * np.random.random())  # Random score between 0.5 and 1.0
                    
                    # Apply filters if specified
                    if request.filter:
                        # Check if document metadata matches all filter criteria
                        matches_filter = all(
                            key in doc.metadata and doc.metadata[key] == value
                            for key, value in request.filter.items()
                        )
                        if not matches_filter:
                            continue
                    
                    results.append(SearchResult(
                        document=doc,
                        score=score,
                        rank=i + 1
                    ))
            
            # Sort by score and limit to top_k
            results.sort(key=lambda x: x.score, reverse=True)
            results = results[:request.top_k]
            
            # Update ranks
            for i, result in enumerate(results):
                result.rank = i + 1
            
            return results
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document from the mock vector database."""
        if document_id in self.documents:
            del self.documents[document_id]
            logger.info(f"Deleted document with ID: {document_id}")
            return True
        else:
            logger.warning(f"Document not found for deletion: {document_id}")
            return False
    
    def health_check(self) -> bool:
        """Perform a health check on the mock vector database."""
        # Mock health check always succeeds
        return True

# Initialize global instance
vector_db_client = None

def get_vector_db_client():
    """Get or create the vector database client instance."""
    global vector_db_client
    if vector_db_client is None:
        vector_db_client = VectorDBClient()
    return vector_db_client
