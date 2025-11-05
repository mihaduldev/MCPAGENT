# 🏗️ MCP Agent - System Architecture

> **Comprehensive architecture documentation for the MCP Agent system**

## Table of Contents
- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Component Design](#component-design)
- [Data Flow](#data-flow)
- [Technology Stack](#technology-stack)
- [Design Patterns](#design-patterns)
- [Scalability](#scalability)

---

## Overview

MCP Agent is a production-grade AI agent system built with enterprise patterns and best practices. The architecture is designed for:

- **Modularity**: Clear separation of concerns with layered architecture
- **Scalability**: Horizontal scaling support with stateless design
- **Maintainability**: Clean code structure and comprehensive testing
- **Extensibility**: Plugin architecture for tools and agents
- **Observability**: Built-in monitoring, logging, and tracing

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Presentation Layer                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │  Web UI    │  │    CLI     │  │  REST API  │  │  Webhooks  │   │
│  │  (React)   │  │  (Typer)   │  │ (FastAPI)  │  │            │   │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘   │
└────────┼────────────────┼────────────────┼────────────────┼─────────┘
         │                │                │                │
         └────────────────┴────────────────┴────────────────┘
                                  │
┌─────────────────────────────────┴─────────────────────────────────────┐
│                        Application Layer (API)                         │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │              Middleware & Security                            │    │
│  │  • Authentication (JWT, API Keys)                            │    │
│  │  • Authorization (RBAC)                                      │    │
│  │  • Rate Limiting                                             │    │
│  │  • Request Validation                                        │    │
│  │  • Error Handling                                            │    │
│  └──────────────────────────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │                 API Endpoints (v1)                           │    │
│  │  /chat  /documents  /agents  /users  /tools  /sessions      │    │
│  └────────────────────────┬─────────────────────────────────────┘    │
└───────────────────────────┼───────────────────────────────────────────┘
                            │
┌───────────────────────────┴───────────────────────────────────────────┐
│                        Service Layer                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐   │
│  │  Chat       │  │  Document   │  │  Agent      │  │   User   │   │
│  │  Service    │  │  Service    │  │  Service    │  │  Service │   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └────┬─────┘   │
└─────────┼─────────────────┼─────────────────┼──────────────┼─────────┘
          │                 │                 │              │
┌─────────┴─────────────────┴─────────────────┴──────────────┴─────────┐
│                          Core Layer                                    │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │                 Multi-Agent Orchestrator                       │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │   │
│  │  │   Research   │  │    Coding    │  │     Data     │       │   │
│  │  │    Agent     │  │    Agent     │  │   Analysis   │       │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘       │   │
│  └────────────────────────────┬──────────────────────────────────┘   │
│  ┌────────────────────────────┴──────────────────────────────────┐   │
│  │                    RAG System                                  │   │
│  │  • Vector Store (ChromaDB)                                    │   │
│  │  • Embeddings (OpenAI)                                        │   │
│  │  • Hybrid Search (Semantic + Keyword)                         │   │
│  │  • Reranking (Cross-encoder)                                  │   │
│  │  • History-Aware Retrieval                                    │   │
│  └────────────────────────────┬──────────────────────────────────┘   │
│  ┌────────────────────────────┴──────────────────────────────────┐   │
│  │                    MCP Client                                  │   │
│  │  • Tool Discovery                                             │   │
│  │  • Tool Execution                                             │   │
│  │  • Connection Management                                      │   │
│  └────────────────────────────┬──────────────────────────────────┘   │
└─────────────────────────────┬─┴───────────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────────────────┐
│                     Infrastructure Layer                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │  PostgreSQL  │  │    Redis     │  │   ChromaDB   │  │   LLM    │  │
│  │  (Database)  │  │   (Cache)    │  │   (Vector)   │  │ Providers│  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. **Configuration Layer** (`src/config/`)

**Responsibilities:**
- Application settings management
- Environment variable loading
- Validation of configuration
- Structured logging setup

**Key Components:**
- `settings.py`: Pydantic-based settings with validation
- `logging.py`: Structured JSON logging configuration

**Design Patterns:**
- **Singleton**: Single settings instance
- **Factory**: Logger creation

---

### 2. **Infrastructure Layer** (`src/infrastructure/`)

**Responsibilities:**
- Database management (PostgreSQL/SQLite)
- Caching (Redis)
- Vector store (ChromaDB)
- LLM provider abstraction

**Key Components:**

#### Database (`database/`)
- `base.py`: SQLAlchemy setup and session management
- `models.py`: ORM models (User, Conversation, Message, Document)
- Migrations with Alembic

#### Cache (`cache/`)
- `redis_cache.py`: Redis caching layer with fallback

#### Vector Store (`vector_store/`)
- ChromaDB integration
- FAISS fallback option

#### LLM (`llm/`)
- `llm_factory.py`: Multi-provider LLM factory
- Support for OpenAI, Anthropic, Gemini, Ollama, Groq

**Design Patterns:**
- **Repository Pattern**: Database access abstraction
- **Factory Pattern**: LLM instance creation
- **Dependency Injection**: Database sessions

---

### 3. **Core Layer** (`src/core/`)

**Responsibilities:**
- Business logic
- Agent orchestration
- RAG system
- MCP integration
- Memory management

**Key Components:**

#### RAG System (`rag/`)
```python
EnhancedRAGSystem:
  • Document ingestion pipeline
  • Persistent vector storage
  • Hybrid search (semantic + keyword)
  • Reranking for better results
  • History-aware retrieval
```

#### Multi-Agent (`agent/`)
```python
MultiAgentOrchestrator:
  • Agent registration and routing
  • Specialized agents (Research, Coding, Data Analysis)
  • Tool management per agent
  • Query routing logic
```

#### MCP Client (`mcp/`)
```python
MCPClient:
  • Dynamic tool discovery
  • Remote tool execution
  • Connection pooling
  • Error handling and retries
```

**Design Patterns:**
- **Strategy Pattern**: Agent selection
- **Observer Pattern**: Event handling
- **Chain of Responsibility**: Tool execution

---

### 4. **Service Layer** (`src/services/`)

**Responsibilities:**
- Business workflows
- Transaction management
- Cross-cutting concerns
- External integrations

**Key Services:**
- `chat_service.py`: Chat orchestration
- `rag_service.py`: RAG operations
- `auth_service.py`: Authentication and authorization
- `mcp_service.py`: MCP server management

**Design Patterns:**
- **Facade Pattern**: Simplified interfaces
- **Transaction Script**: Business workflows

---

### 5. **API Layer** (`src/api/`)

**Responsibilities:**
- HTTP endpoint exposure
- Request/response handling
- Authentication/authorization
- API versioning

**Structure:**
```
api/
├── v1/
│   ├── endpoints/
│   │   ├── chat.py
│   │   ├── documents.py
│   │   ├── agents.py
│   │   └── users.py
│   ├── models/
│   │   ├── requests.py
│   │   └── responses.py
│   └── dependencies/
│       ├── auth.py
│       └── rate_limit.py
├── middleware/
│   ├── auth.py
│   ├── logging.py
│   └── error_handler.py
└── main.py
```

**Design Patterns:**
- **Dependency Injection**: FastAPI dependencies
- **Decorator Pattern**: Middleware
- **Builder Pattern**: Response construction

---

## Data Flow

### Chat Request Flow

```
1. Client Request
   ↓
2. Middleware Pipeline
   • Authentication
   • Rate Limiting
   • Request Validation
   ↓
3. API Endpoint
   • Parse request
   • Extract parameters
   ↓
4. Service Layer
   • Load session history from DB
   • Get cached response (if available)
   ↓
5. Core Layer
   • RAG: Retrieve relevant context
   • Agent: Select appropriate agent
   • MCP: Load required tools
   ↓
6. LLM Provider
   • Stream response
   • Track tokens/cost
   ↓
7. Service Layer
   • Save conversation to DB
   • Cache response
   • Update metrics
   ↓
8. API Response
   • Format response
   • Stream to client
```

### Document Ingestion Flow

```
1. Document Upload
   ↓
2. Validation
   • File type check
   • Size limits
   • Content scan
   ↓
3. Storage
   • Save to filesystem
   • Create DB record
   ↓
4. Processing
   • Extract text
   • Split into chunks
   • Generate metadata
   ↓
5. Embedding
   • Generate embeddings
   • Store in vector DB
   ↓
6. Indexing
   • Update search index
   • Cache invalidation
   ↓
7. Notification
   • Update status
   • Trigger webhooks
```

---

## Technology Stack

### Backend
- **Framework**: FastAPI 0.111+
- **Language**: Python 3.11+
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic

### Database
- **Primary**: PostgreSQL 16
- **Cache**: Redis 7
- **Vector**: ChromaDB 0.4+

### AI/ML
- **Orchestration**: LangChain + LangGraph
- **LLMs**: OpenAI, Anthropic, Gemini, Ollama
- **Embeddings**: OpenAI text-embedding-3-small
- **Vector Search**: FAISS, ChromaDB

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Orchestration**: Kubernetes (optional)
- **Monitoring**: Prometheus + Grafana
- **Logging**: Structured JSON logs
- **Tracing**: OpenTelemetry (optional)

---

## Design Patterns

### 1. **Layered Architecture**
- Clear separation of concerns
- Dependency flow: API → Service → Core → Infrastructure

### 2. **Repository Pattern**
- Abstract database operations
- Testable data access layer

### 3. **Factory Pattern**
- LLM creation
- Agent instantiation
- Tool loading

### 4. **Strategy Pattern**
- Agent selection
- LLM provider selection
- Search strategy (hybrid, semantic, keyword)

### 5. **Dependency Injection**
- FastAPI dependencies
- Database sessions
- Configuration

### 6. **Observer Pattern**
- Event-driven updates
- Metrics collection
- Webhooks

---

## Scalability

### Horizontal Scaling

```
┌─────────────────┐
│   Load Balancer │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───┐
│ API  │  │ API  │  ← Multiple instances
│ Node │  │ Node │
└───┬──┘  └──┬───┘
    │         │
    └────┬────┘
         │
    ┌────▼────────────┐
    │  Shared Storage │
    │  • PostgreSQL   │
    │  • Redis        │
    │  • ChromaDB     │
    └─────────────────┘
```

### Performance Optimization

1. **Caching Strategy**
   - Response caching (Redis)
   - Embedding caching
   - Session caching

2. **Database Optimization**
   - Connection pooling
   - Query optimization
   - Proper indexing

3. **Async Processing**
   - Background tasks (Celery)
   - Async I/O (asyncio)
   - Streaming responses

4. **Resource Management**
   - Rate limiting
   - Connection pooling
   - Circuit breakers

---

## Security

### Authentication & Authorization
- JWT tokens
- API keys
- Role-based access control (RBAC)

### Data Protection
- Encryption at rest
- Encryption in transit (TLS)
- Secure secret management

### Input Validation
- Pydantic models
- SQL injection prevention
- XSS protection

---

## Monitoring & Observability

### Metrics (Prometheus)
- Request count & latency
- Token usage & cost
- Cache hit rate
- Error rates

### Logging
- Structured JSON logs
- Log levels: DEBUG, INFO, WARNING, ERROR
- Correlation IDs for tracing

### Tracing (OpenTelemetry)
- Distributed tracing
- Performance profiling
- Dependency mapping

---

## Deployment

### Development
```bash
python -m uvicorn src.api.main:app --reload
```

### Docker
```bash
docker-compose up -d
```

### Kubernetes
```bash
kubectl apply -f deployment/kubernetes/
```

---

## Future Enhancements

1. **Advanced RAG**
   - Multi-hop reasoning
   - Graph-based retrieval
   - Adaptive retrieval

2. **Agent Capabilities**
   - Code execution sandbox
   - Tool creation
   - Self-improvement loop

3. **Scalability**
   - Message queue (RabbitMQ/Kafka)
   - Distributed caching
   - CDN integration

4. **Observability**
   - APM integration
   - Real-time dashboards
   - Anomaly detection

---

**Last Updated**: 2025-01-05  
**Version**: 1.0.0

