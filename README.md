# Enhanced MLOps Framework for Agentic AI RAG Workflows

A comprehensive framework for building, deploying, and managing Agentic AI Retrieval-Augmented Generation (RAG) workflows on Google Cloud Platform, with a focus on medical customer support applications.

## Overview

This framework provides a complete end-to-end solution for implementing production-grade RAG systems with agentic capabilities. It is designed as a set of microservices that work together to provide a robust and scalable platform.

The framework is built on Google Cloud Platform and leverages key agent technologies:
- Agent Development Kit (ADK) for building multi-agent systems
- Google Agentspace for agent discovery and governance

## Key Features

- **Microservices Architecture**: Each component of the framework is a separate service, allowing for independent development, deployment, and scaling.
- **Vector Database Integration**: Efficient storage, indexing, and retrieval of medical knowledge embeddings.
- **Agent Orchestration**: Coordinating tools, reasoning chains, and stateful interactions for medical support.
- **Document Processing**: Chunking, embedding, and indexing medical documents effectively.
- **Compliance Framework**: HIPAA-compliant handling of sensitive medical information.
- **Real-time Serving**: Low-latency, high-throughput serving with streaming responses.
- **Cost Optimization**: Managing the significant costs of LLM API calls and embedding generation.
- **React-based UI**: Modern, responsive interface for medical support agents.
- **Monitoring & Governance**: Comprehensive dashboards for system oversight.

## Architecture

The framework is composed of a set of interconnected microservices. The `API Gateway` serves as the single entry point for all requests, and it routes them to the appropriate backend service. The services communicate with each other over a network, making the system scalable and resilient.

See the [Architecture Documentation](docs/architecture.md) for a more detailed diagram and explanation of the architecture.

## Running the Framework

### Prerequisites

- Docker and Docker Compose
- Google Cloud SDK (optional, for GCP deployment)
- Python 3.9+

### Local Development

1.  Clone this repository:
    ```bash
    git clone https://github.com/yourusername/enhanced-rag-framework.git
    cd enhanced-rag-framework
    ```

2.  Start all the services using Docker Compose:
    ```bash
    docker-compose up --build
    ```

3.  The services will be available at the following ports:
    -   **API Gateway**: http://localhost:8000
    -   **Web UI**: http://localhost:3000

## Documentation

- [Architecture](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
