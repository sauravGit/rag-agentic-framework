from unittest.mock import MagicMock, patch
from mvp.agent_orchestrator.orchestrator import AgentOrchestrator

@patch('mvp.agent_orchestrator.orchestrator.AgentOrchestrator._get_embedding_model')
@patch('openai.Completion.create')
def test_process_query(mock_openai_create, mock_get_embedding_model):
    # Create a mock VectorDBClient
    mock_vector_db_client = MagicMock()
    mock_vector_db_client.search.return_value = [{"document": "This is a test document."}]

    # Create an AgentOrchestrator with the mock client
    orchestrator = AgentOrchestrator(mock_vector_db_client, "fake_api_key")

    # Mock the OpenAI API response
    mock_openai_create.return_value.choices = [MagicMock(text="This is a test response.")]

    # Process a query
    response = orchestrator.process_query("test_index", "What is this?")

    # Check that the search method was called on the mock client
    mock_vector_db_client.search.assert_called()

    # Check that the OpenAI API was called
    mock_openai_create.assert_called()

    # Check that the response is correct
    assert response == "This is a test response."
