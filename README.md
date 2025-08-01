# Enhanced MLOps Framework for Agentic AI RAG Workflows

A comprehensive framework for building, deploying, and managing Agentic AI Retrieval-Augmented Generation (RAG) workflows on Google Cloud Platform, with a focus on medical customer support applications.

## Overview

This framework provides a complete end-to-end solution for implementing production-grade RAG systems with agentic capabilities. It addresses the unique challenges of retrieval-augmented generation workflows, including vector database management, agent orchestration, document processing, compliance, evaluation, and cost optimization.

The framework is built on Google Cloud Platform and leverages key agent technologies:
- Agent Development Kit (ADK) for building multi-agent systems
- Google Agentspace for agent discovery and governance

## Key Features

- **Vector Database Integration**: Efficient storage, indexing, and retrieval of medical knowledge embeddings
- **Agent Orchestration**: Coordinating tools, reasoning chains, and stateful interactions for medical support
- **Document Processing**: Chunking, embedding, and indexing medical documents effectively
- **Compliance Framework**: HIPAA-compliant handling of sensitive medical information
- **Real-time Serving**: Low-latency, high-throughput serving with streaming responses
- **Cost Optimization**: Managing the significant costs of LLM API calls and embedding generation
- **React-based UI**: Modern, responsive interface for medical support agents
- **Monitoring & Governance**: Comprehensive dashboards for system oversight

## Architecture

The framework consists of several interconnected layers, each addressing specific aspects of RAG system development and deployment. See the [Architecture Documentation](docs/architecture.md) for detailed diagrams and explanations.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Google Cloud SDK
- Node.js and npm (for UI development)
- Python 3.9+

### Local Development

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/enhanced-rag-framework.git
   cd enhanced-rag-framework
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Start the services:
   ```bash
   docker-compose up
   ```

4. Access the UI at http://localhost:3000

### GCP Deployment

See the [Deployment Guide](docs/deployment.md) for detailed instructions on deploying to Google Cloud Platform.

## Documentation

- [Architecture](docs/architecture.md)
- [Configuration Layer](docs/components/configuration_layer.md)
- [Execution Engine](docs/components/execution_engine.md)
- [Validation Layer](docs/components/validation_layer.md)
- [Governance Layer](docs/components/governance_layer.md)
- [Infrastructure Components](docs/components/infrastructure_components.md)
- [Developer Experience](docs/components/developer_experience.md)
- [Deployment Guide](docs/deployment.md)
- [CLI and SDK Usage](docs/cli_sdk_usage.md)
- [Monitoring and Logging](docs/monitoring.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Google Cloud Platform for providing the infrastructure and agent technologies
- The open-source community for their invaluable contributions
