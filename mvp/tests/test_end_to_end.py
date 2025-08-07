import os
from unittest.mock import MagicMock, patch
from mvp.vector_db.client import VectorDBClient
from mvp.document_processor.processor import DocumentProcessor
from mvp.agent_orchestrator.orchestrator import AgentOrchestrator

@patch('mvp.document_processor.processor.DocumentProcessor._get_embedding_model')
@patch('mvp.agent_orchestrator.orchestrator.AgentOrchestrator._get_embedding_model')
@patch('openai.Completion.create')
def test_end_to_end(mock_openai_create, mock_agent_get_embedding_model, mock_doc_get_embedding_model):
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

    # Index the documents
    document_processor.process_directory(dummy_dir, "e2e_test_index")

    # Mock the OpenAI API response
    mock_openai_create.return_value.choices = [MagicMock(text="The sky is blue.")]

    # Ask a question
    response = orchestrator.process_query("e2e_test_index", "What color is the sky?")

    # Check that the response is correct
    assert "blue" in response.lower()

    # Clean up the dummy directory and files
    os.remove(os.path.join(dummy_dir, "doc1.txt"))
    os.remove(os.path.join(dummy_dir, "doc2.txt"))
    os.rmdir(dummy_dir)
