import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

from .service import CostOptimizationService, CostOptimizationRequest
from ..core.config import Config

app = FastAPI(
    title="Cost Optimization Service",
    description="Optimizes the cost of RAG workflows.",
    version="1.0.0",
)

# In a real application, you would have a more robust way of managing the service instance.
config = Config({})  # You would load your config here
cost_optimization_service = CostOptimizationService(config.cost_optimization)


class OptRequest(BaseModel):
    query: str
    context: Dict[str, Any] = None
    optimization_types: List[str] = None
    metadata: Dict[str, Any] = None


@app.post("/optimize")
async def optimize(request: OptRequest):
    try:
        opt_request = CostOptimizationRequest(
            query=request.query,
            context=request.context,
            optimization_types=request.optimization_types,
            metadata=request.metadata,
        )
        response = cost_optimization_service.optimize(opt_request)
        return response.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}
