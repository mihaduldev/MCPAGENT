# 🚀 Getting Started with MCP Agent

> **Quick start guide to get you up and running in minutes**

## 📋 Prerequisites

- **Python 3.11+** installed
- **Docker & Docker Compose** (optional, but recommended)
- **PostgreSQL** or use SQLite (included)
- **Redis** (optional, for caching)
- **API Keys** for LLM provider (OpenAI, Anthropic, or Gemini)

---

## ⚡ Quick Start (5 minutes)

### Option 1: Docker (Recommended)

```bash
# 1. Clone or navigate to project
cd MCPAGENT

# 2. Create environment file
cat > .env << 'EOF'
# Required
OPENAI_API_KEY=sk-your-key-here
DATABASE_URL=postgresql://mcpagent:mcpagent_password@postgres:5432/mcpagent
REDIS_URL=redis://redis:6379/0

# Optional
APP_ENV=development
DEBUG=true
EOF

# 3. Start all services
docker-compose up -d

# 4. Check status
docker-compose ps

# 5. View logs
docker-compose logs -f api

# 6. Test the API
curl http://localhost:8000/health
```

**✅ Done!** API is running at http://localhost:8000

---

### Option 2: Local Development

```bash
# 1. Navigate to project
cd MCPAGENT

# 2. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env

# Edit .env and add your API keys:
# - OPENAI_API_KEY
# - DATABASE_URL (or use default SQLite)

# 5. Initialize database
python -m scripts.init_db

# 6. Run the server
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**✅ Done!** API is running at http://localhost:8000

---

## 🧪 Test Your Setup

### 1. Health Check
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "vector_store": "healthy",
    "llm": "configured"
  }
}
```

### 2. API Documentation
Visit: http://localhost:8000/docs

### 3. Simple Chat (TODO: Implement endpoint)
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, who are you?",
    "session_id": "test-session"
  }'
```

---

## 🎮 Using the CLI

### Basic Commands

```bash
# Show version
python -m src.cli.main version

# Check system status
python -m src.cli.main status

# Interactive chat
python -m src.cli.main chat --interactive

# Single query
python -m src.cli.main chat --query "What is AI?"

# Ingest documents
python -m src.cli.main ingest /path/to/documents --recursive
```

---

## 📚 Next Steps

### 1. Configure Your LLM

Edit `.env` file:

```env
# Choose your LLM provider
LLM_PROVIDER=openai  # or anthropic, gemini, ollama, groq

# OpenAI
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4-turbo-preview

# Or Anthropic
ANTHROPIC_API_KEY=sk-ant-your-key
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Or Gemini
GOOGLE_API_KEY=your-key
GEMINI_MODEL=gemini-1.5-pro

# Or Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### 2. Add Documents to Knowledge Base

```bash
# Via CLI
python -m src.cli.main ingest ./docs --recursive

# Or via API
curl -X POST http://localhost:8000/api/v1/documents \
  -F "file=@document.pdf"
```

### 3. Configure Vector Store

```env
# ChromaDB (default, persistent)
VECTOR_STORE_TYPE=chromadb
VECTOR_STORE_PATH=./data/vector_store

# Or FAISS (in-memory, fast)
VECTOR_STORE_TYPE=faiss
```

### 4. Enable Monitoring

```env
# Enable Prometheus metrics
ENABLE_METRICS=true
METRICS_PORT=9090

# Access metrics at:
# http://localhost:9090/metrics
```

### 5. Start with Monitoring Stack

```bash
# Start with Prometheus + Grafana
docker-compose --profile monitoring up -d

# Access:
# - Prometheus: http://localhost:9091
# - Grafana: http://localhost:3001 (admin/admin)
```

---

## 🔧 Configuration Guide

### Essential Settings

```env
# Application
APP_NAME=MCP Agent
APP_ENV=development  # development, staging, production
DEBUG=true
LOG_LEVEL=INFO

# API
API_HOST=0.0.0.0
API_PORT=8000
API_SECRET_KEY=change-this-secret-key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mcpagent
# Or SQLite:
# DATABASE_URL=sqlite:///./data/mcpagent.db

# Cache (optional)
REDIS_URL=redis://localhost:6379/0
ENABLE_CACHE=true

# RAG
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVAL_K=5
ENABLE_RERANKING=true

# Security
JWT_SECRET_KEY=your-jwt-secret
ENABLE_RATE_LIMITING=true
RATE_LIMIT_PER_MINUTE=60
```

---

## 🐛 Troubleshooting

### Issue: "Database connection failed"

**Solution:**
```bash
# Check DATABASE_URL in .env
# For SQLite (simplest):
DATABASE_URL=sqlite:///./data/mcpagent.db

# For PostgreSQL:
DATABASE_URL=postgresql://user:password@localhost:5432/mcpagent

# Initialize database
python -m scripts.init_db
```

### Issue: "LLM not configured"

**Solution:**
```bash
# Add API key to .env
OPENAI_API_KEY=sk-your-key-here

# Or use local Ollama
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

### Issue: "Redis connection failed"

**Solution:**
```bash
# Option 1: Start Redis with Docker
docker run -d -p 6379:6379 redis:7-alpine

# Option 2: Disable caching
ENABLE_CACHE=false
```

### Issue: "Vector store error"

**Solution:**
```bash
# Ensure directory exists
mkdir -p data/vector_store

# Or use FAISS (in-memory)
VECTOR_STORE_TYPE=faiss
```

### Issue: "Port already in use"

**Solution:**
```bash
# Change port in .env
API_PORT=8001

# Or kill process using port
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9
```

---

## 📖 Learning Resources

### Documentation
- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture
- [COMPARISON.md](docs/COMPARISON.md) - vs RAG-MCP
- [API Documentation](http://localhost:8000/docs) - Interactive API docs

### Examples
- `examples/` - Code examples
- `tests/` - Test examples

---

## 🎯 Common Use Cases

### 1. Build a Knowledge Base Chatbot

```bash
# 1. Add your documents
python -m src.cli.main ingest ./company-docs --recursive

# 2. Query via CLI
python -m src.cli.main chat --interactive --mode rag

# 3. Or use API
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is our return policy?", "mode": "rag"}'
```

### 2. Multi-Agent System

```bash
# Configure specialized agents
# Edit src/core/agent/multi_agent.py

# Use via API
curl -X POST http://localhost:8000/api/v1/chat \
  -d '{"message": "Analyze this data", "agent_type": "data_analysis"}'
```

### 3. Production Deployment

```bash
# 1. Set production environment
APP_ENV=production
DEBUG=false

# 2. Use strong secrets
API_SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# 3. Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# 4. Setup reverse proxy (Nginx/Traefik)
# 5. Enable HTTPS
# 6. Configure monitoring
```

---

## ✅ Success Checklist

After setup, verify:

- [ ] Health check returns "healthy"
- [ ] API docs accessible at /docs
- [ ] Database connection working
- [ ] Vector store initialized
- [ ] LLM configured and responding
- [ ] Cache working (if enabled)
- [ ] CLI commands work
- [ ] Can ingest documents
- [ ] Can query knowledge base
- [ ] Metrics endpoint available

---

## 🆘 Getting Help

- **Documentation**: Check `/docs` folder
- **API Docs**: http://localhost:8000/docs
- **Examples**: See `examples/` directory
- **Issues**: Create an issue on GitHub
- **Logs**: Check `logs/mcpagent.log`

---

## 🎉 You're Ready!

You now have a production-ready AI agent system running!

**Next Steps:**
1. Add your documents to build a knowledge base
2. Customize agents for your use case
3. Integrate with your application
4. Deploy to production

Happy building! 🚀

