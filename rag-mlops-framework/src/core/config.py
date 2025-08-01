"""
Base configuration and utilities for the core framework.
"""
from typing import Dict, Any, Optional, List
import os
import json
from pydantic import BaseModel, Field


class FrameworkConfig(BaseModel):
    """Base configuration for the framework."""
    project_id: str = Field(..., description="GCP Project ID")
    region: str = Field("us-central1", description="GCP Region")
    environment: str = Field("development", description="Deployment environment")
    logging_level: str = Field("INFO", description="Logging level")
    
    @classmethod
    def from_file(cls, file_path: str) -> "FrameworkConfig":
        """Load configuration from a file."""
        with open(file_path, "r") as f:
            config_data = json.load(f)
        return cls(**config_data)
    
    @classmethod
    def from_env(cls) -> "FrameworkConfig":
        """Load configuration from environment variables."""
        return cls(
            project_id=os.environ.get("GCP_PROJECT_ID", "demo-project"),
            region=os.environ.get("GCP_REGION", "us-central1"),
            environment=os.environ.get("ENVIRONMENT", "development"),
            logging_level=os.environ.get("LOGGING_LEVEL", "INFO"),
        )


class ServiceConfig(BaseModel):
    """Base configuration for services."""
    service_name: str
    host: str
    port: int
    api_version: str = "v1"
    
    @property
    def base_url(self) -> str:
        """Get the base URL for the service."""
        return f"http://{self.host}:{self.port}/api/{self.api_version}"
