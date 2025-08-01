"""
Configuration module for the Enhanced MLOps Framework for Agentic AI RAG Workflows.

This module provides configuration management functionality, including loading,
validation, and distribution of configuration settings.
"""

import os
import yaml
import json
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, validator
import logging

from ..core import ConfigBase, FrameworkException

logger = logging.getLogger(__name__)

class VectorDBConfig(ConfigBase):
    """Configuration for the Vector Database component."""
    
    provider: str = Field(..., description="Vector database provider (e.g., 'elasticsearch', 'pinecone', 'vertex_matching_engine')")
    connection_string: str = Field(..., description="Connection string for the vector database")
    index_name: str = Field(..., description="Name of the vector index")
    embedding_dimension: int = Field(768, description="Dimension of the embedding vectors")
    similarity_metric: str = Field("cosine", description="Similarity metric to use (cosine, dot_product, euclidean)")
    batch_size: int = Field(100, description="Batch size for vector operations")
    
    @validator('similarity_metric')
    def validate_similarity_metric(cls, v):
        allowed_metrics = ["cosine", "dot_product", "euclidean"]
        if v not in allowed_metrics:
            raise ValueError(f"Similarity metric must be one of {allowed_metrics}")
        return v

class AgentConfig(ConfigBase):
    """Configuration for the Agent Orchestration component."""
    
    adk_enabled: bool = Field(True, description="Whether to use Google's Agent Development Kit")
    agentspace_enabled: bool = Field(True, description="Whether to use Google Agentspace")
    agentspace_project_id: Optional[str] = Field(None, description="Google Cloud project ID for Agentspace")
    model_name: str = Field("gemini-pro", description="Name of the LLM model to use")
    max_tokens: int = Field(8192, description="Maximum number of tokens for context window")
    temperature: float = Field(0.2, description="Temperature for LLM generation")
    tools_enabled: List[str] = Field(["search", "calculator", "medical_database"], description="List of enabled tools")
    memory_type: str = Field("conversation_buffer", description="Type of memory to use")
    memory_window: int = Field(10, description="Number of conversation turns to keep in memory")
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        return v

class DocumentProcessingConfig(ConfigBase):
    """Configuration for the Document Processing component."""
    
    chunking_strategy: str = Field("recursive", description="Strategy for chunking documents")
    chunk_size: int = Field(1000, description="Size of document chunks in characters")
    chunk_overlap: int = Field(200, description="Overlap between chunks in characters")
    embedding_model: str = Field("text-embedding-ada-002", description="Model to use for generating embeddings")
    supported_file_types: List[str] = Field(["pdf", "docx", "txt", "html"], description="Supported file types")
    extract_metadata: bool = Field(True, description="Whether to extract metadata from documents")
    medical_entity_extraction: bool = Field(True, description="Whether to extract medical entities")
    
    @validator('chunking_strategy')
    def validate_chunking_strategy(cls, v):
        allowed_strategies = ["recursive", "fixed", "semantic", "medical_section"]
        if v not in allowed_strategies:
            raise ValueError(f"Chunking strategy must be one of {allowed_strategies}")
        return v

class ComplianceConfig(ConfigBase):
    """Configuration for the Compliance component."""
    
    hipaa_enabled: bool = Field(True, description="Whether HIPAA compliance is enabled")
    pii_detection_enabled: bool = Field(True, description="Whether PII detection is enabled")
    pii_action: str = Field("mask", description="Action to take on detected PII (mask, remove, log)")
    audit_logging_enabled: bool = Field(True, description="Whether audit logging is enabled")
    data_residency: str = Field("us", description="Data residency requirement")
    retention_period_days: int = Field(90, description="Data retention period in days")
    
    @validator('pii_action')
    def validate_pii_action(cls, v):
        allowed_actions = ["mask", "remove", "log"]
        if v not in allowed_actions:
            raise ValueError(f"PII action must be one of {allowed_actions}")
        return v

class EvaluationConfig(ConfigBase):
    """Configuration for the Evaluation component."""
    
    metrics: List[str] = Field(["retrieval_precision", "answer_relevance", "factual_accuracy", "citation_accuracy"], 
                              description="Metrics to evaluate")
    evaluation_frequency: str = Field("continuous", description="Frequency of evaluation (batch, continuous)")
    reference_dataset_path: Optional[str] = Field(None, description="Path to reference dataset for evaluation")
    human_feedback_enabled: bool = Field(True, description="Whether to collect human feedback")
    confidence_threshold: float = Field(0.7, description="Confidence threshold for answers")
    
    @validator('evaluation_frequency')
    def validate_evaluation_frequency(cls, v):
        allowed_frequencies = ["batch", "continuous", "scheduled"]
        if v not in allowed_frequencies:
            raise ValueError(f"Evaluation frequency must be one of {allowed_frequencies}")
        return v

class CostOptimizationConfig(ConfigBase):
    """Configuration for the Cost Optimization component."""
    
    caching_enabled: bool = Field(True, description="Whether response caching is enabled")
    cache_ttl_seconds: int = Field(3600, description="Time-to-live for cached responses in seconds")
    token_budget_daily: Optional[int] = Field(None, description="Daily token budget")
    model_fallback_enabled: bool = Field(True, description="Whether to fall back to smaller models when appropriate")
    batch_processing_enabled: bool = Field(True, description="Whether to use batch processing when possible")

class ServingConfig(ConfigBase):
    """Configuration for the Serving component."""
    
    api_rate_limit: int = Field(100, description="Rate limit for API requests per minute")
    max_concurrent_requests: int = Field(20, description="Maximum number of concurrent requests")
    timeout_seconds: int = Field(30, description="Request timeout in seconds")
    streaming_enabled: bool = Field(True, description="Whether streaming responses are enabled")
    cors_origins: List[str] = Field(["*"], description="Allowed CORS origins")
    health_check_path: str = Field("/health", description="Path for health check endpoint")

class MonitoringConfig(ConfigBase):
    """Configuration for the Monitoring component."""
    
    metrics_enabled: bool = Field(True, description="Whether metrics collection is enabled")
    logging_level: str = Field("INFO", description="Logging level")
    tracing_enabled: bool = Field(True, description="Whether distributed tracing is enabled")
    alert_channels: List[str] = Field(["email"], description="Alert notification channels")
    dashboard_refresh_seconds: int = Field(60, description="Dashboard refresh interval in seconds")
    
    @validator('logging_level')
    def validate_logging_level(cls, v):
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v not in allowed_levels:
            raise ValueError(f"Logging level must be one of {allowed_levels}")
        return v

class AppConfig(ConfigBase):
    """Main application configuration."""
    
    app_name: str = Field("medical-support-rag", description="Name of the application")
    environment: str = Field("development", description="Deployment environment")
    vector_db: VectorDBConfig = Field(..., description="Vector database configuration")
    agent: AgentConfig = Field(..., description="Agent configuration")
    document_processing: DocumentProcessingConfig = Field(..., description="Document processing configuration")
    compliance: ComplianceConfig = Field(..., description="Compliance configuration")
    evaluation: EvaluationConfig = Field(..., description="Evaluation configuration")
    cost_optimization: CostOptimizationConfig = Field(..., description="Cost optimization configuration")
    serving: ServingConfig = Field(..., description="Serving configuration")
    monitoring: MonitoringConfig = Field(..., description="Monitoring configuration")
    
    @validator('environment')
    def validate_environment(cls, v):
        allowed_environments = ["development", "testing", "staging", "production"]
        if v not in allowed_environments:
            raise ValueError(f"Environment must be one of {allowed_environments}")
        return v

class ConfigManager:
    """Manager for application configuration."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._config = None
        return cls._instance
    
    def load_config(self, config_path: str = None) -> AppConfig:
        """Load configuration from file or environment."""
        if config_path and os.path.exists(config_path):
            try:
                self._config = AppConfig.from_yaml(config_path)
                logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.error(f"Failed to load configuration from {config_path}: {e}")
                raise FrameworkException(f"Failed to load configuration: {e}", code="CONFIG_LOAD_ERROR")
        else:
            # Load from environment variables or use defaults
            try:
                config_dict = self._load_from_env()
                self._config = AppConfig(**config_dict)
                logger.info("Loaded configuration from environment variables")
            except Exception as e:
                logger.error(f"Failed to load configuration from environment: {e}")
                raise FrameworkException(f"Failed to load configuration: {e}", code="CONFIG_LOAD_ERROR")
        
        return self._config
    
    def _load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        # This is a simplified implementation
        # In a real system, this would parse environment variables with proper prefixes
        config_dict = {
            "app_name": os.environ.get("APP_NAME", "medical-support-rag"),
            "environment": os.environ.get("ENVIRONMENT", "development"),
            # Add other configuration sections as needed
        }
        
        # Try to load from CONFIG_JSON environment variable
        config_json = os.environ.get("CONFIG_JSON")
        if config_json:
            try:
                config_dict.update(json.loads(config_json))
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse CONFIG_JSON: {e}")
        
        return config_dict
    
    def get_config(self) -> AppConfig:
        """Get the current configuration."""
        if self._config is None:
            self.load_config()
        return self._config
    
    def update_config(self, updates: Dict[str, Any]) -> AppConfig:
        """Update the current configuration."""
        if self._config is None:
            self.load_config()
        
        # Create a dictionary from the current config
        config_dict = self._config.dict()
        
        # Apply updates (this is a simplified implementation)
        for key, value in updates.items():
            if "." in key:
                # Handle nested keys like "vector_db.index_name"
                parts = key.split(".")
                current = config_dict
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            else:
                config_dict[key] = value
        
        # Create a new config instance with the updates
        self._config = AppConfig(**config_dict)
        return self._config
    
    def save_config(self, config_path: str) -> None:
        """Save the current configuration to a file."""
        if self._config is None:
            raise FrameworkException("No configuration to save", code="CONFIG_SAVE_ERROR")
        
        try:
            self._config.to_yaml(config_path)
            logger.info(f"Saved configuration to {config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration to {config_path}: {e}")
            raise FrameworkException(f"Failed to save configuration: {e}", code="CONFIG_SAVE_ERROR")

# Initialize global instance
config_manager = ConfigManager()
