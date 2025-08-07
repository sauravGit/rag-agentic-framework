import os
import openai
import time
from prometheus_client import Counter, Histogram
from ..vector_db.client import VectorDBClient

QUERIES_PROCESSED = Counter("queries_processed_total", "Total number of queries processed", ["agent_name"])
QUERY_PROCESSING_TIME = Histogram("query_processing_seconds", "Time spent processing a query", ["agent_name"])

class Agent:
    def __init__(self, name: str, prompt: str, tools: list = None):
        self.name = name
        self.prompt = prompt
        self.tools = tools or []

class AgentOrchestrator:
    def __init__(self, vector_db_client: VectorDBClient, openai_api_key: str):
        self.vector_db_client = vector_db_client
        self.embedding_model = None
        self.agents = {}
        self.tools = {}
        openai.api_key = openai_api_key

    def _get_embedding_model(self):
        if self.embedding_model is None:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        return self.embedding_model

    def register_agent(self, agent: Agent):
        self.agents[agent.name] = agent

    def register_tool(self, tool_name: str, tool_function):
        self.tools[tool_name] = tool_function

    def process_query(self, index_name: str, query: str, agent_name: str):
        with QUERY_PROCESSING_TIME.labels(agent_name=agent_name).time():
            if agent_name not in self.agents:
                raise ValueError(f"Agent '{agent_name}' not found.")

            agent = self.agents[agent_name]
            embedding_model = self._get_embedding_model()
            query_embedding = embedding_model.encode(query)
            search_results = self.vector_db_client.search(index_name, query_embedding)

            context = "\n".join([result['document'] for result in search_results])

            prompt = agent.prompt.format(context=context, query=query)

            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=150
            )

            QUERIES_PROCESSED.labels(agent_name=agent_name).inc()
            return response.choices[0].text.strip()
