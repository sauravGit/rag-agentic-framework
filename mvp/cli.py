import os
import click
from .vector_db.client import VectorDBClient
from .document_processor.processor import DocumentProcessor
from .agent_orchestrator.orchestrator import AgentOrchestrator, Agent

def get_agent_orchestrator():
    vector_db_client = VectorDBClient()
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")
    agent_orchestrator = AgentOrchestrator(vector_db_client, openai_api_key)
    # Register a default agent
    default_prompt = "Answer the following question based on the provided context.\n\nContext:\n{context}\n\nQuestion:\n{query}"
    default_agent = Agent(name="default", prompt=default_prompt)
    agent_orchestrator.register_agent(default_agent)
    return agent_orchestrator

def get_document_processor():
    vector_db_client = VectorDBClient()
    return DocumentProcessor(vector_db_client)

@click.group()
def cli():
    pass


@cli.command()
@click.argument('directory_path', type=click.Path(exists=True))
@click.argument('index_name')
@click.option('--chunking-strategy', default='fixed', help='The chunking strategy to use (fixed or recursive).')
def index(directory_path, index_name, chunking_strategy):
    """Indexes the documents in a directory."""
    document_processor = get_document_processor()
    click.echo(f"Indexing documents in {directory_path} into index {index_name} using {chunking_strategy} chunking...")
    document_processor.process_directory(directory_path, index_name, chunking_strategy)
    click.echo("Done.")


@cli.command()
@click.argument('index_name')
@click.argument('query_text')
@click.option('--agent', default='default', help='The agent to use for the query.')
def query(index_name, query_text, agent):
    """Queries the RAG system."""
    agent_orchestrator = get_agent_orchestrator()
    click.echo(f"Querying index {index_name} with agent '{agent}' and query: '{query_text}'")
    response = agent_orchestrator.process_query(index_name, query_text, agent)
    click.echo("Response:")
    click.echo(response)


@cli.command()
@click.argument('name')
@click.argument('prompt')
def register_agent(name, prompt):
    """Registers a new agent."""
    agent_orchestrator = get_agent_orchestrator()
    agent = Agent(name=name, prompt=prompt)
    agent_orchestrator.register_agent(agent)
    click.echo(f"Agent '{name}' registered.")


@cli.command()
def list_agents():
    """Lists all registered agents."""
    agent_orchestrator = get_agent_orchestrator()
    click.echo("Registered agents:")
    for agent_name in agent_orchestrator.agents:
        click.echo(f"- {agent_name}")


@cli.command()
@click.argument('name')
def register_tool(name):
    """Registers a new tool."""
    agent_orchestrator = get_agent_orchestrator()
    # For the CLI, we can only register a placeholder function
    def placeholder_tool():
        return f"This is a placeholder for the '{name}' tool."
    agent_orchestrator.register_tool(name, placeholder_tool)
    click.echo(f"Tool '{name}' registered with a placeholder function.")


@cli.command()
def list_tools():
    """Lists all registered tools."""
    agent_orchestrator = get_agent_orchestrator()
    click.echo("Registered tools:")
    for tool_name in agent_orchestrator.tools:
        click.echo(f"- {tool_name}")


if __name__ == '__main__':
    cli()
