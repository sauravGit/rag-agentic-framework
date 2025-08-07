import os
import openai
from ..vector_db.client import VectorDBClient

class AgentOrchestrator:
    def __init__(self, vector_db_client: VectorDBClient, openai_api_key: str):
        self.vector_db_client = vector_db_client
        self.embedding_model = None
        openai.api_key = openai_api_key

    def _get_embedding_model(self):
        if self.embedding_model is None:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        return self.embedding_model

    def process_query(self, index_name: str, query: str):
        embedding_model = self._get_embedding_model()
        query_embedding = embedding_model.encode(query)
        search_results = self.vector_db_client.search(index_name, query_embedding)

        context = "\n".join([result['document'] for result in search_results])

        prompt = f"Answer the following question based on the provided context.\n\nContext:\n{context}\n\nQuestion:\n{query}"

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )

        return response.choices[0].text.strip()
