"""
Serving module for the Enhanced MLOps Framework for Agentic AI RAG Workflows.

This module provides functionality for serving RAG responses to users,
including streaming, response formatting, and result caching for medical customer support scenarios.
"""

import os
import logging
from typing import Dict, Any, Optional, List, Union, Generator, AsyncGenerator
import time
import json
import asyncio
from pydantic import BaseModel, Field

from ..core import FrameworkException, ServiceRegistry, MetricsCollector
from ..core.config import ServingConfig, ConfigManager
from ..agent_orchestration.orchestrator import AgentRequest, AgentResponse, get_agent_orchestrator
from ..vector_db.client import SearchRequest, get_vector_db_client
from ..document_processing.processor import Document, get_document_processor
from ..compliance.service import ComplianceCheck, get_compliance_service
from ..evaluation.service import EvaluationRequest, get_evaluation_service
from ..cost_optimization.service import CostOptimizationRequest, get_cost_optimization_service

logger = logging.getLogger(__name__)

class RAGRequest(BaseModel):
    """Model for a RAG request."""
    
    query: str = Field(..., description="User query to process")
    session_id: Optional[str] = Field(None, description="Session identifier for conversation context")
    user_id: Optional[str] = Field(None, description="User identifier")
    stream: bool = Field(False, description="Whether to stream the response")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context for the request")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the request")

class RAGResponse(BaseModel):
    """Model for a RAG response."""
    
    response_text: str = Field(..., description="Response text")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Sources used for the response")
    processing_time: float = Field(..., description="Time taken to process the request in seconds")
    session_id: Optional[str] = Field(None, description="Session identifier for conversation context")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the response")

class StreamingChunk(BaseModel):
    """Model for a streaming response chunk."""
    
    chunk_text: str = Field(..., description="Text chunk")
    chunk_index: int = Field(..., description="Index of the chunk")
    is_final: bool = Field(False, description="Whether this is the final chunk")
    sources: Optional[List[Dict[str, Any]]] = Field(None, description="Sources (only in final chunk)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the chunk")

class ServingService:
    """Service for serving RAG responses to users."""
    
    def __init__(self, config: ServingConfig = None):
        """Initialize the serving service with configuration."""
        if config is None:
            config_manager = ConfigManager()
            app_config = config_manager.get_config()
            config = app_config.serving
        
        self.config = config
        self.metrics = MetricsCollector()
        
        # Get required services
        self.agent_orchestrator = get_agent_orchestrator()
        self.vector_db_client = get_vector_db_client()
        self.document_processor = get_document_processor()
        self.compliance_service = get_compliance_service()
        self.evaluation_service = get_evaluation_service()
        self.cost_optimization_service = get_cost_optimization_service()
        
        # Initialize response cache if enabled
        self.response_cache = {}
        
        # Register with service registry
        service_registry = ServiceRegistry()
        service_registry.register("serving_service", self)
        
        logger.info("Serving Service initialized")
    
    def process_request(self, request: RAGRequest) -> RAGResponse:
        """Process a RAG request and return a response."""
        start_time = time.time()
        
        try:
            # Apply cost optimization if enabled
            optimized_request = self._apply_cost_optimization(request)
            
            # Check cache if enabled
            if self.config.response_caching_enabled:
                cache_key = self._generate_cache_key(optimized_request.query, optimized_request.context)
                cached_response = self.response_cache.get(cache_key)
                if cached_response:
                    logger.info(f"Cache hit for query: {optimized_request.query}")
                    
                    # Record cache hit metric
                    self.metrics.record("serving_cache_hit", 1, {})
                    
                    # Update processing time and return cached response
                    processing_time = time.time() - start_time
                    cached_response.processing_time = processing_time
                    return cached_response
            
            # Retrieve relevant documents
            search_results = self._retrieve_documents(optimized_request)
            
            # Process with agent orchestrator
            agent_response = self._process_with_agent(optimized_request, search_results)
            
            # Apply compliance checks if enabled
            if self.config.compliance_checking_enabled:
                agent_response = self._apply_compliance_checks(agent_response, optimized_request)
            
            # Format response
            response = self._format_response(agent_response, search_results, optimized_request)
            
            # Apply evaluation if enabled
            if self.config.evaluation_enabled:
                self._evaluate_response(response, optimized_request, search_results)
            
            # Update cache if enabled
            if self.config.response_caching_enabled:
                cache_key = self._generate_cache_key(optimized_request.query, optimized_request.context)
                self.response_cache[cache_key] = response
                
                # Trim cache if it exceeds max size
                if len(self.response_cache) > self.config.max_cache_size:
                    # Simple LRU implementation: just remove oldest entries
                    keys_to_remove = list(self.response_cache.keys())[:-self.config.max_cache_size]
                    for key in keys_to_remove:
                        del self.response_cache[key]
            
            # Record metrics
            processing_time = time.time() - start_time
            self.metrics.record(
                "serving_request_duration",
                processing_time,
                {"stream": request.stream}
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing RAG request: {e}")
            
            # Record error metric
            self.metrics.record(
                "serving_request_error",
                1,
                {"error_type": type(e).__name__}
            )
            
            raise FrameworkException(
                f"Failed to process RAG request: {str(e)}",
                code="SERVING_ERROR",
                details={"query": request.query}
            )
    
    async def process_request_streaming(self, request: RAGRequest) -> AsyncGenerator[StreamingChunk, None]:
        """Process a RAG request and stream the response."""
        if not request.stream:
            request.stream = True  # Ensure streaming is enabled
        
        start_time = time.time()
        chunk_index = 0
        
        try:
            # Apply cost optimization if enabled
            optimized_request = self._apply_cost_optimization(request)
            
            # Check cache if enabled
            cached_response = None
            if self.config.response_caching_enabled:
                cache_key = self._generate_cache_key(optimized_request.query, optimized_request.context)
                cached_response = self.response_cache.get(cache_key)
                if cached_response:
                    logger.info(f"Cache hit for streaming query: {optimized_request.query}")
                    
                    # Record cache hit metric
                    self.metrics.record("serving_cache_hit", 1, {"streaming": True})
                    
                    # Stream cached response in chunks
                    chunk_size = 20  # Characters per chunk
                    response_text = cached_response.response_text
                    
                    for i in range(0, len(response_text), chunk_size):
                        chunk_text = response_text[i:i+chunk_size]
                        is_final = i + chunk_size >= len(response_text)
                        
                        chunk = StreamingChunk(
                            chunk_text=chunk_text,
                            chunk_index=chunk_index,
                            is_final=is_final,
                            sources=cached_response.sources if is_final else None,
                            metadata={"cached": True}
                        )
                        
                        yield chunk
                        chunk_index += 1
                        
                        # Simulate streaming delay
                        await asyncio.sleep(0.1)
                    
                    return
            
            # Retrieve relevant documents
            search_results = self._retrieve_documents(optimized_request)
            
            # Process with agent orchestrator (streaming mode)
            # This is a simplified implementation
            # In a real system, this would use actual streaming from the agent
            
            # Simulate streaming response
            agent_context = {
                "session_id": optimized_request.session_id,
                "documents": [doc["text"] for doc in search_results],
                "stream": True
            }
            
            agent_request = AgentRequest(
                query=optimized_request.query,
                session_id=optimized_request.session_id,
                context=agent_context,
                stream=True
            )
            
            # Get full response first (simplified implementation)
            agent_response = self.agent_orchestrator.process_request(agent_request)
            
            # Apply compliance checks if enabled
            if self.config.compliance_checking_enabled:
                agent_response = self._apply_compliance_checks(agent_response, optimized_request)
            
            # Stream the response in chunks
            response_text = agent_response.response_text
            chunk_size = 20  # Characters per chunk
            
            for i in range(0, len(response_text), chunk_size):
                chunk_text = response_text[i:i+chunk_size]
                is_final = i + chunk_size >= len(response_text)
                
                # Format sources for final chunk
                sources = None
                if is_final:
                    sources = []
                    for result in search_results:
                        sources.append({
                            "title": result.get("title", "Document"),
                            "text": result.get("text", "")[:100] + "...",  # Truncate for display
                            "score": result.get("score", 0.0)
                        })
                
                chunk = StreamingChunk(
                    chunk_text=chunk_text,
                    chunk_index=chunk_index,
                    is_final=is_final,
                    sources=sources,
                    metadata={"streaming": True}
                )
                
                yield chunk
                chunk_index += 1
                
                # Simulate streaming delay
                await asyncio.sleep(0.1)
            
            # Format full response for caching
            response = self._format_response(agent_response, search_results, optimized_request)
            
            # Apply evaluation if enabled
            if self.config.evaluation_enabled:
                self._evaluate_response(response, optimized_request, search_results)
            
            # Update cache if enabled
            if self.config.response_caching_enabled:
                cache_key = self._generate_cache_key(optimized_request.query, optimized_request.context)
                self.response_cache[cache_key] = response
            
            # Record metrics
            processing_time = time.time() - start_time
            self.metrics.record(
                "serving_streaming_duration",
                processing_time,
                {"chunk_count": chunk_index}
            )
            
        except Exception as e:
            logger.error(f"Error processing streaming RAG request: {e}")
            
            # Record error metric
            self.metrics.record(
                "serving_streaming_error",
                1,
                {"error_type": type(e).__name__}
            )
            
            # Yield error chunk
            error_chunk = StreamingChunk(
                chunk_text=f"Error: {str(e)}",
                chunk_index=chunk_index,
                is_final=True,
                sources=None,
                metadata={"error": True}
            )
            
            yield error_chunk
    
    def _apply_cost_optimization(self, request: RAGRequest) -> RAGRequest:
        """Apply cost optimization to a request."""
        if not self.config.cost_optimization_enabled:
            return request
        
        try:
            # Create optimization request
            opt_request = CostOptimizationRequest(
                query=request.query,
                context={
                    "session_id": request.session_id,
                    "user_id": request.user_id,
                    "stream": request.stream,
                    **request.context
                },
                metadata=request.metadata
            )
            
            # Get optimization result
            opt_result = self.cost_optimization_service.optimize(opt_request)
            
            # Create optimized request
            optimized_request = RAGRequest(
                query=opt_result.optimized_query or request.query,
                session_id=request.session_id,
                user_id=request.user_id,
                stream=request.stream,
                context={**request.context, **opt_result.optimized_context},
                metadata={**request.metadata, "cost_optimized": True}
            )
            
            # If we have a cache hit, return the cached response
            if opt_result.cache_hit and opt_result.cached_response:
                # In a real implementation, this would return the cached response
                # For now, just log the cache hit
                logger.info(f"Cost optimization cache hit for query: {request.query}")
            
            logger.debug(f"Cost optimization applied: {optimized_request}")
            return optimized_request
            
        except Exception as e:
            logger.warning(f"Error applying cost optimization: {e}")
            # Fall back to original request
            return request
    
    def _retrieve_documents(self, request: RAGRequest) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query."""
        try:
            # Create search request
            search_request = SearchRequest(
                query=request.query,
                filter=request.context.get("filter", {}),
                top_k=request.context.get("top_k", self.config.default_top_k)
            )
            
            # Perform search
            search_results = self.vector_db_client.search(search_request)
            
            # Convert to simplified format
            results = []
            for result in search_results:
                results.append({
                    "id": result.document.id,
                    "text": result.document.text,
                    "metadata": result.document.metadata,
                    "score": result.score,
                    "rank": result.rank
                })
            
            logger.debug(f"Retrieved {len(results)} documents for query: {request.query}")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            # Return empty list on error
            return []
    
    def _process_with_agent(self, request: RAGRequest, search_results: List[Dict[str, Any]]) -> AgentResponse:
        """Process a request with the agent orchestrator."""
        # Prepare agent context
        agent_context = {
            "session_id": request.session_id,
            "documents": [doc["text"] for doc in search_results],
            "document_scores": [doc["score"] for doc in search_results],
            "stream": request.stream,
            **request.context
        }
        
        # Create agent request
        agent_request = AgentRequest(
            query=request.query,
            session_id=request.session_id,
            context=agent_context,
            stream=request.stream
        )
        
        # Process with agent orchestrator
        agent_response = self.agent_orchestrator.process_request(agent_request)
        
        logger.debug(f"Processed with agent: {agent_response.response_text[:50]}...")
        return agent_response
    
    def _apply_compliance_checks(self, agent_response: AgentResponse, request: RAGRequest) -> AgentResponse:
        """Apply compliance checks to a response."""
        try:
            # Create compliance check
            compliance_check = ComplianceCheck(
                content=agent_response.response_text,
                content_type="response",
                metadata={
                    "query": request.query,
                    "session_id": request.session_id,
                    "user_id": request.user_id
                }
            )
            
            # Perform compliance check
            compliance_result = self.compliance_service.check_compliance(compliance_check)
            
            # If not compliant and we have modified content, update the response
            if not compliance_result.compliant and compliance_result.modified_content:
                agent_response.response_text = compliance_result.modified_content
                agent_response.metadata["compliance_modified"] = True
                agent_response.metadata["compliance_issues"] = len(compliance_result.issues)
            
            # Add compliance metadata
            agent_response.metadata["compliant"] = compliance_result.compliant
            
            logger.debug(f"Compliance check: compliant={compliance_result.compliant}")
            return agent_response
            
        except Exception as e:
            logger.warning(f"Error applying compliance checks: {e}")
            # Fall back to original response
            return agent_response
    
    def _format_response(self, agent_response: AgentResponse, search_results: List[Dict[str, Any]], request: RAGRequest) -> RAGResponse:
        """Format a response for the user."""
        # Format sources
        sources = []
        for result in search_results:
            sources.append({
                "title": result.get("metadata", {}).get("title", f"Document {result['id']}"),
                "text": result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"],
                "score": result["score"],
                "metadata": result["metadata"]
            })
        
        # Create response
        response = RAGResponse(
            response_text=agent_response.response_text,
            sources=sources,
            processing_time=agent_response.processing_time,
            session_id=request.session_id,
            metadata={
                **agent_response.metadata,
                "query": request.query,
                "document_count": len(search_results)
            }
        )
        
        # Add medical disclaimer if needed
        if self.config.add_medical_disclaimer and "medical" in request.query.lower():
            disclaimer = "\n\nDisclaimer: This information is for educational purposes only and is not a substitute for professional medical advice. Always consult with a qualified healthcare provider for medical concerns."
            response.response_text += disclaimer
            response.metadata["disclaimer_added"] = True
        
        logger.debug(f"Formatted response with {len(sources)} sources")
        return response
    
    def _evaluate_response(self, response: RAGResponse, request: RAGRequest, search_results: List[Dict[str, Any]]) -> None:
        """Evaluate a response for quality metrics."""
        try:
            # Create evaluation request
            eval_request = EvaluationRequest(
                query=request.query,
                response=response.response_text,
                retrieved_documents=[{"id": doc["id"], "text": doc["text"]} for doc in search_results],
                metadata={
                    "session_id": request.session_id,
                    "user_id": request.user_id
                }
            )
            
            # Perform evaluation asynchronously
            # In a real system, this would be done in a background task
            # For now, just log that evaluation would be performed
            logger.info(f"Evaluation requested for query: {request.query}")
            
            # In a real implementation, this would actually call the evaluation service
            # eval_result = self.evaluation_service.evaluate(eval_request)
            
        except Exception as e:
            logger.warning(f"Error evaluating response: {e}")
    
    def _generate_cache_key(self, query: str, context: Dict[str, Any]) -> str:
        """Generate a cache key for a query and context."""
        # Normalize query
        normalized_query = query.lower().strip()
        
        # Extract relevant context for cache key
        relevant_context = {}
        if "user_id" in context:
            relevant_context["user_id"] = context["user_id"]
        if "session_id" in context:
            relevant_context["session_id"] = context["session_id"]
        
        # Generate key
        key_data = f"{normalized_query}|{json.dumps(relevant_context, sort_keys=True)}"
        import hashlib
        cache_key = hashlib.md5(key_data.encode()).hexdigest()
        
        return cache_key
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the serving service."""
        status = "healthy"
        message = "Serving Service is healthy"
        
        try:
            # Check dependent services
            agent_status = self.agent_orchestrator.health_check()
            vector_db_status = self.vector_db_client.health_check()
            
            if agent_status["status"] != "healthy":
                status = "warning"
                message = f"Agent orchestrator issue: {agent_status['message']}"
            elif vector_db_status["status"] != "healthy":
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
                "response_caching_enabled": self.config.response_caching_enabled,
                "compliance_checking_enabled": self.config.compliance_checking_enabled,
                "evaluation_enabled": self.config.evaluation_enabled,
                "cost_optimization_enabled": self.config.cost_optimization_enabled,
                "cache_size": len(self.response_cache) if hasattr(self, "response_cache") else 0
            }
        }

# Initialize global instance
serving_service = None

def get_serving_service():
    """Get or create the serving service instance."""
    global serving_service
    if serving_service is None:
        serving_service = ServingService()
    return serving_service
