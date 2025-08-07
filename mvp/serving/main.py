import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_client import start_http_server, Counter, Histogram, generate_latest
from starlette.responses import Response
from ..vector_db.client import VectorDBClient
from ..agent_orchestrator.orchestrator import AgentOrchestrator

app = FastAPI(
    title="MVP RAG Service",
    description="A simple RAG service for the MVP.",
    version="1.0.0",
)

# Initialize components
vector_db_client = VectorDBClient()
openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")
agent_orchestrator = AgentOrchestrator(vector_db_client, openai_api_key)

# Metrics
REQUEST_COUNTER = Counter("requests_total", "Total number of requests")
REQUEST_LATENCY = Histogram("request_latency_seconds", "Request latency")

class QueryRequest(BaseModel):
    index_name: str
    query: str


@app.post("/query")
async def query(request: QueryRequest):
    REQUEST_COUNTER.inc()
    with REQUEST_LATENCY.time():
        try:
            response = agent_orchestrator.process_query(request.index_name, request.query, "default")
            return {"response": response}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
