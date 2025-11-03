# Deployment Guide - Docker Hub Images

This guide explains how to deploy RAG Pro using pre-built images from Docker Hub.

## 🎯 Docker Hub Images

**Repository:** `zezzzz1/rag-pro`

### Available Images

| Image | Size | Description |
|-------|------|-------------|
| `zezzzz1/rag-pro-backend:latest` | 3.45 GB | FastAPI backend with all ML dependencies |
| `zezzzz1/rag-pro-backend:v1.0` | 3.45 GB | Version 1.0 (stable) |
| `zezzzz1/rag-pro-frontend:latest` | 284 MB | Next.js frontend (optimized build) |
| `zezzzz1/rag-pro-frontend:v1.0` | 284 MB | Version 1.0 (stable) |

**Third-party images:**
- `ollama/ollama:latest` - Ollama LLM server

## 🚀 Quick Deploy

### Option 1: One-Command Deploy (Recommended)

```bash
# Download the production compose file
curl -O https://raw.githubusercontent.com/zezzzz11/rag_pro/main/docker-compose.prod.yml

# Download the Ollama init script
curl -O https://raw.githubusercontent.com/zezzzz11/rag_pro/main/ollama-init.sh
chmod +x ollama-init.sh

# Start everything
docker compose -f docker-compose.prod.yml up -d
```

### Option 2: Using Local docker-compose.prod.yml

```bash
# Clone or copy the repository
git clone https://github.com/zezzzz11/rag_pro.git
cd rag_pro

# Start with production compose file
docker compose -f docker-compose.prod.yml up -d
```

### Option 3: Manual Pull & Run

```bash
# Pull images
docker pull zezzzz1/rag-pro-backend:latest
docker pull zezzzz1/rag-pro-frontend:latest
docker pull ollama/ollama:latest

# Run with docker-compose.prod.yml or manually
docker run -d --name ollama -p 11434:11434 ollama/ollama:latest
docker run -d --name backend -p 8000:8000 zezzzz1/rag-pro-backend:latest
docker run -d --name frontend -p 3000:3000 zezzzz1/rag-pro-frontend:latest
```

## 📋 Prerequisites

- **Docker** installed (with Compose V2)
- **Minimum:** 8 GB RAM, 10 GB disk space
- **Recommended:** 16 GB RAM, 20 GB disk space

## 🔧 Configuration

### Environment Variables

Create a `.env` file (optional):

```bash
# Security
SECRET_KEY=your-super-secret-key-change-in-production

# Token expiration (minutes)
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Model selection (lightweight models recommended)
OLLAMA_MODEL=qwen2.5:0.5b

# Available models:
# qwen2.5:0.5b  - 397 MB (fastest, testing/dev)
# llama3.2:1b   - 1.3 GB (balanced)
# phi3:mini     - 2.2 GB (production quality)
# gemma2:2b     - 1.6 GB (good balance)
```

### Persistent Data

Create data directories:

```bash
mkdir -p backend/data backend/uploads
```

These directories will persist:
- `backend/data/` - SQLite database + Qdrant vectors
- `backend/uploads/` - User-uploaded documents
- Docker volume `ollama-data` - Downloaded models

## 🌐 Deployment Targets

### Local Development

```bash
docker compose -f docker-compose.prod.yml up -d
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### VPS / Cloud VM

**Requirements:**
- Ubuntu 20.04+ / Debian 11+ / RHEL 8+
- Docker installed
- Ports 3000, 8000, 11434 open

**Deploy:**

```bash
# SSH into server
ssh user@your-server.com

# Install Docker (if not installed)
curl -fsSL https://get.docker.com | sh

# Deploy application
mkdir rag_pro && cd rag_pro
wget https://raw.githubusercontent.com/zezzzz11/rag_pro/main/docker-compose.prod.yml
wget https://raw.githubusercontent.com/zezzzz11/rag_pro/main/ollama-init.sh
chmod +x ollama-init.sh

# Create .env file
cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
OLLAMA_MODEL=qwen2.5:0.5b
EOF

# Start services
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
```

### Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml rag-pro

# Check services
docker stack services rag-pro
docker stack ps rag-pro
```

### Kubernetes

Convert to Kubernetes manifests using Kompose:

```bash
kompose convert -f docker-compose.prod.yml
kubectl apply -f .
```

## 📊 Monitoring

### Check Status

```bash
# View all containers
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f

# View specific service logs
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f ollama

# Check health
curl http://localhost:8000/
curl http://localhost:11434/api/version
```

### Resource Usage

```bash
# Monitor resource usage
docker stats

# View disk usage
docker system df
```

## 🔄 Updates

### Update to Latest Version

```bash
# Pull latest images
docker compose -f docker-compose.prod.yml pull

# Recreate containers
docker compose -f docker-compose.prod.yml up -d

# Remove old images
docker image prune -a
```

### Update to Specific Version

Edit `docker-compose.prod.yml`:

```yaml
backend:
  image: zezzzz1/rag-pro-backend:v1.0  # Change to specific version
frontend:
  image: zezzzz1/rag-pro-frontend:v1.0  # Change to specific version
```

Then restart:

```bash
docker compose -f docker-compose.prod.yml up -d
```

## 🛡️ Security Hardening

### Production Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set up HTTPS with reverse proxy (nginx/Caddy)
- [ ] Configure firewall (UFW/iptables)
- [ ] Enable Docker security features
- [ ] Regular backups of `backend/data/` directory
- [ ] Update images regularly
- [ ] Monitor logs for suspicious activity
- [ ] Use strong passwords for user accounts

### Reverse Proxy Example (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🗄️ Backup & Restore

### Backup

```bash
# Backup data directories
tar -czf rag-pro-backup-$(date +%Y%m%d).tar.gz backend/data backend/uploads

# Backup Ollama models (optional)
docker run --rm -v rag-pro_ollama-data:/data -v $(pwd):/backup \
  alpine tar -czf /backup/ollama-models-backup.tar.gz /data
```

### Restore

```bash
# Restore data
tar -xzf rag-pro-backup-YYYYMMDD.tar.gz

# Restore Ollama models
docker run --rm -v rag-pro_ollama-data:/data -v $(pwd):/backup \
  alpine tar -xzf /backup/ollama-models-backup.tar.gz -C /
```

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs
docker compose -f docker-compose.prod.yml logs backend

# Restart specific service
docker compose -f docker-compose.prod.yml restart backend

# Force recreate
docker compose -f docker-compose.prod.yml up -d --force-recreate
```

### Out of disk space

```bash
# Clean unused images
docker image prune -a

# Clean unused volumes
docker volume prune

# Clean everything
docker system prune -a --volumes
```

### Model download fails

```bash
# Check Ollama container logs
docker compose -f docker-compose.prod.yml logs ollama

# Manually pull model
docker compose -f docker-compose.prod.yml exec ollama ollama pull qwen2.5:0.5b

# Restart backend after model is ready
docker compose -f docker-compose.prod.yml restart backend
```

## 📈 Scaling

### Horizontal Scaling (Multiple Replicas)

For high availability, use Docker Swarm or Kubernetes to run multiple replicas:

```bash
# Docker Swarm example
docker service scale rag-pro_backend=3
docker service scale rag-pro_frontend=3
```

### Vertical Scaling (More Resources)

Update Docker resource limits in `docker-compose.prod.yml`:

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '4'
        memory: 8G
      reservations:
        cpus: '2'
        memory: 4G
```

## 📞 Support

- **Documentation:** See CLAUDE.md, DOCKER.md, README.md
- **Issues:** GitHub Issues
- **Docker Hub:** https://hub.docker.com/u/zezzzz1

## 📄 License

MIT License - See LICENSE file for details
