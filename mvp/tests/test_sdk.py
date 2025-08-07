import os
from unittest.mock import patch
from mvp.sdk import RAGFramework

@patch('mvp.sdk.VectorDBClient')
@patch('mvp.sdk.DocumentProcessor')
@patch('mvp.sdk.AgentOrchestrator')
def test_sdk_init(mock_agent_orchestrator, mock_doc_processor, mock_vector_db_client):
    sdk = RAGFramework(openai_api_key="fake_key")
    assert sdk.agent_orchestrator is not None
    assert sdk.document_processor is not None
    assert sdk.vector_db_client is not None

@patch('mvp.sdk.VectorDBClient')
@patch('mvp.sdk.AgentOrchestrator')
def test_sdk_query(mock_agent_orchestrator, mock_vector_db_client):
    sdk = RAGFramework(openai_api_key="fake_key")
    sdk.query("test_index", "test_query")
    sdk.agent_orchestrator.process_query.assert_called_with("test_index", "test_query", "default")
