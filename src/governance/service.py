"""
Governance module for the Enhanced MLOps Framework for Agentic AI RAG Workflows.

This module provides functionality for governance of the framework,
including audit logging, access control, and policy enforcement for medical customer support scenarios.
"""

import os
import logging
import time
from typing import Dict, Any, Optional, List, Union
import json
import datetime
import uuid
from pydantic import BaseModel, Field
import threading
import queue

from ..core import FrameworkException, ServiceRegistry
from ..core.config import GovernanceConfig, ConfigManager

logger = logging.getLogger(__name__)

class AuditLogEntry(BaseModel):
    """Model for an audit log entry."""
    
    id: str = Field(..., description="Unique identifier for the log entry")
    timestamp: float = Field(..., description="Timestamp when the event occurred")
    event_type: str = Field(..., description="Type of event")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: Optional[str] = Field(None, description="Identifier of resource affected")
    action: str = Field(..., description="Action performed")
    status: str = Field(..., description="Status of the action")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details about the event")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the event")

class AccessPolicy(BaseModel):
    """Model for an access policy."""
    
    id: str = Field(..., description="Unique identifier for the policy")
    name: str = Field(..., description="Policy name")
    description: str = Field("", description="Policy description")
    resource_type: str = Field(..., description="Type of resource")
    actions: List[str] = Field(..., description="Allowed actions")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Conditions for policy application")
    priority: int = Field(0, description="Policy priority (higher values take precedence)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the policy")

class AccessRequest(BaseModel):
    """Model for an access request."""
    
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    resource_type: str = Field(..., description="Type of resource")
    resource_id: Optional[str] = Field(None, description="Identifier of resource")
    action: str = Field(..., description="Action to perform")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context for the request")

class AccessResponse(BaseModel):
    """Model for an access response."""
    
    allowed: bool = Field(..., description="Whether access is allowed")
    policy_id: Optional[str] = Field(None, description="Identifier of the policy that determined the decision")
    reason: str = Field("", description="Reason for the decision")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the response")

class GovernanceService:
    """Service for governance of the framework."""
    
    def __init__(self, config: GovernanceConfig = None):
        """Initialize the governance service with configuration."""
        if config is None:
            config_manager = ConfigManager()
            app_config = config_manager.get_config()
            config = app_config.governance
        
        self.config = config
        
        # Initialize audit log storage
        self.audit_logs = []
        self.audit_logs_lock = threading.Lock()
        
        # Initialize access policies
        self.access_policies = []
        self.access_policies_lock = threading.Lock()
        
        # Initialize background processing
        self.processing_queue = queue.Queue()
        self.processing_thread = None
        self.running = False
        
        # Load access policies
        self._load_access_policies()
        
        # Start background processing if enabled
        if self.config.background_processing_enabled:
            self._start_background_processing()
        
        # Register with service registry
        service_registry = ServiceRegistry()
        service_registry.register("governance_service", self)
        
        logger.info("Governance Service initialized")
    
    def log_audit_event(self, event_type: str, resource_type: str, action: str, status: str,
                        user_id: str = None, session_id: str = None, resource_id: str = None,
                        details: Dict[str, Any] = None, metadata: Dict[str, Any] = None) -> str:
        """Log an audit event."""
        if details is None:
            details = {}
        if metadata is None:
            metadata = {}
        
        # Create audit log entry
        entry = AuditLogEntry(
            id=str(uuid.uuid4()),
            timestamp=time.time(),
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            status=status,
            details=details,
            metadata=metadata
        )
        
        # Add to processing queue if background processing is enabled
        if self.config.background_processing_enabled:
            self.processing_queue.put(("log_audit", entry))
            return entry.id
        
        # Otherwise, process immediately
        self._process_audit_log(entry)
        return entry.id
    
    def _process_audit_log(self, entry: AuditLogEntry) -> None:
        """Process an audit log entry."""
        with self.audit_logs_lock:
            # Add entry to audit logs
            self.audit_logs.append(entry.dict())
            
            # Trim audit logs if they exceed max size
            if len(self.audit_logs) > self.config.max_audit_log_entries:
                self.audit_logs = self.audit_logs[-self.config.max_audit_log_entries:]
        
        # Log entry
        logger.info(f"Audit log: {entry.event_type} - {entry.resource_type} - {entry.action} - {entry.status}")
        
        # Export to external system if configured
        if self.config.audit_log_export_enabled:
            self._export_audit_log(entry)
    
    def _export_audit_log(self, entry: AuditLogEntry) -> None:
        """Export an audit log entry to an external system."""
        # This is a simplified implementation
        # In a real system, this would export to a database, log aggregation service, etc.
        
        # For now, just log that export would occur
        logger.debug(f"Would export audit log: {entry.id}")
        
        # In a real implementation, this would use an export service
        # For example, to export to BigQuery for medical audit compliance
    
    def get_audit_logs(self, event_type: str = None, resource_type: str = None,
                      user_id: str = None, start_time: float = None, end_time: float = None,
                      limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit logs with optional filtering."""
        with self.audit_logs_lock:
            # Apply filters
            filtered_logs = self.audit_logs
            
            if event_type:
                filtered_logs = [log for log in filtered_logs if log["event_type"] == event_type]
            
            if resource_type:
                filtered_logs = [log for log in filtered_logs if log["resource_type"] == resource_type]
            
            if user_id:
                filtered_logs = [log for log in filtered_logs if log["user_id"] == user_id]
            
            if start_time:
                filtered_logs = [log for log in filtered_logs if log["timestamp"] >= start_time]
            
            if end_time:
                filtered_logs = [log for log in filtered_logs if log["timestamp"] <= end_time]
            
            # Sort by timestamp (newest first)
            filtered_logs = sorted(filtered_logs, key=lambda x: x["timestamp"], reverse=True)
            
            # Apply limit
            if limit > 0:
                filtered_logs = filtered_logs[:limit]
            
            return filtered_logs
    
    def _load_access_policies(self) -> None:
        """Load access policies."""
        try:
            # In a real implementation, this would load from a configuration file or database
            # For now, just add some default policies for medical RAG workflows
            
            with self.access_policies_lock:
                # Admin policy
                self.access_policies.append(AccessPolicy(
                    id="admin-full-access",
                    name="Admin Full Access",
                    description="Full access for administrators",
                    resource_type="*",
                    actions=["*"],
                    conditions={"role": "admin"},
                    priority=100
                ))
                
                # Medical data access policy
                self.access_policies.append(AccessPolicy(
                    id="medical-data-read",
                    name="Medical Data Read Access",
                    description="Read access to medical data for authorized users",
                    resource_type="medical_data",
                    actions=["read"],
                    conditions={"role": ["doctor", "nurse", "medical_staff"]},
                    priority=50
                ))
                
                # Patient data access policy
                self.access_policies.append(AccessPolicy(
                    id="patient-data-access",
                    name="Patient Data Access",
                    description="Access to patient data for the patient and their doctors",
                    resource_type="patient_data",
                    actions=["read", "update"],
                    conditions={"is_patient_or_doctor": True},
                    priority=60
                ))
                
                # Default deny policy
                self.access_policies.append(AccessPolicy(
                    id="default-deny",
                    name="Default Deny",
                    description="Deny access by default",
                    resource_type="*",
                    actions=["*"],
                    conditions={},
                    priority=0
                ))
                
                logger.info(f"Loaded {len(self.access_policies)} access policies")
                
        except Exception as e:
            logger.error(f"Error loading access policies: {e}")
    
    def check_access(self, request: AccessRequest) -> AccessResponse:
        """Check if access is allowed for a request."""
        try:
            # Get matching policies
            matching_policies = []
            
            with self.access_policies_lock:
                for policy in self.access_policies:
                    # Check if policy applies to resource type
                    if policy.resource_type == "*" or policy.resource_type == request.resource_type:
                        # Check if policy applies to action
                        if "*" in policy.actions or request.action in policy.actions:
                            # Check conditions
                            if self._check_policy_conditions(policy, request):
                                matching_policies.append(policy)
            
            # Sort by priority (highest first)
            matching_policies.sort(key=lambda p: p.priority, reverse=True)
            
            # Get highest priority policy
            if matching_policies:
                policy = matching_policies[0]
                
                # Default deny policy
                if policy.id == "default-deny":
                    return AccessResponse(
                        allowed=False,
                        policy_id=policy.id,
                        reason="Access denied by default policy",
                        metadata={"policy_name": policy.name}
                    )
                
                # Log access decision
                self.log_audit_event(
                    event_type="access_decision",
                    resource_type=request.resource_type,
                    resource_id=request.resource_id,
                    action=request.action,
                    status="allowed",
                    user_id=request.user_id,
                    session_id=request.session_id,
                    details={"policy_id": policy.id, "policy_name": policy.name}
                )
                
                return AccessResponse(
                    allowed=True,
                    policy_id=policy.id,
                    reason=f"Access allowed by policy: {policy.name}",
                    metadata={"policy_name": policy.name}
                )
            
            # No matching policies, deny access
            self.log_audit_event(
                event_type="access_decision",
                resource_type=request.resource_type,
                resource_id=request.resource_id,
                action=request.action,
                status="denied",
                user_id=request.user_id,
                session_id=request.session_id,
                details={"reason": "No matching policies"}
            )
            
            return AccessResponse(
                allowed=False,
                policy_id=None,
                reason="No matching policies found",
                metadata={}
            )
            
        except Exception as e:
            logger.error(f"Error checking access: {e}")
            
            # Log error
            self.log_audit_event(
                event_type="access_decision",
                resource_type=request.resource_type,
                resource_id=request.resource_id,
                action=request.action,
                status="error",
                user_id=request.user_id,
                session_id=request.session_id,
                details={"error": str(e)}
            )
            
            # Deny access on error
            return AccessResponse(
                allowed=False,
                policy_id=None,
                reason=f"Error checking access: {str(e)}",
                metadata={"error": True}
            )
    
    def _check_policy_conditions(self, policy: AccessPolicy, request: AccessRequest) -> bool:
        """Check if a policy's conditions are met for a request."""
        # This is a simplified implementation
        # In a real system, this would use a more sophisticated condition evaluation
        
        # If no conditions, policy applies
        if not policy.conditions:
            return True
        
        # Check each condition
        for key, value in policy.conditions.items():
            # Special condition: is_patient_or_doctor
            if key == "is_patient_or_doctor":
                # In a real implementation, this would check if the user is the patient or their doctor
                # For now, just check if the context has this flag
                if request.context.get("is_patient_or_doctor") != value:
                    return False
            
            # Regular condition: check if context has matching value
            elif key in request.context:
                context_value = request.context[key]
                
                # Check if value is a list
                if isinstance(value, list):
                    if context_value not in value:
                        return False
                else:
                    if context_value != value:
                        return False
            else:
                # Context doesn't have this key, condition not met
                return False
        
        # All conditions met
        return True
    
    def _start_background_processing(self) -> None:
        """Start background processing thread."""
        if self.processing_thread is not None and self.processing_thread.is_alive():
            return
        
        self.running = True
        self.processing_thread = threading.Thread(target=self._background_processing_loop)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        logger.info("Background processing thread started")
    
    def _stop_background_processing(self) -> None:
        """Stop background processing thread."""
        self.running = False
        
        if self.processing_thread is not None:
            self.processing_thread.join(timeout=5.0)
            self.processing_thread = None
        
        logger.info("Background processing thread stopped")
    
    def _background_processing_loop(self) -> None:
        """Background processing loop."""
        while self.running:
            try:
                # Get item from queue with timeout
                try:
                    item = self.processing_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Process item
                item_type, data = item
                
                if item_type == "log_audit":
                    self._process_audit_log(data)
                
                # Mark item as done
                self.processing_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in background processing: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the governance service."""
        status = "healthy"
        message = "Governance Service is healthy"
        
        try:
            # Check if background processing is running
            if self.config.background_processing_enabled and (
                self.processing_thread is None or not self.processing_thread.is_alive()
            ):
                status = "warning"
                message = "Background processing thread is not running"
                
                # Try to restart background processing
                self._start_background_processing()
        except Exception as e:
            status = "unhealthy"
            message = f"Health check failed: {str(e)}"
        
        return {
            "status": status,
            "message": message,
            "timestamp": time.time(),
            "details": {
                "background_processing_enabled": self.config.background_processing_enabled,
                "audit_log_export_enabled": self.config.audit_log_export_enabled,
                "access_policies_count": len(self.access_policies),
                "audit_logs_count": len(self.audit_logs)
            }
        }

# Initialize global instance
governance_service = None

def get_governance_service():
    """Get or create the governance service instance."""
    global governance_service
    if governance_service is None:
        governance_service = GovernanceService()
    return governance_service
