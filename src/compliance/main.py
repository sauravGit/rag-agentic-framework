import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

from .service import ComplianceService, ComplianceCheck
from ..core.config import Config

app = FastAPI(
    title="Compliance Service",
    description="Handles compliance checks for HIPAA and PII.",
    version="1.0.0",
)

# In a real application, you would have a more robust way of managing the service instance.
config = Config({})  # You would load your config here
compliance_service = ComplianceService(config.compliance)


class CheckRequest(BaseModel):
    content: str
    content_type: str = "text"
    metadata: Dict[str, Any] = None
    check_types: List[str] = None


@app.post("/check")
async def check_compliance(request: CheckRequest):
    try:
        check = ComplianceCheck(
            content=request.content,
            content_type=request.content_type,
            metadata=request.metadata,
            check_types=request.check_types,
        )
        response = compliance_service.check_compliance(check)
        return response.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}
