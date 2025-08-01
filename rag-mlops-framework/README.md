# Enhanced MLOps Framework for Agentic AI RAG Workflows

This repository contains a comprehensive MLOps framework specifically designed for building, deploying, and managing Agentic AI RAG (Retrieval Augmented Generation) systems on Google Cloud Platform.

## Overview

The Enhanced MLOps Framework for Agentic AI RAG Workflows extends traditional MLOps practices to address the unique challenges of RAG systems, including:

- Vector database management and embedding pipelines
- Agent orchestration with tool selection and reasoning chains
- Real-time serving with streaming responses
- Document processing and chunking strategies
- Compliance and governance for sensitive data
- Evaluation and feedback loops for RAG-specific metrics
- Cost optimization for LLM and embedding operations

## Key Features

- **Modular Architecture**: Plug-and-play components that can be customized for specific use cases
- **Docker-based Local Development**: Run the entire framework locally with Docker Compose
- **GCP Integration**: Seamless deployment to Google Cloud Platform services
- **End-to-End Workflows**: Complete pipelines from document ingestion to agent deployment
- **Compliance-Ready**: Built-in controls for HIPAA, GDPR, and other regulatory requirements
- **Monitoring & Evaluation**: Comprehensive metrics for RAG-specific performance indicators

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Google Cloud SDK (for cloud deployment)

### Quick Start

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/rag-mlops-framework.git
   cd rag-mlops-framework
   ```

2. Start the local development environment:
   ```bash
   docker-compose up
   ```

3. Access the framework UI:
   ```
   http://localhost:8080
   ```

4. Run the sample RAG workflow:
   ```bash
   ./scripts/run_sample_workflow.sh
   ```

## Architecture

The framework consists of several interconnected layers:

1. **Vector Database Integration Layer**: Manages embeddings and vector search
2. **Agent Orchestration Framework**: Coordinates tools, reasoning, and state
3. **Real-Time Serving Infrastructure**: Handles low-latency, streaming responses
4. **Document Processing Pipeline**: Processes and chunks documents for ingestion
5. **Compliance Framework**: Ensures regulatory compliance and data governance
6. **Evaluation System**: Measures and improves RAG performance
7. **Cost Optimization Layer**: Manages resource usage and API costs

## Documentation

- [Architecture Overview](docs/architecture.md)
- [Component Reference](docs/components/README.md)
- [Configuration Guide](docs/configuration.md)
- [Local Development](docs/local_development.md)
- [Cloud Deployment](docs/cloud_deployment.md)
- [Security & Compliance](docs/security_compliance.md)
- [Monitoring & Evaluation](docs/monitoring_evaluation.md)

## Examples

- [Simple Question-Answering System](examples/qa_system/README.md)
- [Document Processing Pipeline](examples/document_processing/README.md)
- [Agent with Tool Usage](examples/agent_with_tools/README.md)
- [Compliance-Focused Healthcare RAG](examples/healthcare_rag/README.md)

## Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for more details.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
