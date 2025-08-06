import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from .processor import DocumentProcessor, Document
from ..core.config import Config

app = FastAPI(
    title="Document Processor",
    description="Processes and chunks documents for the RAG pipeline.",
    version="1.0.0",
)

# In a real application, you would have a more robust way of managing the processor instance.
# For example, you might use a dependency injection system.
config = Config({})  # You would load your config here
processor = DocumentProcessor(config.document_processing)


class DocumentRequest(BaseModel):
    content: str
    metadata: Dict[str, Any] = None


@app.post("/process")
async def process_document(doc: DocumentRequest):
    try:
        document = Document(content=doc.content, metadata=doc.metadata)
        response = processor.process_document(document)
        return response.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy"}
