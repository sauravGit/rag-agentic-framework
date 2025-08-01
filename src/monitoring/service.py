"""
Monitoring module for the Enhanced MLOps Framework for Agentic AI RAG Workflows.

This module provides functionality for monitoring and observability of the framework,
including metrics collection, logging, and alerting for medical customer support scenarios.
"""

import os
import logging
import time
from typing import Dict, Any, Optional, List, Union
import json
import datetime
from pydantic import BaseModel, Field
import threading
import queue

from ..core import FrameworkException, ServiceRegistry
from ..core.config import MonitoringConfig, ConfigManager

logger = logging.getLogger(__name__)

class MetricDataPoint(BaseModel):
    """Model for a metric data point."""
    
    name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    timestamp: float = Field(..., description="Timestamp when the metric was recorded")
    labels: Dict[str, str] = Field(default_factory=dict, description="Metric labels")

class AlertConfig(BaseModel):
    """Model for an alert configuration."""
    
    name: str = Field(..., description="Alert name")
    metric_name: str = Field(..., description="Metric name to monitor")
    condition: str = Field(..., description="Alert condition (e.g., '> 0.9')")
    duration: int = Field(0, description="Duration in seconds the condition must be true")
    labels: Dict[str, str] = Field(default_factory=dict, description="Alert labels")
    description: str = Field("", description="Alert description")
    severity: str = Field("warning", description="Alert severity (info, warning, error, critical)")

class Alert(BaseModel):
    """Model for an active alert."""
    
    name: str = Field(..., description="Alert name")
    metric_name: str = Field(..., description="Metric name that triggered the alert")
    condition: str = Field(..., description="Alert condition that was met")
    value: float = Field(..., description="Current metric value")
    labels: Dict[str, str] = Field(default_factory=dict, description="Alert labels")
    description: str = Field("", description="Alert description")
    severity: str = Field("warning", description="Alert severity")
    start_time: float = Field(..., description="Timestamp when the alert started")
    last_updated: float = Field(..., description="Timestamp when the alert was last updated")
    active: bool = Field(True, description="Whether the alert is active")

class MonitoringService:
    """Service for monitoring and observability of the framework."""
    
    def __init__(self, config: MonitoringConfig = None):
        """Initialize the monitoring service with configuration."""
        if config is None:
            config_manager = ConfigManager()
            app_config = config_manager.get_config()
            config = app_config.monitoring
        
        self.config = config
        
        # Initialize metrics storage
        self.metrics = {}
        self.metrics_lock = threading.Lock()
        
        # Initialize alerts
        self.alert_configs = []
        self.active_alerts = []
        self.alerts_lock = threading.Lock()
        
        # Initialize background processing
        self.processing_queue = queue.Queue()
        self.processing_thread = None
        self.running = False
        
        # Load alert configurations
        self._load_alert_configs()
        
        # Start background processing if enabled
        if self.config.background_processing_enabled:
            self._start_background_processing()
        
        # Register with service registry
        service_registry = ServiceRegistry()
        service_registry.register("monitoring_service", self)
        
        logger.info("Monitoring Service initialized")
    
    def record_metric(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Record a metric data point."""
        if labels is None:
            labels = {}
        
        # Create data point
        data_point = MetricDataPoint(
            name=name,
            value=value,
            timestamp=time.time(),
            labels=labels
        )
        
        # Add to processing queue if background processing is enabled
        if self.config.background_processing_enabled:
            self.processing_queue.put(("record_metric", data_point))
            return
        
        # Otherwise, process immediately
        self._process_metric(data_point)
    
    def _process_metric(self, data_point: MetricDataPoint) -> None:
        """Process a metric data point."""
        with self.metrics_lock:
            # Initialize metric if it doesn't exist
            if data_point.name not in self.metrics:
                self.metrics[data_point.name] = []
            
            # Add data point
            self.metrics[data_point.name].append(data_point.dict())
            
            # Trim metric history if it exceeds max size
            if len(self.metrics[data_point.name]) > self.config.max_metric_history:
                self.metrics[data_point.name] = self.metrics[data_point.name][-self.config.max_metric_history:]
        
        # Check alerts if enabled
        if self.config.alerting_enabled:
            self._check_alerts(data_point)
    
    def get_metrics(self, names: List[str] = None, start_time: float = None, end_time: float = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get metrics data."""
        with self.metrics_lock:
            result = {}
            
            # Filter metrics by name if specified
            metric_names = names if names else list(self.metrics.keys())
            
            for name in metric_names:
                if name in self.metrics:
                    # Filter by time range if specified
                    if start_time or end_time:
                        filtered_data = []
                        for point in self.metrics[name]:
                            if (start_time is None or point["timestamp"] >= start_time) and \
                               (end_time is None or point["timestamp"] <= end_time):
                                filtered_data.append(point)
                        result[name] = filtered_data
                    else:
                        result[name] = self.metrics[name]
            
            return result
    
    def get_metric_summary(self, names: List[str] = None, window_seconds: int = 300) -> Dict[str, Dict[str, Any]]:
        """Get summary statistics for metrics."""
        # Calculate start time for the window
        start_time = time.time() - window_seconds
        
        # Get metrics for the window
        metrics_data = self.get_metrics(names, start_time)
        
        # Calculate summary statistics
        result = {}
        for name, data_points in metrics_data.items():
            if not data_points:
                continue
            
            values = [point["value"] for point in data_points]
            
            result[name] = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "latest": values[-1],
                "window_seconds": window_seconds
            }
        
        return result
    
    def _load_alert_configs(self) -> None:
        """Load alert configurations."""
        try:
            # In a real implementation, this would load from a configuration file or database
            # For now, just add some default alerts for medical RAG workflows
            
            with self.alerts_lock:
                # Response time alert
                self.alert_configs.append(AlertConfig(
                    name="high_response_time",
                    metric_name="serving_request_duration",
                    condition="> 5.0",  # More than 5 seconds
                    duration=60,  # Sustained for 1 minute
                    labels={},
                    description="Response time is higher than expected",
                    severity="warning"
                ))
                
                # Error rate alert
                self.alert_configs.append(AlertConfig(
                    name="high_error_rate",
                    metric_name="serving_request_error",
                    condition="> 0.05",  # More than 5% error rate
                    duration=300,  # Sustained for 5 minutes
                    labels={},
                    description="Error rate is higher than expected",
                    severity="error"
                ))
                
                # Compliance issue alert
                self.alert_configs.append(AlertConfig(
                    name="compliance_issues",
                    metric_name="compliance_issues",
                    condition="> 0",  # Any compliance issues
                    duration=0,  # Immediate alert
                    labels={},
                    description="Compliance issues detected in responses",
                    severity="warning"
                ))
                
                # Low relevance score alert
                self.alert_configs.append(AlertConfig(
                    name="low_relevance_score",
                    metric_name="evaluation_relevance_score",
                    condition="< 0.7",  # Less than 70% relevance
                    duration=600,  # Sustained for 10 minutes
                    labels={},
                    description="Responses have low relevance scores",
                    severity="warning"
                ))
                
                logger.info(f"Loaded {len(self.alert_configs)} alert configurations")
                
        except Exception as e:
            logger.error(f"Error loading alert configurations: {e}")
    
    def _check_alerts(self, data_point: MetricDataPoint) -> None:
        """Check if a metric data point triggers any alerts."""
        with self.alerts_lock:
            # Check each alert configuration
            for config in self.alert_configs:
                if config.metric_name == data_point.name:
                    # Check if labels match (if specified in config)
                    if all(data_point.labels.get(k) == v for k, v in config.labels.items()):
                        # Check condition
                        if self._evaluate_condition(data_point.value, config.condition):
                            # Check if alert already exists
                            existing_alert = None
                            for alert in self.active_alerts:
                                if alert.name == config.name and alert.active:
                                    existing_alert = alert
                                    break
                            
                            if existing_alert:
                                # Update existing alert
                                existing_alert.value = data_point.value
                                existing_alert.last_updated = time.time()
                            else:
                                # Create new alert
                                alert = Alert(
                                    name=config.name,
                                    metric_name=config.metric_name,
                                    condition=config.condition,
                                    value=data_point.value,
                                    labels=data_point.labels,
                                    description=config.description,
                                    severity=config.severity,
                                    start_time=time.time(),
                                    last_updated=time.time(),
                                    active=True
                                )
                                self.active_alerts.append(alert)
                                
                                # Log alert
                                logger.warning(f"Alert triggered: {alert.name} - {alert.description}")
                                
                                # Send notification if configured
                                if self.config.alert_notifications_enabled:
                                    self._send_alert_notification(alert)
                        else:
                            # Check if alert needs to be resolved
                            for alert in self.active_alerts:
                                if alert.name == config.name and alert.active:
                                    alert.active = False
                                    alert.last_updated = time.time()
                                    
                                    # Log resolution
                                    logger.info(f"Alert resolved: {alert.name}")
                                    
                                    # Send resolution notification if configured
                                    if self.config.alert_notifications_enabled:
                                        self._send_alert_resolution(alert)
    
    def _evaluate_condition(self, value: float, condition: str) -> bool:
        """Evaluate an alert condition."""
        try:
            # Parse condition
            operator = None
            threshold = None
            
            if ">" in condition:
                operator = ">"
                threshold = float(condition.split(">")[1].strip())
            elif "<" in condition:
                operator = "<"
                threshold = float(condition.split("<")[1].strip())
            elif ">=" in condition:
                operator = ">="
                threshold = float(condition.split(">=")[1].strip())
            elif "<=" in condition:
                operator = "<="
                threshold = float(condition.split("<=")[1].strip())
            elif "==" in condition:
                operator = "=="
                threshold = float(condition.split("==")[1].strip())
            else:
                logger.error(f"Invalid condition format: {condition}")
                return False
            
            # Evaluate condition
            if operator == ">":
                return value > threshold
            elif operator == "<":
                return value < threshold
            elif operator == ">=":
                return value >= threshold
            elif operator == "<=":
                return value <= threshold
            elif operator == "==":
                return value == threshold
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False
    
    def _send_alert_notification(self, alert: Alert) -> None:
        """Send a notification for an alert."""
        # This is a simplified implementation
        # In a real system, this would send an email, Slack message, etc.
        
        logger.info(f"Alert notification: {alert.name} - {alert.description} - {alert.severity}")
        
        # In a real implementation, this would use a notification service
        # For now, just log the notification
    
    def _send_alert_resolution(self, alert: Alert) -> None:
        """Send a notification for an alert resolution."""
        # This is a simplified implementation
        # In a real system, this would send an email, Slack message, etc.
        
        logger.info(f"Alert resolution: {alert.name} - {alert.description}")
        
        # In a real implementation, this would use a notification service
        # For now, just log the notification
    
    def get_active_alerts(self, severity: str = None) -> List[Dict[str, Any]]:
        """Get active alerts."""
        with self.alerts_lock:
            # Filter alerts by severity if specified
            if severity:
                alerts = [alert.dict() for alert in self.active_alerts if alert.active and alert.severity == severity]
            else:
                alerts = [alert.dict() for alert in self.active_alerts if alert.active]
            
            return alerts
    
    def get_alert_history(self, start_time: float = None, end_time: float = None) -> List[Dict[str, Any]]:
        """Get alert history."""
        with self.alerts_lock:
            # Filter alerts by time range if specified
            if start_time or end_time:
                filtered_alerts = []
                for alert in self.active_alerts:
                    if (start_time is None or alert.start_time >= start_time) and \
                       (end_time is None or alert.start_time <= end_time):
                        filtered_alerts.append(alert.dict())
                return filtered_alerts
            else:
                return [alert.dict() for alert in self.active_alerts]
    
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
                
                if item_type == "record_metric":
                    self._process_metric(data)
                
                # Mark item as done
                self.processing_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in background processing: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the monitoring service."""
        status = "healthy"
        message = "Monitoring Service is healthy"
        
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
                "alerting_enabled": self.config.alerting_enabled,
                "alert_notifications_enabled": self.config.alert_notifications_enabled,
                "active_alerts": len([a for a in self.active_alerts if a.active]),
                "metrics_count": len(self.metrics)
            }
        }

# Initialize global instance
monitoring_service = None

def get_monitoring_service():
    """Get or create the monitoring service instance."""
    global monitoring_service
    if monitoring_service is None:
        monitoring_service = MonitoringService()
    return monitoring_service
