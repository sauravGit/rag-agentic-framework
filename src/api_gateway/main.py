import os
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(
    title="API Gateway",
    description="The API Gateway for the MLOps RAG Framework",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AGENT_ORCHESTRATOR_URL = os.environ.get("AGENT_ORCHESTRATOR_URL")
DOCUMENT_PROCESSOR_URL = os.environ.get("DOCUMENT_PROCESSOR_URL")
COMPLIANCE_URL = os.environ.get("COMPLIANCE_URL")
EVALUATION_URL = os.environ.get("EVALUATION_URL")
MONITORING_URL = os.environ.get("MONITORING_URL")
COST_OPTIMIZER_URL = os.environ.get("COST_OPTIMIZER_URL")


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        url = f"{AGENT_ORCHESTRATOR_URL}/{path}"
        try:
            response = await client.request(
                method=request.method,
                url=url,
                headers=request.headers,
                content=await request.body(),
            )
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {e}")


@app.get("/health")
async def health_check():
    services = {
        "agent-orchestrator": AGENT_ORCHESTRATOR_URL,
        "document-processor": DOCUMENT_PROCESSOR_URL,
        "compliance-service": COMPLIANCE_URL,
        "evaluation-service": EVALUATION_URL,
        "monitoring-service": MONITORING_URL,
        "cost-optimizer": COST_OPTIMIZER_URL,
    }
    health_status = {}
    async with httpx.AsyncClient() as client:
        for name, url in services.items():
            try:
                response = await client.get(f"{url}/health")
                if response.status_code == 200:
                    health_status[name] = "healthy"
                else:
                    health_status[name] = "unhealthy"
            except httpx.RequestError:
                health_status[name] = "unreachable"
    return health_status
