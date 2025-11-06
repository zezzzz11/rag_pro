# Updating Docker Images on Docker Hub

This guide explains how to build and push updated Docker images with the latest authentication fixes to Docker Hub.

## Prerequisites

1. **Docker** installed and running
2. **Docker Hub account** (username: zezzzz1)
3. **Logged into Docker Hub**: Run `docker login` first

## Quick Update (Recommended)

Use the automated script:

```bash
# Build and push as 'latest' (default)
./build-and-push-docker.sh

# Or build with version tag
./build-and-push-docker.sh v1.1
```

The script will:
1. ✅ Build both backend and frontend images
2. ✅ Tag images appropriately
3. ✅ Ask for confirmation before pushing
4. ✅ Push to Docker Hub

## Manual Update Process

If you prefer to build and push manually:

### 1. Login to Docker Hub

```bash
docker login
# Enter username: zezzzz1
# Enter password: [your-password]
```

### 2. Build Backend Image

```bash
cd backend
docker build -t zezzzz1/rag-pro-backend:latest .
cd ..
```

### 3. Build Frontend Image

```bash
cd frontend
docker build -t zezzzz1/rag-pro-frontend:latest .
cd ..
```

### 4. Test Images Locally (Optional)

```bash
# Test with docker-compose
docker compose -f docker-compose.prod.yml up -d

# Verify everything works
# Visit http://localhost:3000 and test authentication

# Stop test containers
docker compose -f docker-compose.prod.yml down
```

### 5. Push to Docker Hub

```bash
# Push backend
docker push zezzzz1/rag-pro-backend:latest

# Push frontend
docker push zezzzz1/rag-pro-frontend:latest
```

## With Version Tags

To create a versioned release:

```bash
# Build and tag backend
cd backend
docker build -t zezzzz1/rag-pro-backend:v1.1 .
docker tag zezzzz1/rag-pro-backend:v1.1 zezzzz1/rag-pro-backend:latest
cd ..

# Build and tag frontend
cd frontend
docker build -t zezzzz1/rag-pro-frontend:v1.1 .
docker tag zezzzz1/rag-pro-frontend:v1.1 zezzzz1/rag-pro-frontend:latest
cd ..

# Push all tags
docker push zezzzz1/rag-pro-backend:v1.1
docker push zezzzz1/rag-pro-backend:latest
docker push zezzzz1/rag-pro-frontend:v1.1
docker push zezzzz1/rag-pro-frontend:latest
```

## What's Included in the Updated Images

The updated Docker images include the **authentication fixes**:

### Frontend Changes
- ✅ Token validation on page load (`app/page.tsx`)
- ✅ Auto-logout when token is invalid/expired
- ✅ Consistent 401/403 error handling in all components
- ✅ Clear error messages for authentication failures

### Backend
- ✅ No changes needed (backend was working correctly)

### Files Modified
- `frontend/app/page.tsx`
- `frontend/components/ChatInterface.tsx`
- `frontend/components/FileUpload.tsx`
- `frontend/components/DocumentList.tsx`
- `frontend/components/AdminPanel.tsx`

## Verify Update Was Successful

After pushing, verify the images are updated:

```bash
# Check image info on Docker Hub
docker manifest inspect zezzzz1/rag-pro-backend:latest
docker manifest inspect zezzzz1/rag-pro-frontend:latest

# Pull and test the images
docker pull zezzzz1/rag-pro-backend:latest
docker pull zezzzz1/rag-pro-frontend:latest

# Run with production compose
docker compose -f docker-compose.prod.yml up -d

# Test authentication fixes:
# 1. Login to http://localhost:3000
# 2. Refresh page - should stay logged in
# 3. Manually corrupt token in localStorage
# 4. Refresh page - should auto-logout
```

## Troubleshooting

### "authentication required" error when pushing

```bash
# Login again
docker login

# Verify you're logged in as the correct user
docker info | grep Username
```

### Build fails with "no space left on device"

```bash
# Clean up old images
docker system prune -a

# Remove unused volumes
docker volume prune
```

### Image size concerns

Current sizes:
- Backend: ~3.45 GB (includes ML libraries: torch, transformers, etc.)
- Frontend: ~284 MB (Next.js standalone build)

To reduce size:
- Backend: Already optimized with multi-stage build
- Frontend: Already uses standalone output

### Push is very slow

Docker images are large. Expect:
- Backend: 10-30 minutes depending on connection
- Frontend: 1-5 minutes

Tips:
- Use good internet connection
- Push during off-peak hours
- Consider using Docker layer caching

## Updating DEPLOYMENT.md

After pushing new images, update version numbers in DEPLOYMENT.md:

```bash
# Edit DEPLOYMENT.md
# Update the "Available Images" section with new version
# Update the changelog/release notes

# Example:
# | `zezzzz1/rag-pro-backend:v1.1` | 3.45 GB | Version 1.1 - Authentication fixes |
# | `zezzzz1/rag-pro-frontend:v1.1` | 284 MB | Version 1.1 - Authentication fixes |
```

## Automation (GitHub Actions)

For future updates, consider setting up GitHub Actions to automatically build and push on release:

```yaml
# .github/workflows/docker-publish.yml
name: Docker Build and Push

on:
  release:
    types: [published]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: zezzzz1/rag-pro-backend:${{ github.ref_name }},zezzzz1/rag-pro-backend:latest
      - uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: zezzzz1/rag-pro-frontend:${{ github.ref_name }},zezzzz1/rag-pro-frontend:latest
```

## Support

For issues:
- Docker Hub: https://hub.docker.com/u/zezzzz1
- GitHub: https://github.com/zezzzz11/rag_pro
- Documentation: See DOCKER.md, DEPLOYMENT.md

## Summary

**TL;DR:**
```bash
# Quick update
./build-and-push-docker.sh

# Or manual
docker login
cd backend && docker build -t zezzzz1/rag-pro-backend:latest . && cd ..
cd frontend && docker build -t zezzzz1/rag-pro-frontend:latest . && cd ..
docker push zezzzz1/rag-pro-backend:latest
docker push zezzzz1/rag-pro-frontend:latest
```

The images will now include all authentication fixes! 🎉
