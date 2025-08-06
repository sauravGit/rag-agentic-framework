import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

from .service import EvaluationService, EvaluationRequest
from ..core.config import Config

app = FastAPI(
    title="Evaluation Service",
    description="Evaluates the performance of the RAG system.",
    version="1.0.0",
)

# In a real application, you would have a more robust way of managing the service instance.
config = Config({})  # You would load your config here
evaluation_service = EvaluationService(config.evaluation)


class EvalRequest(BaseModel):
    query: str
    response: str
    retrieved_documents: List[Dict[str, Any]]
    ground_truth: str = None
    evaluation_types: List[str] = None
    metadata: Dict[str, Any] = None


@app.post("/evaluate")
async def evaluate(request: EvalRequest):
    try:
        eval_request = EvaluationRequest(
            query=request.query,
            response=request.response,
            retrieved_documents=request.retrieved_documents,
            ground_truth=request.ground_truth,
            evaluation_types=request.evaluation_types,
            metadata=request.metadata,
        )
        response = evaluation_service.evaluate(eval_request)
        return response.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}
