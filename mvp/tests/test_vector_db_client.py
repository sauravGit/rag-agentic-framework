import numpy as np
from unittest.mock import MagicMock, patch
from mvp.vector_db.client import VectorDBClient

@patch('mvp.vector_db.client.Elasticsearch')
def test_index_and_search(mock_elasticsearch):
    # Create a mock Elasticsearch client
    mock_es_client = MagicMock()
    mock_elasticsearch.return_value = mock_es_client

    # Create a VectorDBClient with the mock client
    client = VectorDBClient()

    # Test create_index
    client.create_index("test_index", 3)
    mock_es_client.indices.exists.assert_called_with(index="test_index")

    # Test index_document
    doc1_vec = np.array([1, 2, 3])
    client.index_document("test_index", "doc1", "This is doc1", doc1_vec)
    mock_es_client.index.assert_called_with(
        index="test_index",
        id="doc1",
        body={"text": "This is doc1", "embedding": [1.0, 2.0, 3.0]},
    )

    # Test search
    query_vec = np.array([1, 2, 4])
    mock_es_client.search.return_value = {
        "hits": {
            "hits": [
                {
                    "_id": "doc1",
                    "_source": {"text": "This is doc1"},
                    "_score": 1.0,
                }
            ]
        }
    }
    results = client.search("test_index", query_vec, top_k=1)
    mock_es_client.search.assert_called()
    assert len(results) == 1
    assert results[0]["id"] == "doc1"
