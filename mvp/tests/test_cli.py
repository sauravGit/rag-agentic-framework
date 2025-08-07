import os
from click.testing import CliRunner
from unittest.mock import patch
from mvp.cli import cli

@patch('mvp.cli.get_document_processor')
@patch('mvp.cli.VectorDBClient')
def test_register_agent(mock_vector_db_client, mock_get_doc_processor, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake_key")
    runner = CliRunner()
    result = runner.invoke(cli, ['register-agent', 'test_agent', 'test_prompt'])
    assert result.exit_code == 0
    assert "Agent 'test_agent' registered." in result.output

@patch('mvp.cli.get_document_processor')
@patch('mvp.cli.VectorDBClient')
def test_list_agents(mock_vector_db_client, mock_get_doc_processor, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake_key")
    runner = CliRunner()
    result = runner.invoke(cli, ['list-agents'])
    assert result.exit_code == 0
    assert "Registered agents:" in result.output
    assert "- default" in result.output

@patch('mvp.cli.get_document_processor')
@patch('mvp.cli.VectorDBClient')
def test_register_tool(mock_vector_db_client, mock_get_doc_processor, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake_key")
    runner = CliRunner()
    result = runner.invoke(cli, ['register-tool', 'test_tool'])
    assert result.exit_code == 0
    assert "Tool 'test_tool' registered with a placeholder function." in result.output

@patch('mvp.cli.get_document_processor')
@patch('mvp.cli.VectorDBClient')
def test_list_tools(mock_vector_db_client, mock_get_doc_processor, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake_key")
    runner = CliRunner()
    result = runner.invoke(cli, ['list-tools'])
    assert result.exit_code == 0
    assert "Registered tools:" in result.output
