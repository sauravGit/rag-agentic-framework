"""
Core module for the Enhanced MLOps Framework for Agentic AI RAG Workflows.

This module contains shared utilities, base classes, and common functionality
used across the framework.
"""

import os
import logging
from typing import Dict, Any, Optional, List, Union
import yaml
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class ConfigBase(BaseModel):
    """Base configuration model with common functionality."""
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> "ConfigBase":
        """Load configuration from a YAML file."""
        try:
            with open(yaml_path, "r") as f:
                config_dict = yaml.safe_load(f)
            return cls(**config_dict)
        except Exception as e:
            logger.error(f"Failed to load configuration from {yaml_path}: {e}")
            raise

    def to_yaml(self, yaml_path: str) -> None:
        """Save configuration to a YAML file."""
        try:
            with open(yaml_path, "w") as f:
                yaml.dump(self.dict(), f)
        except Exception as e:
            logger.error(f"Failed to save configuration to {yaml_path}: {e}")
            raise

class FrameworkException(Exception):
    """Base exception class for the framework."""
    
    def __init__(self, message: str, code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

class ServiceRegistry:
    """Registry for framework services."""
    
    _instance = None
    _services = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceRegistry, cls).__new__(cls)
        return cls._instance
    
    def register(self, name: str, service: Any) -> None:
        """Register a service."""
        self._services[name] = service
        logger.debug(f"Registered service: {name}")
    
    def get(self, name: str) -> Any:
        """Get a registered service."""
        if name not in self._services:
            raise FrameworkException(f"Service not found: {name}", code="SERVICE_NOT_FOUND")
        return self._services[name]
    
    def list(self) -> List[str]:
        """List all registered services."""
        return list(self._services.keys())

class HealthCheck:
    """Health check utility for framework services."""
    
    @staticmethod
    def check_service(service_name: str) -> Dict[str, Any]:
        """Check the health of a service."""
        try:
            registry = ServiceRegistry()
            service = registry.get(service_name)
            if hasattr(service, "health_check") and callable(service.health_check):
                return service.health_check()
            return {"status": "unknown", "message": "Service does not implement health check"}
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def check_all() -> Dict[str, Dict[str, Any]]:
        """Check the health of all registered services."""
        registry = ServiceRegistry()
        results = {}
        for service_name in registry.list():
            results[service_name] = HealthCheck.check_service(service_name)
        return results

class MetricsCollector:
    """Collector for framework metrics."""
    
    def __init__(self):
        self.metrics = {}
    
    def record(self, name: str, value: Union[int, float], labels: Dict[str, str] = None) -> None:
        """Record a metric."""
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append({
            "value": value,
            "labels": labels or {},
            "timestamp": import_time_module().time()
        })
        
    def get(self, name: str) -> List[Dict[str, Any]]:
        """Get recorded metrics for a name."""
        return self.metrics.get(name, [])

def import_time_module():
    """Import time module dynamically to avoid circular imports."""
    import time
    return time

# Initialize global instances
service_registry = ServiceRegistry()
metrics_collector = MetricsCollector()
