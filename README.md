# MCP Agent

Production-grade AI Agent System with RAG, Multi-Agent Orchestration, and MCP Integration.

## Quick Start

### 1. Setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your API keys
```

### 2. Run

```bash
# Start the API server
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Or use Docker
docker-compose up -d
```

### 3. Test

```bash
# Health check
curl http://localhost:8000/health

# API docs
# Open: http://localhost:8000/docs
```

## Features

- ✅ **RAG System** - Persistent vector store with ChromaDB
- ✅ **Multi-Agent** - Specialized agents (Research, Coding, Data Analysis)
- ✅ **MCP Integration** - Connect to MCP servers for tools
- ✅ **FastAPI** - Production-ready REST API
- ✅ **Database** - PostgreSQL/SQLite support
- ✅ **Caching** - Redis for performance
- ✅ **CLI** - Rich command-line interface

## API Endpoints

- `GET /health` - Health check
- `POST /api/v1/chat` - Chat with AI agent
- `GET /api/v1/sessions` - List sessions

## Configuration

### Option 1: With Docker Services (Recommended)

1. **Start PostgreSQL & Redis:**
   ```bash
   start_services.bat
   # Or: docker-compose -f docker-compose.services.yml up -d
   ```

2. **Create `.env` file:**
   ```env
   # LLM Provider (Required)
   OPENAI_API_KEY=your-key-here
   
   # Database - Docker PostgreSQL
   DATABASE_URL=postgresql://mcpagent:mcpagent_password@localhost:5432/mcpagent
   
   # Redis - Docker Redis
   REDIS_URL=redis://localhost:6379/0
   ENABLE_CACHE=true
   ```

### Option 2: SQLite Only (No Docker)

```env
# LLM Provider
OPENAI_API_KEY=your-key-here

# Database - SQLite
DATABASE_URL=sqlite:///./data/mcpagent.db

# Redis - Disabled
ENABLE_CACHE=false
```

## MCP Integration

Configure MCP servers in `config/mcp_servers.json`:

```json
[
  {
    "name": "math",
    "url": "http://localhost:8001/api/mcp/math/mcp",
    "enabled": true
  }
]
```

## Project Structure

```
MCPAGENT/
├── src/
│   ├── api/              # FastAPI application
│   ├── core/             # Core logic (agents, RAG, MCP)
│   ├── infrastructure/   # Database, cache, LLM
│   ├── config/           # Configuration
│   └── utils/            # Utilities
├── config/               # Configuration files
├── requirements.txt      # Dependencies
└── docker-compose.yml    # Docker setup
```

## License

MIT

