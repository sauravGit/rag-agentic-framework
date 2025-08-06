import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from .orchestrator import AgentOrchestrator
from ..core.config import Config

app = FastAPI(
    title="Agent Orchestrator",
    description="Manages and coordinates AI agents.",
    version="1.0.0",
)

# In a real application, you would have a more robust way of managing the orchestrator instance.
# For example, you might use a dependency injection system.
config = Config({})  # You would load your config here
orchestrator = AgentOrchestrator(config)


class Query(BaseModel):
    session_id: str
    query: str
    context: Dict[str, Any] = None


@app.post("/query")
async def query(query: Query):
    try:
        response = orchestrator.process_query(
            session_id=query.session_id, query=query.query, context=query.context
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/session")
async def create_session(user_id: str):
    response = orchestrator.create_session(user_id)
    return response


@app.get("/health")
async def health():
    return {"status": "healthy"}
