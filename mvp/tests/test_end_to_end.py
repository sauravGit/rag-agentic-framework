import os
from unittest.mock import MagicMock, patch
from mvp.vector_db.client import VectorDBClient
from mvp.document_processor.processor import DocumentProcessor
from mvp.agent_orchestrator.orchestrator import AgentOrchestrator, Agent

@patch('mvp.vector_db.client.Elasticsearch')
@patch('mvp.document_processor.processor.DocumentProcessor._get_embedding_model')
@patch('mvp.agent_orchestrator.orchestrator.AgentOrchestrator._get_embedding_model')
@patch('openai.Completion.create')
def test_end_to_end(mock_openai_create, mock_agent_get_embedding_model, mock_doc_get_embedding_model, mock_elasticsearch):
    # Create a mock Elasticsearch client
    mock_es_client = MagicMock()
    mock_elasticsearch.return_value = mock_es_client

    # Create a dummy directory and some dummy files
    dummy_dir = "dummy_test_dir_e2e"
    os.makedirs(dummy_dir, exist_ok=True)
    with open(os.path.join(dummy_dir, "doc1.txt"), "w") as f:
        f.write("The sky is blue.")
    with open(os.path.join(dummy_dir, "doc2.txt"), "w") as f:
        f.write("The grass is green.")

    # Create the components
    vector_db_client = VectorDBClient()
    document_processor = DocumentProcessor(vector_db_client)
    orchestrator = AgentOrchestrator(vector_db_client, "fake_api_key")

    # Register a default agent
    default_prompt = "Answer the following question based on the provided context.\n\nContext:\n{context}\n\nQuestion:\n{query}"
    default_agent = Agent(name="default", prompt=default_prompt)
    orchestrator.register_agent(default_agent)

    # Index the documents
    document_processor.process_directory(dummy_dir, "e2e_test_index")

    # Mock the search results
    mock_es_client.search.return_value = {
        "hits": {
            "hits": [
                {
                    "_id": "doc1.txt_chunk_0",
                    "_source": {"text": "The sky is blue."},
                    "_score": 1.0,
                }
            ]
        }
    }

    # Mock the OpenAI API response
    mock_openai_create.return_value.choices = [MagicMock(text="The sky is blue.")]

    # Ask a question
    response = orchestrator.process_query("e2e_test_index", "What color is the sky?", "default")

    # Check that the response is correct
    assert "blue" in response.lower()

    # Clean up the dummy directory and files
    os.remove(os.path.join(dummy_dir, "doc1.txt"))
    os.remove(os.path.join(dummy_dir, "doc2.txt"))
    os.rmdir(dummy_dir)
