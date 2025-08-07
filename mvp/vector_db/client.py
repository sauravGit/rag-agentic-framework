import numpy as np

class VectorDBClient:
    def __init__(self):
        self.documents = {}
        self.vectors = {}

    def create_index(self, index_name: str):
        # In-memory, so nothing to do here
        pass

    def index_document(self, index_name: str, document_id: str, document: str, vector: np.ndarray):
        if index_name not in self.documents:
            self.documents[index_name] = {}
            self.vectors[index_name] = []
        self.documents[index_name][document_id] = document
        self.vectors[index_name].append((document_id, vector))

    def search(self, index_name: str, query_vector: np.ndarray, top_k: int = 5):
        if index_name not in self.vectors:
            return []

        vectors = self.vectors[index_name]
        if not vectors:
            return []

        # Unpack document IDs and their vectors
        doc_ids, doc_vectors = zip(*vectors)
        doc_vectors = np.array(doc_vectors)

        # Calculate cosine similarity
        similarities = np.dot(doc_vectors, query_vector) / (
            np.linalg.norm(doc_vectors, axis=1) * np.linalg.norm(query_vector)
        )

        # Get top_k results
        top_k_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for i in top_k_indices:
            doc_id = doc_ids[i]
            similarity = similarities[i]
            document = self.documents[index_name][doc_id]
            results.append({"id": doc_id, "document": document, "score": similarity})

        return results
