#!/bin/bash
# Script to build and push Docker images to Docker Hub
# This includes the latest authentication fixes

set -e

echo "🐳 Building and pushing Docker images with authentication fixes..."
echo ""

# Check if logged into Docker Hub
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Get version tag (optional, defaults to latest)
VERSION="${1:-latest}"
echo "📦 Building version: $VERSION"
echo ""

# Build backend image
echo "🔨 Building backend image..."
cd backend
docker build -t zezzzz1/rag-pro-backend:$VERSION .
cd ..
echo "✅ Backend image built"
echo ""

# Build frontend image  
echo "🔨 Building frontend image..."
cd frontend
docker build -t zezzzz1/rag-pro-frontend:$VERSION .
cd ..
echo "✅ Frontend image built"
echo ""

# Tag as latest if version was specified
if [ "$VERSION" != "latest" ]; then
    echo "🏷️  Tagging images as latest..."
    docker tag zezzzz1/rag-pro-backend:$VERSION zezzzz1/rag-pro-backend:latest
    docker tag zezzzz1/rag-pro-frontend:$VERSION zezzzz1/rag-pro-frontend:latest
    echo "✅ Images tagged"
    echo ""
fi

# Push images
echo "📤 Pushing images to Docker Hub..."
echo "   (Make sure you're logged in with 'docker login')"
echo ""

read -p "Push backend image? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker push zezzzz1/rag-pro-backend:$VERSION
    if [ "$VERSION" != "latest" ]; then
        docker push zezzzz1/rag-pro-backend:latest
    fi
    echo "✅ Backend image pushed"
fi
echo ""

read -p "Push frontend image? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker push zezzzz1/rag-pro-frontend:$VERSION
    if [ "$VERSION" != "latest" ]; then
        docker push zezzzz1/rag-pro-frontend:latest
    fi
    echo "✅ Frontend image pushed"
fi

echo ""
echo "🎉 Done! Images are now available on Docker Hub:"
echo "   - zezzzz1/rag-pro-backend:$VERSION"
echo "   - zezzzz1/rag-pro-frontend:$VERSION"
if [ "$VERSION" != "latest" ]; then
    echo "   - zezzzz1/rag-pro-backend:latest"
    echo "   - zezzzz1/rag-pro-frontend:latest"
fi
echo ""
echo "📝 Note: These images include the authentication fixes:"
echo "   - Token validation on page load"
echo "   - Auto-logout on invalid/expired tokens"
echo "   - Consistent error handling for 401/403"
echo ""
