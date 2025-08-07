import numpy as np
from mvp.vector_db.client import VectorDBClient

def test_index_and_search():
    client = VectorDBClient()
    client.create_index("test_index")

    doc1_vec = np.array([1, 2, 3])
    doc2_vec = np.array([4, 5, 6])

    client.index_document("test_index", "doc1", "This is doc1", doc1_vec)
    client.index_document("test_index", "doc2", "This is doc2", doc2_vec)

    query_vec = np.array([1, 2, 4])
    results = client.search("test_index", query_vec, top_k=1)

    assert len(results) == 1
    assert results[0]["id"] == "doc1"
