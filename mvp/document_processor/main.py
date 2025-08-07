from fastapi import FastAPI
from prometheus_client import generate_latest
from starlette.responses import Response

app = FastAPI(
    title="Document Processor",
    description="Processes and chunks documents for the RAG pipeline.",
    version="1.0.0",
)

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
