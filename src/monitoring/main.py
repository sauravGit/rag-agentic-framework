import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

from .service import MonitoringService, MetricDataPoint
from ..core.config import Config

app = FastAPI(
    title="Monitoring Service",
    description="Monitors the health and performance of the RAG system.",
    version="1.0.0",
)

# In a real application, you would have a more robust way of managing the service instance.
config = Config({})  # You would load your config here
monitoring_service = MonitoringService(config.monitoring)


class MetricRequest(BaseModel):
    name: str
    value: float
    labels: Dict[str, str] = None


@app.post("/metric")
async def record_metric(metric: MetricRequest):
    try:
        monitoring_service.record_metric(
            name=metric.name, value=metric.value, labels=metric.labels
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics(names: List[str] = None):
    try:
        response = monitoring_service.get_metrics(names=names)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}
