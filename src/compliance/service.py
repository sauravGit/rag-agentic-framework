"""
Compliance module for the Enhanced MLOps Framework for Agentic AI RAG Workflows.

This module provides compliance functionality for medical customer support scenarios,
including HIPAA compliance, PII detection, and audit logging.
"""

import os
import logging
from typing import Dict, Any, Optional, List, Union
import time
import json
import re
from pydantic import BaseModel, Field

from ..core import FrameworkException, ServiceRegistry, MetricsCollector
from ..core.config import ComplianceConfig, ConfigManager

logger = logging.getLogger(__name__)

class ComplianceCheck(BaseModel):
    """Model for a compliance check request."""
    
    content: str = Field(..., description="Content to check for compliance")
    content_type: str = Field("text", description="Type of content (text, document, response)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata for the content")
    check_types: List[str] = Field(default_factory=list, description="Types of compliance checks to perform")

class ComplianceResult(BaseModel):
    """Model for a compliance check result."""
    
    compliant: bool = Field(..., description="Whether the content is compliant")
    issues: List[Dict[str, Any]] = Field(default_factory=list, description="Compliance issues found")
    modified_content: Optional[str] = Field(None, description="Modified content if PII was masked or removed")
    processing_time: float = Field(..., description="Time taken to process the compliance check in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata about the compliance check")

class ComplianceService:
    """Service for handling compliance requirements in RAG workflows."""
    
    def __init__(self, config: ComplianceConfig = None):
        """Initialize the compliance service with configuration."""
        if config is None:
            config_manager = ConfigManager()
            app_config = config_manager.get_config()
            config = app_config.compliance
        
        self.config = config
        self.metrics = MetricsCollector()
        
        # Register with service registry
        service_registry = ServiceRegistry()
        service_registry.register("compliance_service", self)
        
        logger.info("Compliance Service initialized")
    
    def check_compliance(self, check: ComplianceCheck) -> ComplianceResult:
        """Check content for compliance issues."""
        start_time = time.time()
        
        try:
            issues = []
            modified_content = check.content
            
            # Determine which checks to perform
            check_types = check.check_types
            if not check_types:
                # Use default checks based on configuration
                if self.config.hipaa_enabled:
                    check_types.append("hipaa")
                if self.config.pii_detection_enabled:
                    check_types.append("pii")
            
            # Perform requested checks
            for check_type in check_types:
                if check_type == "hipaa":
                    hipaa_issues = self._check_hipaa_compliance(check.content, check.metadata)
                    issues.extend(hipaa_issues)
                
                elif check_type == "pii":
                    pii_result = self._check_pii(check.content, check.metadata)
                    issues.extend(pii_result["issues"])
                    if pii_result["modified_content"]:
                        modified_content = pii_result["modified_content"]
            
            # Log compliance check if audit logging is enabled
            if self.config.audit_logging_enabled:
                self._log_compliance_check(check, issues)
            
            # Determine overall compliance
            compliant = len(issues) == 0
            
            # Record metrics
            processing_time = time.time() - start_time
            self.metrics.record(
                "compliance_check_duration",
                processing_time,
                {"content_type": check.content_type, "compliant": compliant}
            )
            
            # Create and return result
            result = ComplianceResult(
                compliant=compliant,
                issues=issues,
                modified_content=modified_content if modified_content != check.content else None,
                processing_time=processing_time,
                metadata={
                    "check_types": check_types,
                    "content_type": check.content_type,
                    "issue_count": len(issues)
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking compliance: {e}")
            
            # Record error metric
            self.metrics.record(
                "compliance_check_error",
                1,
                {"error_type": type(e).__name__}
            )
            
            raise FrameworkException(
                f"Failed to check compliance: {str(e)}",
                code="COMPLIANCE_CHECK_ERROR"
            )
    
    def _check_hipaa_compliance(self, content: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check content for HIPAA compliance issues."""
        # This is a simplified implementation
        # In a real system, this would use more sophisticated HIPAA compliance checking
        
        issues = []
        
        # Check for PHI (Protected Health Information)
        phi_patterns = {
            "patient_name": r"\b(?:patient|name):\s*([A-Z][a-z]+ [A-Z][a-z]+)\b",
            "ssn": r"\b(?:\d{3}-\d{2}-\d{4})\b",
            "medical_record_number": r"\b(?:medical record|mrn):\s*(\d{6,10})\b",
            "dob": r"\b(?:dob|date of birth):\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b",
            "address": r"\b(\d+ [A-Za-z]+ (?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd))\b"
        }
        
        for phi_type, pattern in phi_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                issue = {
                    "type": "hipaa_phi",
                    "subtype": phi_type,
                    "text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "severity": "high"
                }
                issues.append(issue)
        
        # Check for specific medical conditions that require extra privacy
        sensitive_conditions = [
            "HIV", "AIDS", "substance abuse", "mental health", "psychiatric", 
            "alcohol abuse", "drug abuse", "STD", "sexually transmitted"
        ]
        
        for condition in sensitive_conditions:
            pattern = r"\b" + re.escape(condition) + r"\b"
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                issue = {
                    "type": "hipaa_sensitive_condition",
                    "subtype": "condition",
                    "text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "severity": "medium"
                }
                issues.append(issue)
        
        logger.debug(f"Found {len(issues)} HIPAA compliance issues")
        return issues
    
    def _check_pii(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Check content for PII (Personally Identifiable Information)."""
        # This is a simplified implementation
        # In a real system, this would use more sophisticated PII detection
        
        issues = []
        modified_content = content
        
        # Check for common PII patterns
        pii_patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b(?:\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b",
            "credit_card": r"\b(?:\d{4}[- ]?){3}\d{4}\b",
            "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        }
        
        for pii_type, pattern in pii_patterns.items():
            matches = list(re.finditer(pattern, content))
            
            # Process matches in reverse order to avoid messing up indices when replacing
            for match in reversed(matches):
                issue = {
                    "type": "pii",
                    "subtype": pii_type,
                    "text": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "severity": "medium"
                }
                issues.append(issue)
                
                # Apply PII action based on configuration
                if self.config.pii_action == "mask":
                    # Replace with asterisks
                    replacement = "*" * len(match.group(0))
                    modified_content = modified_content[:match.start()] + replacement + modified_content[match.end():]
                elif self.config.pii_action == "remove":
                    # Remove the PII
                    modified_content = modified_content[:match.start()] + modified_content[match.end():]
        
        logger.debug(f"Found {len(issues)} PII issues")
        return {
            "issues": issues,
            "modified_content": modified_content
        }
    
    def _log_compliance_check(self, check: ComplianceCheck, issues: List[Dict[str, Any]]) -> None:
        """Log a compliance check for audit purposes."""
        # This is a simplified implementation
        # In a real system, this would log to a secure audit log
        
        audit_entry = {
            "timestamp": time.time(),
            "content_type": check.content_type,
            "content_length": len(check.content),
            "check_types": check.check_types,
            "issue_count": len(issues),
            "issue_types": [issue["type"] for issue in issues],
            "metadata": check.metadata
        }
        
        logger.info(f"Compliance audit log: {json.dumps(audit_entry)}")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the compliance service."""
        status = "healthy"
        message = "Compliance Service is healthy"
        
        try:
            # Perform a simple compliance check
            check = ComplianceCheck(
                content="This is a test.",
                content_type="text",
                check_types=["hipaa", "pii"]
            )
            self.check_compliance(check)
        except Exception as e:
            status = "unhealthy"
            message = f"Health check failed: {str(e)}"
        
        return {
            "status": status,
            "message": message,
            "timestamp": time.time(),
            "details": {
                "hipaa_enabled": self.config.hipaa_enabled,
                "pii_detection_enabled": self.config.pii_detection_enabled,
                "audit_logging_enabled": self.config.audit_logging_enabled
            }
        }

# Initialize global instance
compliance_service = None

def get_compliance_service():
    """Get or create the compliance service instance."""
    global compliance_service
    if compliance_service is None:
        compliance_service = ComplianceService()
    return compliance_service
