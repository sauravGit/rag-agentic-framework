"""
API Gateway for the Enhanced MLOps Framework for Agentic AI RAG Workflows.

This module serves as the central entry point for all framework services.
"""
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from typing import Dict, Any, Optional

from core.config import ServiceConfig

app = FastAPI(
    title="Enhanced MLOps Framework API Gateway",
    description="API Gateway for the Enhanced MLOps Framework for Agentic AI RAG Workflows",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service configurations
document_processor = ServiceConfig(
    service_name="document-processor",
    host=os.environ.get("DOCUMENT_PROCESSOR_HOST", "document-processor"),
    port=8001,
)

agent_orchestrator = ServiceConfig(
    service_name="agent-orchestrator",
    host=os.environ.get("AGENT_ORCHESTRATOR_HOST", "agent-orchestrator"),
    port=8000,
)

vector_db_service = ServiceConfig(
    service_name="vector-db-service",
    host=os.environ.get("VECTOR_DB_HOST", "vector-db"),
    port=9200,
)

compliance_service = ServiceConfig(
    service_name="compliance-service",
    host=os.environ.get("COMPLIANCE_SERVICE_HOST", "compliance-service"),
    port=8002,
)

@app.get("/")
async def root():
    """Root endpoint for the API Gateway."""
    return {
        "message": "Welcome to the Enhanced MLOps Framework for Agentic AI RAG Workflows",
        "version": "0.1.0",
        "services": {
            "document_processor": document_processor.base_url,
            "agent_orchestrator": agent_orchestrator.base_url,
            "vector_db": f"http://{vector_db_service.host}:{vector_db_service.port}",
            "compliance_service": compliance_service.base_url,
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for the API Gateway."""
    return {"status": "healthy"}

@app.post("/api/v1/documents")
async def process_document(request: Request):
    """Process a document through the document processing pipeline."""
    try:
        payload = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{document_processor.base_url}/documents",
                json=payload,
                timeout=30.0
            )
            return response.json()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Document processor service unavailable: {str(exc)}")

@app.post("/api/v1/query")
async def query_agent(request: Request):
    """Query the agent with a natural language question."""
    try:
        payload = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{agent_orchestrator.base_url}/query",
                json=payload,
                timeout=60.0
            )
            return response.json()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Agent orchestrator service unavailable: {str(exc)}")

@app.get("/api/v1/documents/{document_id}")
async def get_document(document_id: str):
    """Get a document by ID."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{document_processor.base_url}/documents/{document_id}",
                timeout=10.0
            )
            return response.json()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Document processor service unavailable: {str(exc)}")

@app.get("/api/v1/status")
async def get_system_status():
    """Get the status of all system components."""
    statuses = {}
    
    async with httpx.AsyncClient() as client:
        # Check document processor
        try:
            response = await client.get(f"{document_processor.base_url}/health", timeout=2.0)
            statuses["document_processor"] = "healthy" if response.status_code == 200 else "unhealthy"
        except:
            statuses["document_processor"] = "unavailable"
            
        # Check agent orchestrator
        try:
            response = await client.get(f"{agent_orchestrator.base_url}/health", timeout=2.0)
            statuses["agent_orchestrator"] = "healthy" if response.status_code == 200 else "unhealthy"
        except:
            statuses["agent_orchestrator"] = "unavailable"
            
        # Check vector db
        try:
            response = await client.get(f"http://{vector_db_service.host}:{vector_db_service.port}", timeout=2.0)
            statuses["vector_db"] = "healthy" if response.status_code == 200 else "unhealthy"
        except:
            statuses["vector_db"] = "unavailable"
            
        # Check compliance service
        try:
            response = await client.get(f"{compliance_service.base_url}/health", timeout=2.0)
            statuses["compliance_service"] = "healthy" if response.status_code == 200 else "unhealthy"
        except:
            statuses["compliance_service"] = "unavailable"
    
    return {
        "status": "healthy" if all(s == "healthy" for s in statuses.values()) else "degraded",
        "components": statuses
    }
