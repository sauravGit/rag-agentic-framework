import os
import re
import time
from prometheus_client import Counter, Histogram
from ..vector_db.client import VectorDBClient

DOCUMENTS_PROCESSED = Counter("documents_processed_total", "Total number of documents processed")
DOCUMENT_PROCESSING_TIME = Histogram("document_processing_seconds", "Time spent processing a document")

class DocumentProcessor:
    def __init__(self, vector_db_client: VectorDBClient):
        self.vector_db_client = vector_db_client
        self.embedding_model = None

    def _get_embedding_model(self):
        if self.embedding_model is None:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        return self.embedding_model

    def process_directory(self, directory_path: str, index_name: str, chunking_strategy: str = 'fixed'):
        for filename in os.listdir(directory_path):
            filepath = os.path.join(directory_path, filename)
            if os.path.isfile(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.process_document(index_name, filename, content, chunking_strategy)

    def process_document(self, index_name: str, document_id: str, content: str, chunking_strategy: str = 'fixed'):
        with DOCUMENT_PROCESSING_TIME.time():
            if chunking_strategy == 'fixed':
                chunks = self._fixed_size_chunking(content)
            elif chunking_strategy == 'recursive':
                chunks = self._recursive_chunking(content)
            else:
                raise ValueError(f"Unknown chunking strategy: {chunking_strategy}")

            embedding_model = self._get_embedding_model()
            vector_dimension = embedding_model.get_sentence_embedding_dimension()
            self.vector_db_client.create_index(index_name, vector_dimension)
            for i, chunk in enumerate(chunks):
                chunk_id = f"{document_id}_chunk_{i}"
                embedding = embedding_model.encode(chunk)
                self.vector_db_client.index_document(index_name, chunk_id, chunk, embedding)
        DOCUMENTS_PROCESSED.inc()

    def _fixed_size_chunking(self, content: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
        chunks = []
        start = 0
        while start < len(content):
            end = start + chunk_size
            chunks.append(content[start:end])
            start += chunk_size - overlap
        return chunks

    def _recursive_chunking(self, content: str, chunk_size: int = 512) -> list[str]:
        # A simple recursive chunking implementation
        chunks = []
        if len(content) <= chunk_size:
            return [content]

        # First, try to split by paragraphs
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 1:
            for p in paragraphs:
                chunks.extend(self._recursive_chunking(p, chunk_size))
            return chunks

        # If no paragraphs, split by sentences
        sentences = re.split(r'(?<=[.!?])\s+', content)
        if len(sentences) > 1:
            current_chunk = ""
            for s in sentences:
                if len(current_chunk) + len(s) > chunk_size:
                    chunks.append(current_chunk)
                    current_chunk = s
                else:
                    current_chunk += " " + s
            if current_chunk:
                chunks.append(current_chunk)
            return chunks

        # If still too large, use fixed-size chunking as a fallback
        return self._fixed_size_chunking(content, chunk_size)
