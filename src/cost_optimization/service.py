"""
Cost Optimization module for the Enhanced MLOps Framework for Agentic AI RAG Workflows.

This module provides functionality for optimizing costs in RAG workflows,
including model selection, caching, and resource utilization for medical customer support scenarios.
"""

import os
import logging
from typing import Dict, Any, Optional, List, Union
import time
import json
import hashlib
from pydantic import BaseModel, Field

from ..core import FrameworkException, ServiceRegistry, MetricsCollector
from ..core.config import CostOptimizationConfig, ConfigManager

logger = logging.getLogger(__name__)

class CostOptimizationRequest(BaseModel):
    """Model for a cost optimization request."""
    
    query: str = Field(..., description="User query to optimize")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context for the query")
    optimization_types: List[str] = Field(default_factory=list, description="Types of optimizations to perform")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for optimization")

class CostOptimizationResult(BaseModel):
    """Model for a cost optimization result."""
    
    optimized_query: Optional[str] = Field(None, description="Optimized query if modified")
    optimized_context: Dict[str, Any] = Field(default_factory=dict, description="Optimized context")
    cache_hit: bool = Field(False, description="Whether a cache hit occurred")
    cached_response: Optional[Dict[str, Any]] = Field(None, description="Cached response if available")
    recommended_models: Dict[str, str] = Field(default_factory=dict, description="Recommended models for different stages")
    estimated_cost: float = Field(..., description="Estimated cost in USD")
    estimated_savings: float = Field(..., description="Estimated cost savings in USD")
    processing_time: float = Field(..., description="Time taken to process the optimization in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata about the optimization")

class CostOptimizationService:
    """Service for optimizing costs in RAG workflows."""
    
    def __init__(self, config: CostOptimizationConfig = None):
        """Initialize the cost optimization service with configuration."""
        if config is None:
            config_manager = ConfigManager()
            app_config = config_manager.get_config()
            config = app_config.cost_optimization
        
        self.config = config
        self.metrics = MetricsCollector()
        
        # Initialize cache if enabled
        self.cache = {}
        
        # Register with service registry
        service_registry = ServiceRegistry()
        service_registry.register("cost_optimization_service", self)
        
        logger.info("Cost Optimization Service initialized")
    
    def optimize(self, request: CostOptimizationRequest) -> CostOptimizationResult:
        """Optimize costs for a RAG workflow."""
        start_time = time.time()
        
        try:
            optimized_query = request.query
            optimized_context = request.context.copy()
            cache_hit = False
            cached_response = None
            recommended_models = {}
            estimated_cost = 0.0
            estimated_savings = 0.0
            
            # Determine which optimizations to perform
            opt_types = request.optimization_types
            if not opt_types:
                # Use default optimizations based on configuration
                if self.config.query_optimization_enabled:
                    opt_types.append("query_optimization")
                if self.config.caching_enabled:
                    opt_types.append("caching")
                if self.config.model_selection_enabled:
                    opt_types.append("model_selection")
                if self.config.resource_optimization_enabled:
                    opt_types.append("resource_optimization")
            
            # Perform requested optimizations
            for opt_type in opt_types:
                if opt_type == "query_optimization":
                    query_result = self._optimize_query(request.query, request.context)
                    optimized_query = query_result["optimized_query"]
                    estimated_savings += query_result["estimated_savings"]
                
                elif opt_type == "caching":
                    cache_result = self._check_cache(request.query, request.context)
                    cache_hit = cache_result["cache_hit"]
                    cached_response = cache_result["cached_response"]
                    estimated_savings += cache_result["estimated_savings"]
                
                elif opt_type == "model_selection":
                    model_result = self._select_optimal_models(request.query, request.context)
                    recommended_models = model_result["recommended_models"]
                    optimized_context.update({"recommended_models": recommended_models})
                    estimated_savings += model_result["estimated_savings"]
                
                elif opt_type == "resource_optimization":
                    resource_result = self._optimize_resources(request.query, request.context)
                    optimized_context.update(resource_result["optimized_context"])
                    estimated_savings += resource_result["estimated_savings"]
            
            # Calculate estimated cost
            estimated_cost = self._calculate_estimated_cost(request.query, request.context, recommended_models)
            
            # Record metrics
            processing_time = time.time() - start_time
            self.metrics.record(
                "cost_optimization_duration",
                processing_time,
                {"opt_types": ",".join(opt_types)}
            )
            
            # Create and return result
            result = CostOptimizationResult(
                optimized_query=optimized_query if optimized_query != request.query else None,
                optimized_context=optimized_context,
                cache_hit=cache_hit,
                cached_response=cached_response,
                recommended_models=recommended_models,
                estimated_cost=estimated_cost,
                estimated_savings=estimated_savings,
                processing_time=processing_time,
                metadata={
                    "opt_types": opt_types,
                    "original_query_length": len(request.query)
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error optimizing costs: {e}")
            
            # Record error metric
            self.metrics.record(
                "cost_optimization_error",
                1,
                {"error_type": type(e).__name__}
            )
            
            raise FrameworkException(
                f"Failed to optimize costs: {str(e)}",
                code="COST_OPTIMIZATION_ERROR"
            )
    
    def _optimize_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize a query to reduce costs."""
        # This is a simplified implementation
        # In a real system, this would use more sophisticated query optimization
        
        optimized_query = query
        estimated_savings = 0.0
        
        # Check for query length and complexity
        query_words = query.split()
        
        # Simplify very long queries
        if len(query_words) > 50:
            # Extract key terms (simplified implementation)
            key_terms = query_words[:20]  # Just take first 20 words as a simplification
            optimized_query = " ".join(key_terms)
            
            # Estimate savings from reduced token count
            token_reduction = (len(query_words) - len(key_terms)) * 1.3  # Approximate tokens per word
            estimated_savings = token_reduction * 0.00002  # Approximate cost per token
        
        # Check for medical specificity
        medical_context = context.get("domain") == "medical" or "medical" in query.lower()
        if medical_context and self.config.domain_specific_optimization:
            # Add medical context hint if not already present
            if "medical" not in query.lower():
                optimized_query = f"In a medical context: {optimized_query}"
                
                # No direct cost savings, but improves relevance
                estimated_savings += 0.001  # Nominal savings from improved relevance
        
        logger.debug(f"Query optimization: original='{query}', optimized='{optimized_query}'")
        return {
            "optimized_query": optimized_query,
            "estimated_savings": estimated_savings
        }
    
    def _check_cache(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if a query result is available in cache."""
        # This is a simplified implementation
        # In a real system, this would use a more sophisticated caching strategy
        
        if not self.config.caching_enabled:
            return {
                "cache_hit": False,
                "cached_response": None,
                "estimated_savings": 0.0
            }
        
        # Generate cache key
        cache_key = self._generate_cache_key(query, context)
        
        # Check cache
        cache_hit = cache_key in self.cache
        cached_response = self.cache.get(cache_key)
        
        # Estimate savings from cache hit
        estimated_savings = 0.0
        if cache_hit:
            # Estimate based on typical API costs
            query_tokens = len(query.split()) * 1.3  # Approximate tokens per word
            response_tokens = 150  # Assume average response length
            
            # Approximate cost for embedding + LLM call
            embedding_cost = query_tokens * 0.0001
            llm_cost = (query_tokens + response_tokens) * 0.002
            
            estimated_savings = embedding_cost + llm_cost
            
            # Record cache hit metric
            self.metrics.record("cache_hit", 1, {})
        
        logger.debug(f"Cache check: hit={cache_hit}, key={cache_key}")
        return {
            "cache_hit": cache_hit,
            "cached_response": cached_response,
            "estimated_savings": estimated_savings
        }
    
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
        cache_key = hashlib.md5(key_data.encode()).hexdigest()
        
        return cache_key
    
    def update_cache(self, query: str, context: Dict[str, Any], response: Dict[str, Any]) -> None:
        """Update the cache with a query result."""
        if not self.config.caching_enabled:
            return
        
        # Generate cache key
        cache_key = self._generate_cache_key(query, context)
        
        # Update cache
        self.cache[cache_key] = response
        
        # Trim cache if it exceeds max size
        if len(self.cache) > self.config.max_cache_size:
            # Simple LRU implementation: just remove oldest entries
            # In a real system, this would use a proper LRU cache
            keys_to_remove = list(self.cache.keys())[:-self.config.max_cache_size]
            for key in keys_to_remove:
                del self.cache[key]
        
        logger.debug(f"Cache updated: key={cache_key}")
    
    def _select_optimal_models(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Select optimal models for different stages of the RAG workflow."""
        # This is a simplified implementation
        # In a real system, this would use more sophisticated model selection
        
        recommended_models = {}
        estimated_savings = 0.0
        
        # Determine query complexity and length
        query_length = len(query.split())
        query_complexity = "low"
        
        if query_length > 20:
            query_complexity = "medium"
        if query_length > 50:
            query_complexity = "high"
        
        # Check for medical terminology
        medical_terms = [
            "diagnosis", "symptom", "treatment", "medication", "disease",
            "condition", "prescription", "dosage", "side effect"
        ]
        has_medical_terms = any(term in query.lower() for term in medical_terms)
        
        # Select embedding model
        if query_complexity == "low" and not has_medical_terms:
            recommended_models["embedding"] = "text-embedding-3-small"
            estimated_savings += 0.0005  # Savings compared to larger model
        else:
            recommended_models["embedding"] = "text-embedding-3-large"
        
        # Select retrieval model
        recommended_models["retrieval"] = "bm25"  # Simple keyword-based retrieval is often sufficient
        
        # Select generation model based on complexity
        if query_complexity == "low" and not has_medical_terms:
            recommended_models["generation"] = "gemini-1.0-pro"
            estimated_savings += 0.01  # Savings compared to larger model
        elif query_complexity == "medium" or has_medical_terms:
            recommended_models["generation"] = "gemini-1.5-pro"
            estimated_savings += 0.005  # Some savings compared to largest model
        else:
            recommended_models["generation"] = "gemini-1.5-ultra"
        
        logger.debug(f"Model selection: {recommended_models}")
        return {
            "recommended_models": recommended_models,
            "estimated_savings": estimated_savings
        }
    
    def _optimize_resources(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize resource utilization for a query."""
        # This is a simplified implementation
        # In a real system, this would use more sophisticated resource optimization
        
        optimized_context = {}
        estimated_savings = 0.0
        
        # Optimize chunk retrieval count
        if "top_k" not in context:
            # Default to a reasonable value based on query complexity
            query_length = len(query.split())
            if query_length < 10:
                optimized_context["top_k"] = 3
                estimated_savings += 0.002  # Savings from retrieving fewer chunks
            elif query_length < 30:
                optimized_context["top_k"] = 5
                estimated_savings += 0.001  # Some savings
            else:
                optimized_context["top_k"] = 8
        
        # Optimize generation parameters
        if "max_tokens" not in context:
            # Set reasonable max tokens based on expected response length
            optimized_context["max_tokens"] = 300  # Default for medical responses
            estimated_savings += 0.003  # Savings from limiting token generation
        
        # Optimize temperature
        if "temperature" not in context:
            # For medical domain, lower temperature is better for factual responses
            optimized_context["temperature"] = 0.2
            estimated_savings += 0.001  # Nominal savings from more efficient generation
        
        logger.debug(f"Resource optimization: {optimized_context}")
        return {
            "optimized_context": optimized_context,
            "estimated_savings": estimated_savings
        }
    
    def _calculate_estimated_cost(self, query: str, context: Dict[str, Any], recommended_models: Dict[str, str]) -> float:
        """Calculate the estimated cost for processing a query."""
        # This is a simplified implementation
        # In a real system, this would use more accurate cost models
        
        # Estimate token counts
        query_tokens = len(query.split()) * 1.3  # Approximate tokens per word
        context_tokens = sum(len(str(v).split()) for v in context.values()) * 1.3
        response_tokens = context.get("max_tokens", 300)  # Use context value or default
        
        # Get model costs
        embedding_model = recommended_models.get("embedding", "text-embedding-3-large")
        generation_model = recommended_models.get("generation", "gemini-1.5-pro")
        
        # Embedding cost
        if embedding_model == "text-embedding-3-small":
            embedding_cost = query_tokens * 0.00001
        else:  # text-embedding-3-large
            embedding_cost = query_tokens * 0.00002
        
        # Retrieval cost (minimal for vector search)
        retrieval_cost = 0.0001
        
        # Generation cost
        input_tokens = query_tokens + context_tokens
        if generation_model == "gemini-1.0-pro":
            generation_cost = (input_tokens * 0.00001) + (response_tokens * 0.00002)
        elif generation_model == "gemini-1.5-pro":
            generation_cost = (input_tokens * 0.00002) + (response_tokens * 0.00004)
        else:  # gemini-1.5-ultra
            generation_cost = (input_tokens * 0.00003) + (response_tokens * 0.00006)
        
        # Total cost
        total_cost = embedding_cost + retrieval_cost + generation_cost
        
        logger.debug(f"Estimated cost: ${total_cost:.6f}")
        return total_cost
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the cost optimization service."""
        status = "healthy"
        message = "Cost Optimization Service is healthy"
        
        try:
            # Perform a simple optimization
            request = CostOptimizationRequest(
                query="What are the symptoms of a cold?",
                context={}
            )
            self.optimize(request)
        except Exception as e:
            status = "unhealthy"
            message = f"Health check failed: {str(e)}"
        
        return {
            "status": status,
            "message": message,
            "timestamp": time.time(),
            "details": {
                "caching_enabled": self.config.caching_enabled,
                "query_optimization_enabled": self.config.query_optimization_enabled,
                "model_selection_enabled": self.config.model_selection_enabled,
                "cache_size": len(self.cache) if hasattr(self, "cache") else 0
            }
        }

# Initialize global instance
cost_optimization_service = None

def get_cost_optimization_service():
    """Get or create the cost optimization service instance."""
    global cost_optimization_service
    if cost_optimization_service is None:
        cost_optimization_service = CostOptimizationService()
    return cost_optimization_service
