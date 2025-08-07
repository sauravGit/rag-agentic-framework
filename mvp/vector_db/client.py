import os
from elasticsearch import Elasticsearch
import numpy as np

class VectorDBClient:
    def __init__(self):
        self.client = Elasticsearch(os.environ.get("ELASTICSEARCH_URL"))

    def create_index(self, index_name: str, vector_dimension: int):
        if not self.client.indices.exists(index=index_name):
            self.client.indices.create(
                index=index_name,
                body={
                    "mappings": {
                        "properties": {
                            "embedding": {
                                "type": "dense_vector",
                                "dims": vector_dimension,
                            },
                            "text": {"type": "text"},
                        }
                    }
                },
            )

    def index_document(self, index_name: str, document_id: str, document: str, vector: np.ndarray):
        self.client.index(
            index=index_name,
            id=document_id,
            body={"text": document, "embedding": vector.tolist()},
        )

    def search(self, index_name: str, query_vector: np.ndarray, top_k: int = 5):
        response = self.client.search(
            index=index_name,
            body={
                "size": top_k,
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                            "params": {"query_vector": query_vector.tolist()},
                        },
                    }
                },
            },
        )
        return [
            {
                "id": hit["_id"],
                "document": hit["_source"]["text"],
                "score": hit["_score"],
            }
            for hit in response["hits"]["hits"]
        ]
