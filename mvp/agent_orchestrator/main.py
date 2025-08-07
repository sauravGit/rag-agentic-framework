from fastapi import FastAPI
from prometheus_client import generate_latest
from starlette.responses import Response

app = FastAPI(
    title="Agent Orchestrator",
    description="Manages and coordinates AI agents.",
    version="1.0.0",
)

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
