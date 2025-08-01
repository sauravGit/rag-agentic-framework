"""
Medical RAG Workflow Configuration for the Enhanced MLOps Framework.

This configuration file defines the settings for a medical customer support RAG workflow.
"""

import os
import yaml
from typing import Dict, Any, List, Optional

class MedicalRAGConfig:
    """Configuration for Medical RAG Workflow."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the configuration.
        
        Args:
            config_path: Path to the YAML configuration file (optional)
        """
        # Default configuration
        self.config = {
            # Core settings
            "project": {
                "name": "medical-rag-support",
                "description": "Medical Customer Support RAG Workflow",
                "version": "1.0.0"
            },
            
            # GCP settings
            "gcp": {
                "project_id": os.environ.get("GCP_PROJECT_ID", "medical-rag-project"),
                "location": os.environ.get("GCP_LOCATION", "us-central1"),
                "service_account": os.environ.get("GCP_SERVICE_ACCOUNT", ""),
                "enable_apis": [
                    "aiplatform.googleapis.com",
                    "documentai.googleapis.com",
                    "storage.googleapis.com",
                    "logging.googleapis.com",
                    "monitoring.googleapis.com"
                ]
            },
            
            # Agent settings
            "agent": {
                "type": "medical_assistant",
                "model": "gemini-pro",
                "temperature": 0.2,
                "max_output_tokens": 1024,
                "top_p": 0.95,
                "top_k": 40,
                "safety_settings": {
                    "harmful_categories": "block_medium_and_above",
                    "harassment": "block_medium_and_above",
                    "hate_speech": "block_medium_and_above",
                    "sexually_explicit": "block_medium_and_above",
                    "dangerous_content": "block_medium_and_above"
                }
            },
            
            # Vector database settings
            "vector_db": {
                "type": "vertex_matching_engine",
                "dimensions": 768,
                "distance_measure": "cosine",
                "index_update_schedule": "hourly",
                "embedding_model": "textembedding-gecko@latest",
                "shard_size": "medium"
            },
            
            # Document processing settings
            "document_processing": {
                "chunk_size": 512,
                "chunk_overlap": 128,
                "processors": [
                    {
                        "type": "text_splitter",
                        "config": {
                            "separator": "\n\n",
                            "keep_separator": False
                        }
                    },
                    {
                        "type": "metadata_extractor",
                        "config": {
                            "extract_title": True,
                            "extract_date": True,
                            "extract_authors": True,
                            "extract_medical_entities": True
                        }
                    },
                    {
                        "type": "medical_entity_extractor",
                        "config": {
                            "entity_types": ["condition", "medication", "procedure", "anatomy"]
                        }
                    }
                ],
                "supported_formats": ["pdf", "docx", "txt", "html", "csv", "xlsx"]
            },
            
            # Compliance settings
            "compliance": {
                "enabled": True,
                "frameworks": ["hipaa", "gdpr"],
                "pii_detection": {
                    "enabled": True,
                    "info_types": [
                        "PERSON_NAME",
                        "US_SOCIAL_SECURITY_NUMBER",
                        "PHONE_NUMBER",
                        "EMAIL_ADDRESS",
                        "MEDICAL_RECORD_NUMBER",
                        "HEALTH_INSURANCE_ID_NUMBER"
                    ]
                },
                "content_safety": {
                    "enabled": True,
                    "block_unsafe_content": True,
                    "log_safety_issues": True
                },
                "audit_logging": {
                    "enabled": True,
                    "log_queries": True,
                    "log_responses": True,
                    "log_pii_detections": True
                }
            },
            
            # Evaluation settings
            "evaluation": {
                "enabled": True,
                "metrics": [
                    "relevance",
                    "factual_accuracy",
                    "medical_correctness",
                    "response_completeness",
                    "response_conciseness",
                    "response_helpfulness"
                ],
                "evaluation_frequency": "daily",
                "sample_size": 100,
                "threshold_alerts": {
                    "relevance": 0.7,
                    "factual_accuracy": 0.9,
                    "medical_correctness": 0.95
                },
                "human_in_the_loop": {
                    "enabled": True,
                    "review_threshold": 0.8,
                    "review_sample_size": 20
                }
            },
            
            # Serving settings
            "serving": {
                "endpoint_type": "vertex_endpoint",
                "min_replicas": 1,
                "max_replicas": 10,
                "autoscaling": {
                    "enabled": True,
                    "target_cpu_utilization": 70,
                    "target_memory_utilization": 80
                },
                "streaming": {
                    "enabled": True,
                    "chunk_size": 20
                },
                "rate_limiting": {
                    "enabled": True,
                    "qps_per_user": 10,
                    "qps_total": 100
                },
                "caching": {
                    "enabled": True,
                    "ttl_seconds": 300
                }
            },
            
            # Monitoring settings
            "monitoring": {
                "enabled": True,
                "metrics": [
                    "latency",
                    "throughput",
                    "error_rate",
                    "token_usage",
                    "query_volume",
                    "cache_hit_rate",
                    "retrieval_precision",
                    "user_feedback_score"
                ],
                "alerting": {
                    "enabled": True,
                    "channels": ["email", "slack"],
                    "thresholds": {
                        "error_rate": 0.05,
                        "p95_latency_ms": 2000,
                        "user_feedback_score": 3.5
                    }
                },
                "logging": {
                    "enabled": True,
                    "log_level": "info",
                    "retention_days": 30
                },
                "dashboards": {
                    "enabled": True,
                    "refresh_interval_seconds": 300
                }
            },
            
            # Cost optimization settings
            "cost_optimization": {
                "enabled": True,
                "token_budget_daily": 1000000,
                "caching_strategy": "aggressive",
                "model_fallback": {
                    "enabled": True,
                    "fallback_models": ["text-bison@latest"]
                },
                "batch_processing": {
                    "enabled": True,
                    "batch_size": 10
                },
                "scheduled_scaling": {
                    "enabled": True,
                    "off_hours": {
                        "start": "22:00",
                        "end": "06:00",
                        "timezone": "America/New_York",
                        "min_replicas": 1
                    }
                }
            }
        }
        
        # Load configuration from file if provided
        if config_path and os.path.exists(config_path):
            self._load_from_file(config_path)
    
    def _load_from_file(self, config_path: str) -> None:
        """Load configuration from a YAML file.
        
        Args:
            config_path: Path to the YAML configuration file
        """
        try:
            with open(config_path, 'r') as f:
                file_config = yaml.safe_load(f)
                
            # Merge with default config
            self._deep_update(self.config, file_config)
        except Exception as e:
            print(f"Error loading configuration from {config_path}: {str(e)}")
    
    def _deep_update(self, d: Dict[str, Any], u: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively update a dictionary.
        
        Args:
            d: Dictionary to update
            u: Dictionary with updates
            
        Returns:
            Updated dictionary
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._deep_update(d[k], v)
            else:
                d[k] = v
        return d
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get a configuration value by its key path.
        
        Args:
            key_path: Dot-separated path to the configuration value
            default: Default value to return if the key is not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> None:
        """Set a configuration value by its key path.
        
        Args:
            key_path: Dot-separated path to the configuration value
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config
        
        for i, key in enumerate(keys[:-1]):
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def save(self, config_path: str) -> None:
        """Save the configuration to a YAML file.
        
        Args:
            config_path: Path to save the configuration file
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Write configuration to file
            with open(config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
                
            print(f"Configuration saved to {config_path}")
        except Exception as e:
            print(f"Error saving configuration to {config_path}: {str(e)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the configuration to a dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return self.config.copy()
    
    def validate(self) -> List[str]:
        """Validate the configuration.
        
        Returns:
            List of validation errors, empty if valid
        """
        errors = []
        
        # Validate required fields
        required_fields = [
            "project.name",
            "gcp.project_id",
            "agent.model"
        ]
        
        for field in required_fields:
            if not self.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate GCP project ID format
        project_id = self.get("gcp.project_id")
        if project_id and not project_id.islower() and not all(c.isalnum() or c == '-' for c in project_id):
            errors.append("GCP project ID must contain only lowercase letters, numbers, and hyphens")
        
        # Validate agent model
        valid_models = ["gemini-pro", "gemini-pro-vision", "text-bison", "chat-bison"]
        agent_model = self.get("agent.model")
        if agent_model and agent_model not in valid_models:
            errors.append(f"Invalid agent model: {agent_model}. Must be one of: {', '.join(valid_models)}")
        
        # Validate temperature range
        temperature = self.get("agent.temperature")
        if temperature is not None and (temperature < 0 or temperature > 1):
            errors.append(f"Invalid temperature: {temperature}. Must be between 0 and 1")
        
        return errors
