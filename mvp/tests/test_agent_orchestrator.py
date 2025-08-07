from unittest.mock import MagicMock, patch
from mvp.agent_orchestrator.orchestrator import AgentOrchestrator, Agent

@patch('mvp.agent_orchestrator.orchestrator.AgentOrchestrator._get_embedding_model')
@patch('openai.Completion.create')
def test_process_query_with_agent(mock_openai_create, mock_get_embedding_model):
    # Create a mock VectorDBClient
    mock_vector_db_client = MagicMock()
    mock_vector_db_client.search.return_value = [{"document": "This is a test document."}]

    # Create an AgentOrchestrator with the mock client
    orchestrator = AgentOrchestrator(mock_vector_db_client, "fake_api_key")

    # Register a test agent
    test_prompt = "Test prompt: {context} - {query}"
    test_agent = Agent(name="test_agent", prompt=test_prompt)
    orchestrator.register_agent(test_agent)

    # Mock the OpenAI API response
    mock_openai_create.return_value.choices = [MagicMock(text="This is a test response.")]

    # Process a query
    response = orchestrator.process_query("test_index", "What is this?", "test_agent")

    # Check that the search method was called on the mock client
    mock_vector_db_client.search.assert_called()

    # Check that the OpenAI API was called
    mock_openai_create.assert_called()

    # Check that the response is correct
    assert response == "This is a test response."

def test_register_tool():
    # Create a mock VectorDBClient
    mock_vector_db_client = MagicMock()

    # Create an AgentOrchestrator with the mock client
    orchestrator = AgentOrchestrator(mock_vector_db_client, "fake_api_key")

    # Register a test tool
    def test_tool():
        return "This is a test tool."
    orchestrator.register_tool("test_tool", test_tool)

    # Check that the tool was registered
    assert "test_tool" in orchestrator.tools
    assert orchestrator.tools["test_tool"]() == "This is a test tool."
