"""
API Gateway module for the Enhanced MLOps Framework for Agentic AI RAG Workflows.

This module provides a FastAPI-based API gateway for the framework,
exposing endpoints for RAG queries, document management, and system monitoring.
"""

import os
import logging
import time
import json
import asyncio
from typing import Dict, Any, Optional, List, Union
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from ..core import FrameworkException, ServiceRegistry
from ..core.config import APIGatewayConfig, ConfigManager
from ..serving.service import RAGRequest, RAGResponse, get_serving_service
from ..document_processing.processor import Document, get_document_processor
from ..monitoring.service import get_monitoring_service
from ..compliance.service import get_compliance_service
from ..evaluation.service import get_evaluation_service
from ..cost_optimization.service import get_cost_optimization_service

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced MLOps Framework for Agentic AI RAG Workflows",
    description="API Gateway for medical customer support RAG workflows",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class QueryRequest(BaseModel):
    """Model for a query request."""
    
    query: str = Field(..., description="User query to process")
    session_id: Optional[str] = Field(None, description="Session identifier for conversation context")
    user_id: Optional[str] = Field(None, description="User identifier")
    stream: bool = Field(False, description="Whether to stream the response")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context for the request")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the request")

class DocumentUploadRequest(BaseModel):
    """Model for a document upload request."""
    
    title: str = Field(..., description="Document title")
    text: str = Field(..., description="Document text content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")

# Response models
class QueryResponse(BaseModel):
    """Model for a query response."""
    
    response_text: str = Field(..., description="Response text")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Sources used for the response")
    processing_time: float = Field(..., description="Time taken to process the request in seconds")
    session_id: Optional[str] = Field(None, description="Session identifier for conversation context")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the response")

class DocumentUploadResponse(BaseModel):
    """Model for a document upload response."""
    
    document_id: str = Field(..., description="Identifier for the uploaded document")
    status: str = Field(..., description="Status of the upload")
    processing_time: float = Field(..., description="Time taken to process the upload in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the upload")

class HealthCheckResponse(BaseModel):
    """Model for a health check response."""
    
    status: str = Field(..., description="Overall system status")
    components: Dict[str, Dict[str, Any]] = Field(..., description="Status of individual components")
    timestamp: float = Field(..., description="Timestamp of the health check")

# Service initialization
def get_config():
    """Get the API gateway configuration."""
    config_manager = ConfigManager()
    app_config = config_manager.get_config()
    return app_config.api_gateway

# Initialize services on startup
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Initializing API Gateway services")
    
    # Initialize services
    get_serving_service()
    get_document_processor()
    get_monitoring_service()
    get_compliance_service()
    get_evaluation_service()
    get_cost_optimization_service()
    
    logger.info("API Gateway services initialized")

# API endpoints
@app.post("/api/v1/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Process a query and return a response."""
    start_time = time.time()
    
    try:
        # Convert to RAG request
        rag_request = RAGRequest(
            query=request.query,
            session_id=request.session_id,
            user_id=request.user_id,
            stream=request.stream,
            context=request.context,
            metadata=request.metadata
        )
        
        # Get serving service
        serving_service = get_serving_service()
        
        # Process request
        response = serving_service.process_request(rag_request)
        
        # Convert to API response
        api_response = QueryResponse(
            response_text=response.response_text,
            sources=response.sources,
            processing_time=response.processing_time,
            session_id=response.session_id,
            metadata=response.metadata
        )
        
        return api_response
        
    except FrameworkException as e:
        logger.error(f"Framework error processing query: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error processing query: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/v1/query/stream")
async def query_stream(request: QueryRequest):
    """Process a query and stream the response."""
    try:
        # Ensure streaming is enabled
        request.stream = True
        
        # Convert to RAG request
        rag_request = RAGRequest(
            query=request.query,
            session_id=request.session_id,
            user_id=request.user_id,
            stream=True,
            context=request.context,
            metadata=request.metadata
        )
        
        # Get serving service
        serving_service = get_serving_service()
        
        # Define streaming response generator
        async def response_generator():
            async for chunk in serving_service.process_request_streaming(rag_request):
                yield json.dumps(chunk.dict()) + "\n"
        
        # Return streaming response
        return StreamingResponse(
            response_generator(),
            media_type="application/x-ndjson"
        )
        
    except FrameworkException as e:
        logger.error(f"Framework error processing streaming query: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error processing streaming query: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/v1/documents", response_model=DocumentUploadResponse)
async def upload_document(request: DocumentUploadRequest):
    """Upload a document for indexing."""
    start_time = time.time()
    
    try:
        # Create document
        document = Document(
            title=request.title,
            text=request.text,
            metadata=request.metadata
        )
        
        # Get document processor
        document_processor = get_document_processor()
        
        # Process document
        result = document_processor.process_document(document)
        
        # Create response
        processing_time = time.time() - start_time
        response = DocumentUploadResponse(
            document_id=result.document_id,
            status="success",
            processing_time=processing_time,
            metadata={
                "chunks": result.chunk_count,
                "indexed": result.indexed
            }
        )
        
        return response
        
    except FrameworkException as e:
        logger.error(f"Framework error uploading document: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error uploading document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/health", response_model=HealthCheckResponse)
async def health_check():
    """Check the health of the system."""
    try:
        # Get services
        serving_service = get_serving_service()
        document_processor = get_document_processor()
        monitoring_service = get_monitoring_service()
        compliance_service = get_compliance_service()
        evaluation_service = get_evaluation_service()
        cost_optimization_service = get_cost_optimization_service()
        
        # Check health of each service
        serving_health = serving_service.health_check()
        document_health = document_processor.health_check()
        monitoring_health = monitoring_service.health_check()
        compliance_health = compliance_service.health_check()
        evaluation_health = evaluation_service.health_check()
        cost_health = cost_optimization_service.health_check()
        
        # Determine overall status
        status = "healthy"
        if any(s["status"] != "healthy" for s in [
            serving_health, document_health, monitoring_health,
            compliance_health, evaluation_health, cost_health
        ]):
            status = "warning"
        
        # Create response
        response = HealthCheckResponse(
            status=status,
            components={
                "serving": serving_health,
                "document_processing": document_health,
                "monitoring": monitoring_health,
                "compliance": compliance_health,
                "evaluation": evaluation_health,
                "cost_optimization": cost_health
            },
            timestamp=time.time()
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error checking health: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            components={},
            timestamp=time.time()
        )

@app.get("/api/v1/metrics")
async def get_metrics():
    """Get system metrics."""
    try:
        # Get monitoring service
        monitoring_service = get_monitoring_service()
        
        # Get metrics
        metrics = monitoring_service.get_metrics()
        
        return JSONResponse(content=metrics)
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving metrics")

# Error handling
@app.exception_handler(FrameworkException)
async def framework_exception_handler(request: Request, exc: FrameworkException):
    """Handle framework exceptions."""
    return JSONResponse(
        status_code=400,
        content={
            "error": str(exc),
            "code": exc.code,
            "details": exc.details
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "details": str(exc) if os.getenv("DEBUG") == "true" else None
        }
    )

# Main entry point
def start_api_gateway():
    """Start the API gateway."""
    import uvicorn
    
    # Get configuration
    config = get_config()
    
    # Start server
    uvicorn.run(
        "src.api_gateway.main:app",
        host=config.host,
        port=config.port,
        reload=config.reload_enabled
    )

if __name__ == "__main__":
    start_api_gateway()
