import os
import click
from .vector_db.client import VectorDBClient
from .document_processor.processor import DocumentProcessor
from .agent_orchestrator.orchestrator import AgentOrchestrator

# Initialize components
vector_db_client = VectorDBClient()
document_processor = DocumentProcessor(vector_db_client)
openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")
agent_orchestrator = AgentOrchestrator(vector_db_client, openai_api_key)


@click.group()
def cli():
    pass


@cli.command()
@click.argument('directory_path', type=click.Path(exists=True))
@click.argument('index_name')
def index(directory_path, index_name):
    """Indexes the documents in a directory."""
    click.echo(f"Indexing documents in {directory_path} into index {index_name}...")
    document_processor.process_directory(directory_path, index_name)
    click.echo("Done.")


@cli.command()
@click.argument('index_name')
@click.argument('query_text')
def query(index_name, query_text):
    """Queries the RAG system."""
    click.echo(f"Querying index {index_name} with: '{query_text}'")
    response = agent_orchestrator.process_query(index_name, query_text)
    click.echo("Response:")
    click.echo(response)


if __name__ == '__main__':
    cli()
