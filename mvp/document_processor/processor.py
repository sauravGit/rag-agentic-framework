import os
from ..vector_db.client import VectorDBClient

class DocumentProcessor:
    def __init__(self, vector_db_client: VectorDBClient):
        self.vector_db_client = vector_db_client
        self.embedding_model = None

    def _get_embedding_model(self):
        if self.embedding_model is None:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        return self.embedding_model

    def process_directory(self, directory_path: str, index_name: str):
        for filename in os.listdir(directory_path):
            filepath = os.path.join(directory_path, filename)
            if os.path.isfile(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.process_document(index_name, filename, content)

    def process_document(self, index_name: str, document_id: str, content: str):
        chunks = self._chunk_content(content)
        embedding_model = self._get_embedding_model()
        for i, chunk in enumerate(chunks):
            chunk_id = f"{document_id}_chunk_{i}"
            embedding = embedding_model.encode(chunk)
            self.vector_db_client.index_document(index_name, chunk_id, chunk, embedding)

    def _chunk_content(self, content: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
        chunks = []
        start = 0
        while start < len(content):
            end = start + chunk_size
            chunks.append(content[start:end])
            start += chunk_size - overlap
        return chunks
