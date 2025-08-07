import os
import click
from .vector_db.client import VectorDBClient
from .document_processor.processor import DocumentProcessor
from .agent_orchestrator.orchestrator import AgentOrchestrator, Agent

# Initialize components
vector_db_client = VectorDBClient()
document_processor = DocumentProcessor(vector_db_client)
openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")
agent_orchestrator = AgentOrchestrator(vector_db_client, openai_api_key)

# Register a default agent
default_prompt = "Answer the following question based on the provided context.\n\nContext:\n{context}\n\nQuestion:\n{query}"
default_agent = Agent(name="default", prompt=default_prompt)
agent_orchestrator.register_agent(default_agent)


@click.group()
def cli():
    pass


@cli.command()
@click.argument('directory_path', type=click.Path(exists=True))
@click.argument('index_name')
@click.option('--chunking-strategy', default='fixed', help='The chunking strategy to use (fixed or recursive).')
def index(directory_path, index_name, chunking_strategy):
    """Indexes the documents in a directory."""
    click.echo(f"Indexing documents in {directory_path} into index {index_name} using {chunking_strategy} chunking...")
    document_processor.process_directory(directory_path, index_name, chunking_strategy)
    click.echo("Done.")


@cli.command()
@click.argument('index_name')
@click.argument('query_text')
@click.option('--agent', default='default', help='The agent to use for the query.')
def query(index_name, query_text, agent):
    """Queries the RAG system."""
    click.echo(f"Querying index {index_name} with agent '{agent}' and query: '{query_text}'")
    response = agent_orchestrator.process_query(index_name, query_text, agent)
    click.echo("Response:")
    click.echo(response)


if __name__ == '__main__':
    cli()
