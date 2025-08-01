"""
Document Processing module for the Enhanced MLOps Framework for Agentic AI RAG Workflows.

This module provides functionality for processing documents, including chunking,
embedding generation, and metadata extraction for medical customer support scenarios.
"""

import os
import logging
from typing import Dict, Any, Optional, List, Union
import time
import json
import re
from pydantic import BaseModel, Field

from ..core import FrameworkException, ServiceRegistry, MetricsCollector
from ..core.config import DocumentProcessingConfig, ConfigManager
from ..vector_db.client import VectorDBDocument, get_vector_db_client

logger = logging.getLogger(__name__)

class Document(BaseModel):
    """Model for a document to be processed."""
    
    id: Optional[str] = Field(None, description="Unique identifier for the document")
    content: str = Field(..., description="Text content of the document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata for the document")
    source: Optional[str] = Field(None, description="Source of the document")
    file_type: Optional[str] = Field(None, description="File type of the original document")

class DocumentChunk(BaseModel):
    """Model for a chunk of a document."""
    
    id: str = Field(..., description="Unique identifier for the chunk")
    document_id: str = Field(..., description="ID of the parent document")
    content: str = Field(..., description="Text content of the chunk")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata for the chunk")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding of the chunk")
    chunk_index: int = Field(..., description="Index of the chunk within the document")

class ProcessingResult(BaseModel):
    """Model for the result of document processing."""
    
    document_id: str = Field(..., description="ID of the processed document")
    chunk_count: int = Field(..., description="Number of chunks created")
    indexed_count: int = Field(..., description="Number of chunks indexed")
    processing_time: float = Field(..., description="Time taken to process the document in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata extracted from the document")
    medical_entities: List[Dict[str, Any]] = Field(default_factory=list, description="Medical entities extracted from the document")

class DocumentProcessor:
    """Processor for documents in RAG workflows."""
    
    def __init__(self, config: DocumentProcessingConfig = None):
        """Initialize the document processor with configuration."""
        if config is None:
            config_manager = ConfigManager()
            app_config = config_manager.get_config()
            config = app_config.document_processing
        
        self.config = config
        self.metrics = MetricsCollector()
        
        # Get vector database client
        self.vector_db_client = get_vector_db_client()
        
        # Register with service registry
        service_registry = ServiceRegistry()
        service_registry.register("document_processor", self)
        
        logger.info("Document Processor initialized")
    
    def process_document(self, document: Document) -> ProcessingResult:
        """Process a document for RAG workflows."""
        start_time = time.time()
        
        try:
            # Generate document ID if not provided
            if not document.id:
                document.id = f"doc_{int(time.time())}_{hash(document.content) % 10000}"
            
            # Extract metadata if enabled
            if self.config.extract_metadata:
                self._extract_metadata(document)
            
            # Extract medical entities if enabled
            medical_entities = []
            if self.config.medical_entity_extraction:
                medical_entities = self._extract_medical_entities(document)
            
            # Chunk the document
            chunks = self._chunk_document(document)
            
            # Generate embeddings for chunks
            chunks_with_embeddings = self._generate_embeddings(chunks)
            
            # Index chunks in vector database
            indexed_count = 0
            for chunk in chunks_with_embeddings:
                # Convert to VectorDBDocument
                vector_doc = VectorDBDocument(
                    id=chunk.id,
                    text=chunk.content,
                    metadata={
                        **chunk.metadata,
                        "document_id": document.id,
                        "chunk_index": chunk.chunk_index
                    },
                    embedding=chunk.embedding
                )
                
                # Index in vector database
                self.vector_db_client.index_document(vector_doc)
                indexed_count += 1
            
            # Record metrics
            processing_time = time.time() - start_time
            self.metrics.record(
                "document_processing_duration",
                processing_time,
                {"chunk_count": len(chunks)}
            )
            
            # Create and return processing result
            result = ProcessingResult(
                document_id=document.id,
                chunk_count=len(chunks),
                indexed_count=indexed_count,
                processing_time=processing_time,
                metadata=document.metadata,
                medical_entities=medical_entities
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            
            # Record error metric
            self.metrics.record(
                "document_processing_error",
                1,
                {"error_type": type(e).__name__}
            )
            
            raise FrameworkException(
                f"Failed to process document: {str(e)}",
                code="PROCESSING_ERROR",
                details={"document_id": document.id if document.id else "unknown"}
            )
    
    def _extract_metadata(self, document: Document) -> None:
        """Extract metadata from a document."""
        # This is a simplified implementation
        # In a real system, this would use more sophisticated metadata extraction
        
        # Extract basic metadata
        word_count = len(document.content.split())
        document.metadata["word_count"] = word_count
        
        # Extract document type if not already set
        if not document.file_type and document.source:
            file_extension = os.path.splitext(document.source)[1].lower()
            if file_extension:
                document.file_type = file_extension[1:]  # Remove the dot
                document.metadata["file_type"] = document.file_type
        
        # Extract creation date if available in the source
        if document.source and os.path.exists(document.source):
            try:
                mtime = os.path.getmtime(document.source)
                document.metadata["creation_date"] = time.strftime("%Y-%m-%d", time.localtime(mtime))
            except Exception as e:
                logger.warning(f"Failed to extract creation date: {e}")
        
        logger.debug(f"Extracted metadata: {document.metadata}")
    
    def _extract_medical_entities(self, document: Document) -> List[Dict[str, Any]]:
        """Extract medical entities from a document."""
        # This is a mock implementation
        # In a real system, this would use NER models or medical entity extraction services
        
        medical_entities = []
        
        # Simple pattern matching for common medical terms
        patterns = {
            "medication": r"\b(aspirin|ibuprofen|acetaminophen|lisinopril|metformin|atorvastatin)\b",
            "condition": r"\b(diabetes|hypertension|asthma|arthritis|depression|anxiety)\b",
            "procedure": r"\b(surgery|biopsy|transplant|injection|infusion|examination)\b",
            "anatomy": r"\b(heart|lung|liver|kidney|brain|spine)\b"
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.finditer(pattern, document.content, re.IGNORECASE)
            for match in matches:
                entity = {
                    "type": entity_type,
                    "text": match.group(0),
                    "start": match.start(),
                    "end": match.end()
                }
                medical_entities.append(entity)
        
        # Add to document metadata
        if medical_entities:
            entity_types = set(entity["type"] for entity in medical_entities)
            document.metadata["medical_entity_types"] = list(entity_types)
            document.metadata["medical_entity_count"] = len(medical_entities)
        
        logger.debug(f"Extracted {len(medical_entities)} medical entities")
        return medical_entities
    
    def _chunk_document(self, document: Document) -> List[DocumentChunk]:
        """Chunk a document based on the configured strategy."""
        chunks = []
        
        if self.config.chunking_strategy == "fixed":
            chunks = self._fixed_size_chunking(document)
        elif self.config.chunking_strategy == "recursive":
            chunks = self._recursive_chunking(document)
        elif self.config.chunking_strategy == "semantic":
            chunks = self._semantic_chunking(document)
        elif self.config.chunking_strategy == "medical_section":
            chunks = self._medical_section_chunking(document)
        else:
            raise FrameworkException(
                f"Unsupported chunking strategy: {self.config.chunking_strategy}",
                code="UNSUPPORTED_CHUNKING_STRATEGY"
            )
        
        logger.debug(f"Created {len(chunks)} chunks using {self.config.chunking_strategy} strategy")
        return chunks
    
    def _fixed_size_chunking(self, document: Document) -> List[DocumentChunk]:
        """Chunk a document into fixed-size chunks."""
        chunks = []
        content = document.content
        chunk_size = self.config.chunk_size
        chunk_overlap = self.config.chunk_overlap
        
        # Split content into chunks
        start = 0
        chunk_index = 0
        
        while start < len(content):
            # Calculate end position with overlap
            end = min(start + chunk_size, len(content))
            
            # Extract chunk content
            chunk_content = content[start:end]
            
            # Create chunk
            chunk = DocumentChunk(
                id=f"{document.id}_chunk_{chunk_index}",
                document_id=document.id,
                content=chunk_content,
                metadata=document.metadata.copy(),
                chunk_index=chunk_index
            )
            
            chunks.append(chunk)
            
            # Move to next chunk with overlap
            start = end - chunk_overlap if end < len(content) else end
            chunk_index += 1
        
        return chunks
    
    def _recursive_chunking(self, document: Document) -> List[DocumentChunk]:
        """Chunk a document recursively based on sections and paragraphs."""
        # This is a simplified implementation
        # In a real system, this would use more sophisticated recursive chunking
        
        # First split by sections (using headers as delimiters)
        section_pattern = r"(?:^|\n)#+\s+(.+?)(?=\n#+\s+|\Z)"
        sections = re.split(section_pattern, document.content)
        
        chunks = []
        chunk_index = 0
        
        for section in sections:
            if not section.strip():
                continue
            
            # If section is small enough, use it as a chunk
            if len(section) <= self.config.chunk_size:
                chunk = DocumentChunk(
                    id=f"{document.id}_chunk_{chunk_index}",
                    document_id=document.id,
                    content=section,
                    metadata=document.metadata.copy(),
                    chunk_index=chunk_index
                )
                chunks.append(chunk)
                chunk_index += 1
            else:
                # Split section into paragraphs
                paragraphs = re.split(r"\n\s*\n", section)
                
                current_chunk = ""
                for paragraph in paragraphs:
                    if not paragraph.strip():
                        continue
                    
                    # If adding paragraph would exceed chunk size, create a new chunk
                    if len(current_chunk) + len(paragraph) > self.config.chunk_size:
                        if current_chunk:
                            chunk = DocumentChunk(
                                id=f"{document.id}_chunk_{chunk_index}",
                                document_id=document.id,
                                content=current_chunk,
                                metadata=document.metadata.copy(),
                                chunk_index=chunk_index
                            )
                            chunks.append(chunk)
                            chunk_index += 1
                            current_chunk = ""
                    
                    # Add paragraph to current chunk
                    if current_chunk:
                        current_chunk += "\n\n"
                    current_chunk += paragraph
                
                # Add the last chunk if not empty
                if current_chunk:
                    chunk = DocumentChunk(
                        id=f"{document.id}_chunk_{chunk_index}",
                        document_id=document.id,
                        content=current_chunk,
                        metadata=document.metadata.copy(),
                        chunk_index=chunk_index
                    )
                    chunks.append(chunk)
                    chunk_index += 1
        
        return chunks
    
    def _semantic_chunking(self, document: Document) -> List[DocumentChunk]:
        """Chunk a document based on semantic boundaries."""
        # This is a mock implementation
        # In a real system, this would use more sophisticated semantic chunking
        
        # For now, just use recursive chunking as a fallback
        logger.warning("Semantic chunking not fully implemented, falling back to recursive chunking")
        return self._recursive_chunking(document)
    
    def _medical_section_chunking(self, document: Document) -> List[DocumentChunk]:
        """Chunk a medical document based on medical sections."""
        # This is a mock implementation
        # In a real system, this would use medical document structure knowledge
        
        # Common medical document sections
        section_patterns = [
            r"(?:^|\n)(?:patient\s+information|demographics)(?:\s*:)?(?=\n|$)",
            r"(?:^|\n)(?:medical\s+history|history)(?:\s*:)?(?=\n|$)",
            r"(?:^|\n)(?:medications|current\s+medications)(?:\s*:)?(?=\n|$)",
            r"(?:^|\n)(?:allergies)(?:\s*:)?(?=\n|$)",
            r"(?:^|\n)(?:vital\s+signs|vitals)(?:\s*:)?(?=\n|$)",
            r"(?:^|\n)(?:symptoms|chief\s+complaint)(?:\s*:)?(?=\n|$)",
            r"(?:^|\n)(?:diagnosis|assessment)(?:\s*:)?(?=\n|$)",
            r"(?:^|\n)(?:treatment\s+plan|plan)(?:\s*:)?(?=\n|$)",
            r"(?:^|\n)(?:follow\s*-?\s*up|followup)(?:\s*:)?(?=\n|$)"
        ]
        
        # Combine patterns
        combined_pattern = "|".join(section_patterns)
        
        # Split document by sections
        sections = re.split(combined_pattern, document.content)
        section_headers = re.findall(combined_pattern, document.content)
        
        chunks = []
        chunk_index = 0
        
        # Process each section
        current_section = ""
        for i, section_content in enumerate(sections):
            # Skip empty sections
            if not section_content.strip():
                continue
            
            # Get section header if available
            section_header = section_headers[i-1] if i > 0 and i-1 < len(section_headers) else "Introduction"
            
            # Clean up section header
            section_header = re.sub(r"[\n:]", "", section_header).strip()
            
            # Create metadata for this section
            section_metadata = document.metadata.copy()
            section_metadata["section"] = section_header
            
            # Create chunk
            chunk = DocumentChunk(
                id=f"{document.id}_chunk_{chunk_index}",
                document_id=document.id,
                content=section_content,
                metadata=section_metadata,
                chunk_index=chunk_index
            )
            chunks.append(chunk)
            chunk_index += 1
        
        return chunks
    
    def _generate_embeddings(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Generate embeddings for document chunks."""
        # This is a mock implementation
        # In a real system, this would use actual embedding models
        
        for chunk in chunks:
            # Generate a mock embedding
            # In a real system, this would call an embedding model API
            embedding_dim = self.config.embedding_model == "text-embedding-ada-002" and 1536 or 768
            chunk.embedding = [0.1] * embedding_dim  # Mock embedding
        
        logger.debug(f"Generated embeddings for {len(chunks)} chunks")
        return chunks
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the document processor."""
        status = "healthy"
        message = "Document Processor is healthy"
        
        try:
            # Check vector database client
            vector_db_status = self.vector_db_client.health_check()
            if vector_db_status["status"] != "healthy":
                status = "warning"
                message = f"Vector database issue: {vector_db_status['message']}"
        except Exception as e:
            status = "unhealthy"
            message = f"Health check failed: {str(e)}"
        
        return {
            "status": status,
            "message": message,
            "timestamp": time.time(),
            "details": {
                "chunking_strategy": self.config.chunking_strategy,
                "embedding_model": self.config.embedding_model
            }
        }

# Initialize global instance
document_processor = None

def get_document_processor():
    """Get or create the document processor instance."""
    global document_processor
    if document_processor is None:
        document_processor = DocumentProcessor()
    return document_processor
