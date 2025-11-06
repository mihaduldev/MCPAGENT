# 🐳 Docker Services Setup Guide

## Quick Start - PostgreSQL + Redis

This guide helps you run PostgreSQL and Redis in Docker while running your Python app locally.

---

## 🚀 Start Services

### Option 1: Services Only (Recommended for Development)

```bash
# Start PostgreSQL and Redis only
docker-compose -f docker-compose.services.yml up -d

# Check status
docker-compose -f docker-compose.services.yml ps

# View logs
docker-compose -f docker-compose.services.yml logs -f
```

### Option 2: Full Stack (Everything in Docker)

```bash
# Start all services including API
docker-compose up -d

# Check status
docker-compose ps

# View API logs
docker-compose logs -f api
```

---

## 📝 Configure Your Project

### 1. Update `.env` File

Create or update `.env` in your project root:

```env
# Database - Connect to Docker PostgreSQL
DATABASE_URL=postgresql://mcpagent:mcpagent_password@localhost:5432/mcpagent

# Redis - Connect to Docker Redis
REDIS_URL=redis://localhost:6379/0
ENABLE_CACHE=true

# LLM (Required)
OPENAI_API_KEY=sk-your-key-here

# App Settings
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO
```

### 2. Run Your Python App Locally

```bash
# Activate virtual environment
venv\Scripts\activate

# Run the API
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🔍 Verify Connection

### Test PostgreSQL Connection

```bash
# Using psql (if installed)
psql -h localhost -U mcpagent -d mcpagent

# Or using Python
python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://mcpagent:mcpagent_password@localhost:5432/mcpagent'); print('Connected!' if engine.connect() else 'Failed')"
```

### Test Redis Connection

```bash
# Using redis-cli (if installed)
redis-cli -h localhost ping

# Or using Python
python -c "import redis; r = redis.from_url('redis://localhost:6379/0'); print('Connected!' if r.ping() else 'Failed')"
```

---

## 📊 Database Credentials

| Parameter | Value |
|-----------|-------|
| **Host** | localhost |
| **Port** | 5432 |
| **Database** | mcpagent |
| **Username** | mcpagent |
| **Password** | mcpagent_password |

**Connection String:**
```
postgresql://mcpagent:mcpagent_password@localhost:5432/mcpagent
```

---

## 💾 Redis Configuration

| Parameter | Value |
|-----------|-------|
| **Host** | localhost |
| **Port** | 6379 |
| **Database** | 0 |

**Connection String:**
```
redis://localhost:6379/0
```

---

## 🛠️ Useful Commands

### Start Services
```bash
docker-compose -f docker-compose.services.yml up -d
```

### Stop Services
```bash
docker-compose -f docker-compose.services.yml down
```

### Restart Services
```bash
docker-compose -f docker-compose.services.yml restart
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.services.yml logs -f

# PostgreSQL only
docker-compose -f docker-compose.services.yml logs -f postgres

# Redis only
docker-compose -f docker-compose.services.yml logs -f redis
```

### Check Status
```bash
docker-compose -f docker-compose.services.yml ps
```

### Remove Everything (including data)
```bash
docker-compose -f docker-compose.services.yml down -v
```

---

## 🔧 Database Management

### Access PostgreSQL Shell

```bash
docker exec -it mcpagent-postgres psql -U mcpagent -d mcpagent
```

**Inside psql:**
```sql
-- List all tables
\dt

-- Show table structure
\d table_name

-- Query data
SELECT * FROM users LIMIT 10;

-- Exit
\q
```

### Access Redis CLI

```bash
docker exec -it mcpagent-redis redis-cli
```

**Inside redis-cli:**
```bash
# Ping server
PING

# List all keys
KEYS *

# Get a value
GET key_name

# Set a value
SET test_key "test_value"

# Delete a key
DEL key_name

# Exit
EXIT
```

---

## 📦 Data Persistence

Your data is stored in Docker volumes:

- **PostgreSQL**: `mcpagent-postgres-data`
- **Redis**: `mcpagent-redis-data`

### View Volumes
```bash
docker volume ls | grep mcpagent
```

### Backup Database
```bash
# PostgreSQL backup
docker exec mcpagent-postgres pg_dump -U mcpagent mcpagent > backup.sql

# Restore
docker exec -i mcpagent-postgres psql -U mcpagent mcpagent < backup.sql
```

### Backup Redis
```bash
# Redis saves automatically, but you can force save
docker exec mcpagent-redis redis-cli SAVE
```

---

## 🔄 Reset Everything

If you want to start fresh:

```bash
# Stop and remove containers + volumes
docker-compose -f docker-compose.services.yml down -v

# Start fresh
docker-compose -f docker-compose.services.yml up -d
```

---

## 🐛 Troubleshooting

### Port Already in Use

**PostgreSQL (5432):**
```bash
# Windows - Find process using port
netstat -ano | findstr :5432
taskkill /PID <PID> /F

# Or change port in docker-compose
ports:
  - "5433:5432"  # Use 5433 instead
```

**Redis (6379):**
```bash
# Windows - Find process
netstat -ano | findstr :6379
taskkill /PID <PID> /F

# Or change port
ports:
  - "6380:6379"  # Use 6380 instead
```

### Cannot Connect from Python

1. **Check containers are running:**
   ```bash
   docker ps
   ```

2. **Check connection string:**
   ```
   # Use localhost, not container name
   postgresql://mcpagent:mcpagent_password@localhost:5432/mcpagent
   ```

3. **Check firewall:**
   - Allow ports 5432 and 6379

### Database Tables Not Created

```bash
# Initialize database tables
python -c "from src.infrastructure.database import init_db; init_db()"
```

---

## 📊 Health Checks

### Check Services Status

```bash
# All services
docker-compose -f docker-compose.services.yml ps

# Expected output:
# NAME                 STATUS              PORTS
# mcpagent-postgres    Up (healthy)       0.0.0.0:5432->5432/tcp
# mcpagent-redis       Up (healthy)       0.0.0.0:6379->6379/tcp
```

### Test from Your App

```python
# test_connection.py
from src.infrastructure.database import engine
from src.infrastructure.cache.redis_cache import cache

# Test database
try:
    with engine.connect() as conn:
        print("✅ Database connected!")
except Exception as e:
    print(f"❌ Database failed: {e}")

# Test Redis
if cache.enabled:
    print("✅ Redis connected!")
else:
    print("❌ Redis failed")
```

---

## 🎯 Complete Workflow

### 1. Start Docker Services
```bash
cd D:\MCP\MCPAGENT
docker-compose -f docker-compose.services.yml up -d
```

### 2. Configure Environment
```bash
# Edit .env file
DATABASE_URL=postgresql://mcpagent:mcpagent_password@localhost:5432/mcpagent
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-your-key
```

### 3. Run Your App
```bash
# Activate venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Test
```bash
# Health check
curl http://localhost:8000/health

# Should show:
# {
#   "status": "healthy",
#   "services": {
#     "database": "healthy",
#     "cache": "healthy",
#     ...
#   }
# }
```

---

## ✅ Success!

You now have:
- ✅ PostgreSQL running in Docker on port 5432
- ✅ Redis running in Docker on port 6379
- ✅ Your Python app connecting to both services
- ✅ Data persisted in Docker volumes

**Your app is now connected to production-like services!** 🎉

---

## 📞 Need Help?

- Check logs: `docker-compose -f docker-compose.services.yml logs -f`
- Restart: `docker-compose -f docker-compose.services.yml restart`
- Clean slate: `docker-compose -f docker-compose.services.yml down -v`

