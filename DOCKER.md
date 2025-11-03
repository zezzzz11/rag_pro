# Docker Deployment Guide - Fully Containerized

This guide explains how to run RAG Pro using Docker containers with everything containerized (including Ollama).

## Prerequisites

1. **Docker** installed (with Compose V2)
2. **That's it!** Everything else runs in containers.

## Quick Start

```bash
# 1. Start all services (first time will download ~400 MB model)
docker compose up -d

# 2. Watch the model download (first time only)
docker compose logs -f ollama

# 3. Access the application (after model is ready)
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Ollama API: http://localhost:11434

# 4. View all logs
docker compose logs -f

# 5. Stop services
docker compose down

# 6. Remove everything including downloaded models
docker compose down -v
```

## Configuration

### Environment Variables

Create a `.env` file in the project root (optional):

```bash
# Copy example file
cp .env.example .env

# Edit as needed
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=10080
OLLAMA_MODEL=qwen2.5:0.5b
```

### Default Configuration

If no `.env` file exists, these defaults are used:
- SECRET_KEY: `change-this-secret-key-in-production`
- ACCESS_TOKEN_EXPIRE_MINUTES: `10080` (7 days)
- OLLAMA_MODEL: `qwen2.5:0.5b` (397 MB)
- OLLAMA_BASE_URL: `http://ollama:11434` (auto-configured)

### Lightweight Model Options

Choose based on your needs:

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| `qwen2.5:0.5b` | 397 MB | ⚡⚡⚡ | ⭐⭐ | Testing, dev |
| `llama3.2:1b` | 1.3 GB | ⚡⚡ | ⭐⭐⭐ | Balanced |
| `phi3:mini` | 2.2 GB | ⚡ | ⭐⭐⭐⭐ | Production |
| `gemma2:2b` | 1.6 GB | ⚡⚡ | ⭐⭐⭐ | Good balance |

To change model:
```bash
# In .env file
OLLAMA_MODEL=llama3.2:1b

# Then restart
docker compose down
docker compose up -d
```

## Architecture

### Services (All Containerized)

**Ollama Container:**
- Official Ollama Docker image
- Automatically downloads lightweight model on first startup
- Default model: `qwen2.5:0.5b` (397 MB)
- Persistent volume for models
- Port: 11434

**Backend Container:**
- FastAPI application
- Connects to Ollama container via Docker network
- Persistent volumes for data and uploads
- Port: 8000

**Frontend Container:**
- Next.js application (standalone build)
- Connects to backend container
- Port: 3000

### Volume Mounts

Data persists between container restarts:
- `ollama-data` (Docker volume) → Ollama models and config
- `./backend/data` → Container's `/app/data` (SQLite + Qdrant vectors)
- `./backend/uploads` → Container's `/app/uploads` (uploaded documents)

## Common Commands

### Development

```bash
# Build and start
docker compose up -d --build

# Watch logs
docker compose logs -f backend
docker compose logs -f frontend

# Restart a service
docker compose restart backend

# Execute commands in container
docker compose exec backend python -m pip list
docker compose exec frontend npm list
```

### Maintenance

```bash
# Stop all containers
docker compose down

# Stop and remove volumes (⚠️ deletes data)
docker compose down -v

# View running containers
docker compose ps

# Clean up unused images
docker system prune -a
```

### Building Individual Images

```bash
# Backend
docker build -t rag-pro-backend ./backend

# Frontend
docker build -t rag-pro-frontend ./frontend
```

## Troubleshooting

### Backend can't connect to Ollama

**Symptom:** `Connection refused` errors in backend logs

**Solution:**
1. Check Ollama container is running: `docker compose ps ollama`
2. Check Ollama logs: `docker compose logs ollama`
3. Ensure model was downloaded: Look for "Model ready!" in logs
4. Restart backend: `docker compose restart backend`

### Model download is slow

**Symptom:** Ollama container takes long to start

**Solution:**
- First startup downloads the model (~400 MB for default)
- Check download progress: `docker compose logs -f ollama`
- Use lighter model if needed: Set `OLLAMA_MODEL=qwen2.5:0.5b` in `.env`

### Port already in use

**Symptom:** `port is already allocated`

**Solution:**
```bash
# Find process using port
lsof -i :8000
lsof -i :3000

# Kill the process or change ports in docker-compose.yml
```

### Data not persisting

**Symptom:** Documents/users disappear after restart

**Solution:**
- Check volume mounts in `docker-compose.yml`
- Ensure `./backend/data` and `./backend/uploads` exist
- Don't use `docker compose down -v` (removes volumes)

### Frontend can't reach backend

**Symptom:** API calls fail from browser

**Solution:**
1. Backend must be accessible from browser (not just container)
2. Use `http://localhost:8000` (not container hostname)
3. Check CORS settings in `backend/main.py`

### Models taking too long to download

**Symptom:** Backend container times out during startup

**Solution:**
- Download models on host first: `ollama pull llama3.2`
- Models are accessed from host Ollama, not downloaded in container

## Production Considerations

### Security

⚠️ **Before deploying to production:**

1. Change `SECRET_KEY` to a strong random value
2. Set up HTTPS/TLS (use reverse proxy like nginx)
3. Update CORS origins in `backend/main.py`
4. Use environment variables for all secrets
5. Consider using PostgreSQL instead of SQLite
6. Implement rate limiting

### Scalability

For production deployments:
- Use managed Qdrant Cloud instead of file-based
- Deploy Ollama separately or use cloud LLM API
- Add Redis for caching
- Use object storage (S3) for documents
- Set up load balancing
- Implement health checks and monitoring

### Example Production docker-compose.yml

```yaml
services:
  backend:
    image: rag-pro-backend:latest
    restart: always
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=postgresql://...
      - QDRANT_URL=https://your-qdrant-cloud.io
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Alternative: Run Without Docker

If you prefer running without Docker:

```bash
# Backend
cd backend
./setup.sh
source venv/bin/activate
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

See main README.md for detailed non-Docker setup.

## Support

For issues with:
- **Docker setup:** Check this guide
- **Application features:** See main README.md
- **Architecture:** See CLAUDE.md
- **Authentication:** See MULTI_USER_AUTH.md
- **RAG pipeline:** See RAG_IMPROVEMENTS.md
