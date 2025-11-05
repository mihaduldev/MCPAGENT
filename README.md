# 🤖 MCP Agent - Production-Grade AI Agent System

> **A sophisticated, enterprise-ready AI agent platform combining RAG, multi-agent orchestration, persistent memory, and extensible tool integration via Model Context Protocol (MCP).**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)

## 🌟 Key Features

### Core Capabilities
- ✅ **Advanced RAG System** - Persistent vector storage with ChromaDB, hybrid search, reranking
- ✅ **Multi-Agent Orchestration** - Specialized agents for different domains (research, coding, data analysis)
- ✅ **Persistent Memory** - PostgreSQL/SQLite for conversation history and user preferences
- ✅ **MCP Tool Integration** - Dynamic tool loading from local and remote MCP servers
- ✅ **Authentication & Authorization** - JWT-based auth with role-based access control
- ✅ **Caching Layer** - Redis for response caching and session management
- ✅ **Monitoring & Observability** - Prometheus metrics, structured logging, tracing
- ✅ **Streaming Responses** - Real-time SSE streaming with progress indicators
- ✅ **Document Processing** - PDF, DOCX, TXT ingestion into knowledge base
- ✅ **Multi-LLM Support** - OpenAI, Anthropic, Gemini, Ollama, Groq
- ✅ **Web UI** - Modern React frontend with real-time chat
- ✅ **CLI Tool** - Rich interactive CLI with syntax highlighting

### Professional Features
- 🔐 **Security**: API key auth, rate limiting, input validation, CORS configuration
- 📊 **Monitoring**: Health checks, metrics, logging, error tracking
- 🗃️ **Persistence**: Database for history, vector store for embeddings, cache for performance
- 🧪 **Testing**: Unit tests, integration tests, E2E tests
- 📚 **Documentation**: API docs, architecture diagrams, deployment guides
- 🐳 **Deployment**: Docker, docker-compose, Kubernetes manifests
- 🔄 **CI/CD**: GitHub Actions for testing, building, deployment

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (optional)
- PostgreSQL (or use SQLite)
- Redis (optional, for caching)

### Installation

```bash
# Clone the repository
cd MCPAGENT

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup configuration
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python -m scripts.init_db

# Run the application
python -m src.main
```

### Using Docker

```bash
# Start all services (API, DB, Redis, UI)
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Quick API Test

```bash
# Check health
curl http://localhost:8000/health

# Chat (with authentication)
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is artificial intelligence?", "session_id": "test"}'
```

## 📁 Project Structure

```
MCPAGENT/
├── src/
│   ├── api/                    # FastAPI application
│   │   ├── v1/                # API version 1
│   │   │   ├── endpoints/     # API endpoints
│   │   │   ├── models/        # Pydantic models
│   │   │   └── dependencies/  # Dependency injection
│   │   ├── middleware/        # Custom middleware
│   │   └── main.py           # API entry point
│   ├── core/                  # Core business logic
│   │   ├── agent/            # Agent orchestration
│   │   ├── rag/              # RAG system
│   │   ├── mcp/              # MCP client
│   │   ├── memory/           # Conversation memory
│   │   └── tools/            # Custom tools
│   ├── infrastructure/        # Infrastructure layer
│   │   ├── database/         # Database models & repositories
│   │   ├── cache/            # Redis cache
│   │   ├── vector_store/     # ChromaDB integration
│   │   └── llm/              # LLM providers
│   ├── services/              # Business services
│   │   ├── auth_service.py   # Authentication
│   │   ├── chat_service.py   # Chat orchestration
│   │   ├── rag_service.py    # RAG operations
│   │   └── mcp_service.py    # MCP management
│   ├── cli/                   # CLI application
│   │   ├── commands/         # CLI commands
│   │   └── main.py           # CLI entry point
│   ├── web/                   # Web UI (React)
│   │   ├── src/
│   │   ├── public/
│   │   └── package.json
│   ├── config/                # Configuration
│   │   ├── settings.py       # Settings management
│   │   ├── logging.py        # Logging config
│   │   └── security.py       # Security config
│   └── utils/                 # Utilities
│       ├── logger.py         # Logging utilities
│       ├── metrics.py        # Prometheus metrics
│       └── validators.py     # Input validators
├── mcp_servers/               # Local MCP servers
│   ├── math_server/
│   ├── weather_server/
│   ├── web_server/
│   └── database_server/
├── tests/                     # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── e2e/                  # End-to-end tests
├── scripts/                   # Utility scripts
│   ├── init_db.py           # Initialize database
│   ├── seed_data.py         # Seed test data
│   └── benchmark.py         # Performance benchmarks
├── docs/                      # Documentation
│   ├── architecture.md       # System architecture
│   ├── api.md               # API documentation
│   ├── deployment.md        # Deployment guide
│   └── development.md       # Development guide
├── deployment/               # Deployment configs
│   ├── docker/              # Docker configs
│   ├── kubernetes/          # K8s manifests
│   └── terraform/           # Infrastructure as code
├── .github/                  # GitHub configs
│   └── workflows/           # CI/CD workflows
├── requirements.txt          # Python dependencies
├── requirements-dev.txt      # Development dependencies
├── docker-compose.yml        # Docker Compose config
├── Dockerfile                # Docker image
├── pytest.ini                # Pytest configuration
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                         Clients                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Web UI   │  │   CLI    │  │   API    │  │  Mobile  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │      FastAPI Application          │
        │  ┌──────────────────────────┐    │
        │  │  Authentication Layer    │    │
        │  │  (JWT, API Keys)         │    │
        │  └────────────┬─────────────┘    │
        │               │                   │
        │  ┌────────────┴─────────────┐    │
        │  │   API Endpoints (v1)     │    │
        │  │  /chat, /docs, /agents   │    │
        │  └────────────┬─────────────┘    │
        └───────────────┼──────────────────┘
                        │
        ┌───────────────┴──────────────────┐
        │      Services Layer              │
        │  ┌─────────┐  ┌─────────┐       │
        │  │  Chat   │  │   RAG   │       │
        │  │ Service │  │ Service │       │
        │  └────┬────┘  └────┬────┘       │
        └───────┼────────────┼─────────────┘
                │            │
        ┌───────┴────────────┴─────────────┐
        │       Core Layer                  │
        │  ┌─────────────────────────┐     │
        │  │   Agent Orchestrator    │     │
        │  │  ┌────────┬────────┐    │     │
        │  │  │Research│Coding │    │     │
        │  │  │ Agent  │Agent  │    │     │
        │  │  └────────┴────────┘    │     │
        │  └──────────┬──────────────┘     │
        │             │                     │
        │  ┌──────────┴──────────────┐     │
        │  │     RAG System          │     │
        │  │  • Retrieval            │     │
        │  │  • Reranking            │     │
        │  │  • Context injection    │     │
        │  └──────────┬──────────────┘     │
        │             │                     │
        │  ┌──────────┴──────────────┐     │
        │  │    MCP Client           │     │
        │  │  • Tool discovery       │     │
        │  │  • Tool execution       │     │
        │  └──────────┬──────────────┘     │
        └─────────────┼────────────────────┘
                      │
        ┌─────────────┴────────────────────┐
        │   Infrastructure Layer            │
        │  ┌─────────┐  ┌─────────┐        │
        │  │  Redis  │  │ Postgres│        │
        │  │  Cache  │  │  (DB)   │        │
        │  └─────────┘  └─────────┘        │
        │  ┌─────────┐  ┌─────────┐        │
        │  │ChromaDB │  │   LLM   │        │
        │  │(Vector) │  │Providers│        │
        │  └─────────┘  └─────────┘        │
        └──────────────────────────────────┘
```

## 🎯 Use Cases

### 1. **Enterprise Knowledge Base**
```bash
# Ingest company documents
python -m src.cli ingest --directory /path/to/docs

# Query knowledge base
python -m src.cli chat --query "What is our vacation policy?"
```

### 2. **Multi-Agent Task Execution**
```bash
# Complex task with multiple agents
python -m src.cli execute --task "Research latest AI trends, summarize findings, and create a presentation outline"
```

### 3. **API Integration**
```python
import httpx

response = httpx.post(
    "http://localhost:8000/api/v1/chat",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={
        "message": "Analyze this sales data",
        "session_id": "user_123",
        "mode": "agent"
    }
)
```

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```env
# Application
APP_NAME=MCP Agent
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=your-secret-key-change-this
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mcpagent
# Or SQLite: DATABASE_URL=sqlite:///./data/mcpagent.db

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
ENABLE_CACHE=true

# Vector Store
VECTOR_STORE_TYPE=chromadb  # or faiss, pinecone
CHROMA_HOST=localhost
CHROMA_PORT=8001

# LLM
LLM_PROVIDER=openai  # openai, anthropic, gemini, ollama, groq
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# RAG
EMBEDDING_MODEL=text-embedding-3-small
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVAL_K=5

# MCP
MCP_SERVER_TIMEOUT=30
MCP_RETRY_ATTEMPTS=3

# Security
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
ENABLE_TRACING=false
```

## 📚 API Documentation

Once running, visit:
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Metrics**: http://localhost:9090/metrics

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with verbose output
pytest -v -s
```

## 📈 Monitoring

### Metrics Available
- Request count & latency
- Token usage & cost
- Cache hit rate
- Agent execution time
- Error rates
- Active sessions

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "vector_store": "healthy",
    "llm": "healthy"
  },
  "uptime": 3600.5
}
```

## 🎨 Features Comparison

| Feature | RAG-MCP | MCP Agent (This) |
|---------|---------|------------------|
| **Vector Store** | FAISS (in-memory) | ChromaDB (persistent) |
| **Database** | None | PostgreSQL/SQLite |
| **Cache** | None | Redis |
| **Authentication** | None | JWT + API Keys |
| **Multi-Agent** | Single agent | Multiple specialized agents |
| **Monitoring** | Basic | Prometheus + Grafana |
| **Testing** | None | Comprehensive test suite |
| **Document Ingestion** | Manual | Automated pipeline |
| **Rate Limiting** | None | Token bucket algorithm |
| **Reranking** | None | Cross-encoder reranking |
| **Hybrid Search** | Semantic only | Semantic + keyword |
| **UI** | None | React web app |
| **CLI** | Basic | Rich interactive CLI |

## 🚢 Deployment

### Docker
```bash
docker-compose up -d
```

### Kubernetes
```bash
kubectl apply -f deployment/kubernetes/
```

### Cloud Platforms
- **AWS**: See `docs/deployment/aws.md`
- **GCP**: See `docs/deployment/gcp.md`
- **Azure**: See `docs/deployment/azure.md`

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/)
- Inspired by [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT)
- MCP protocol by [Anthropic](https://www.anthropic.com/)

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/mcpagent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mcpagent/discussions)

---

**Made with ❤️ for building production-grade AI agents**

