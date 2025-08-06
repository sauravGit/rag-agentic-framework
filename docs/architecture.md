# Architecture

This framework is designed as a set of microservices that work together to provide a robust and scalable platform for Agentic AI RAG workflows. Each service is responsible for a specific part of the workflow, and they communicate with each other over a network.

## Services

The framework is composed of the following services:

-   **API Gateway**: The single entry point for all requests. It routes requests to the appropriate backend service.
-   **Agent Orchestrator**: Manages and coordinates AI agents, tools, and workflows.
-   **Document Processor**: Handles document ingestion, chunking, embedding generation, and metadata extraction.
-   **Compliance Service**: Ensures compliance with regulations like HIPAA and handles PII detection.
-   **Evaluation Service**: Evaluates the performance of the RAG system, including relevance, faithfulness, and answer quality.
-   **Monitoring Service**: Monitors the health and performance of the framework, including metrics collection, logging, and alerting.
-   **Cost Optimization Service**: Optimizes the cost of RAG workflows by managing model selection, caching, and resource utilization.
-   **Vector Database**: Stores and retrieves vector embeddings of the documents. We use Elasticsearch for this.
-   **Web UI**: A React-based user interface for interacting with the framework.

## Communication

The services communicate with each other using REST APIs. The `API Gateway` is the only service that is exposed to the public internet. All other services are only accessible within the internal network.

## Data Flow

A typical query would flow through the system as follows:

1.  A user sends a query to the **Web UI**.
2.  The **Web UI** sends the query to the **API Gateway**.
3.  The **API Gateway** forwards the query to the **Agent Orchestrator**.
4.  The **Agent Orchestrator** might first send the query to the **Cost Optimization Service** to get recommendations on which models to use.
5.  The **Agent Orchestrator** then sends the query to the **Document Processor** to retrieve relevant documents from the **Vector Database**.
6.  The **Agent Orchestrator** uses the retrieved documents and the user's query to generate a response using an LLM.
7.  Before returning the response to the user, the **Agent Orchestrator** sends it to the **Compliance Service** to check for any sensitive information.
8.  The **Agent Orchestrator** also sends the response to the **Evaluation Service** to evaluate its quality.
9.  Finally, the **Agent Orchestrator** returns the response to the **API Gateway**, which forwards it to the **Web UI**.

Throughout this process, all services send metrics to the **Monitoring Service**, which can be used to track the health and performance of the system.
