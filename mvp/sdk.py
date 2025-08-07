import os
from .vector_db.client import VectorDBClient
from .document_processor.processor import DocumentProcessor
from .agent_orchestrator.orchestrator import AgentOrchestrator, Agent

class RAGFramework:
    def __init__(self, openai_api_key: str = None):
        if openai_api_key is None:
            openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not provided or set as an environment variable.")

        self.vector_db_client = VectorDBClient()
        self.document_processor = DocumentProcessor(self.vector_db_client)
        self.agent_orchestrator = AgentOrchestrator(self.vector_db_client, openai_api_key)

        # Register a default agent
        default_prompt = "Answer the following question based on the provided context.\n\nContext:\n{context}\n\nQuestion:\n{query}"
        default_agent = Agent(name="default", prompt=default_prompt)
        self.agent_orchestrator.register_agent(default_agent)

    def index_directory(self, directory_path: str, index_name: str, chunking_strategy: str = 'fixed'):
        self.document_processor.process_directory(directory_path, index_name, chunking_strategy)

    def query(self, index_name: str, query_text: str, agent: str = 'default'):
        return self.agent_orchestrator.process_query(index_name, query_text, agent)

    def register_agent(self, name: str, prompt: str, tools: list = None):
        agent = Agent(name=name, prompt=prompt, tools=tools)
        self.agent_orchestrator.register_agent(agent)

    def list_agents(self):
        return list(self.agent_orchestrator.agents.keys())

    def register_tool(self, tool_name: str, tool_function):
        self.agent_orchestrator.register_tool(tool_name, tool_function)

    def list_tools(self):
        return list(self.agent_orchestrator.tools.keys())
