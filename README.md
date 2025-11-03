# RAG Pro - Modern Document Q&A

A professional, modern RAG (Retrieval-Augmented Generation) application for document question answering.

## Features

✨ **Modern UI**
- Clean, professional interface built with Next.js 15 & Tailwind CSS
- Drag-and-drop file upload
- Real-time chat interface
- Document management
- Dark mode support

🚀 **Powerful Backend**
- LangChain for RAG pipeline
- Qdrant vector database
- Ollama for local LLM inference
- **Docling** for advanced document processing with OCR
- Support for PDF, DOCX, PPTX, XLSX, HTML, and images
- AI-powered layout analysis and table extraction
- Smart text chunking with structure preservation

🔒 **Privacy & Security**
- **Multi-user authentication** with JWT tokens
- **Complete document isolation** - users only see their own documents
- **Persistent storage** - documents survive server restarts
- All processing happens locally
- No data sent to external APIs
- Use your own Ollama models

## Tech Stack

**Frontend:**
- Next.js 15
- TypeScript
- Tailwind CSS
- Lucide Icons
- Axios

**Backend:**
- FastAPI
- LangChain
- Qdrant
- Sentence Transformers
- Ollama
- Docling (IBM Research)

## Prerequisites

- Python 3.9+
- Node.js 18+
- Ollama installed and running
- llama2 model downloaded (`ollama pull llama2`)

**Or use Docker** (no installation needed, see [Docker Deployment](#docker-deployment) below)

## Quick Start

### 1. Setup Backend

```bash
cd backend
chmod +x setup.sh
./setup.sh
```

### 2. Setup Frontend

```bash
cd frontend
npm install
```

### 3. Start Everything

From the root directory:

```bash
chmod +x start.sh stop.sh
./start.sh
```

The application will be available at:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000

### 4. Stop

```bash
./stop.sh
```

## Docker Deployment

### 🐳 Quick Start with Docker (Recommended)

The easiest way to run RAG Pro is with Docker. Everything is containerized including Ollama!

**Prerequisites:** Docker with Compose V2 installed

```bash
# Clone the repository
git clone https://github.com/zezzzz11/rag_pro.git
cd rag_pro

# Start all services (first time downloads ~400 MB model)
docker compose up -d

# Watch logs
docker compose logs -f

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Stop services:**
```bash
docker compose down
```

### 🚀 Deploy from Docker Hub

Deploy without cloning the repository using pre-built images:

```bash
# Download production compose file
curl -O https://raw.githubusercontent.com/zezzzz11/rag_pro/main/docker-compose.prod.yml
curl -O https://raw.githubusercontent.com/zezzzz11/rag_pro/main/ollama-init.sh
chmod +x ollama-init.sh

# Start everything
docker compose -f docker-compose.prod.yml up -d
```

**Docker Hub Images:**
- Backend: `zezzzz1/rag-pro-backend:latest` (3.45 GB)
- Frontend: `zezzzz1/rag-pro-frontend:latest` (284 MB)

### ⚙️ Configuration

Create a `.env` file to customize:

```bash
# Security
SECRET_KEY=your-super-secret-key

# Model selection (lightweight models recommended)
OLLAMA_MODEL=qwen2.5:0.5b

# Available models:
# qwen2.5:0.5b  - 397 MB (fastest, testing/dev)
# llama3.2:1b   - 1.3 GB (balanced)
# phi3:mini     - 2.2 GB (production quality)
# gemma2:2b     - 1.6 GB (good balance)
```

### 📚 Full Documentation

For detailed Docker instructions, see:
- **[DOCKER.md](DOCKER.md)** - Complete Docker setup and troubleshooting
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide for VPS, Cloud, Kubernetes

## Usage

1. **Register/Login:** Create an account or login (data stored locally)
2. **Upload Documents:** Drag and drop PDF, DOCX, PPTX, XLSX, HTML, or image files
3. **Advanced Processing:** Docling automatically handles OCR, table extraction, and layout analysis
4. **Ask Questions:** Type your questions in the chat interface
5. **Get Answers:** Receive AI-powered answers with source citations
6. **Manage Documents:** View and delete your uploaded documents
7. **Privacy Guaranteed:** Your documents are completely isolated from other users

## API Endpoints

**Public:**
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user

**Protected (requires authentication):**
- `GET /auth/me` - Get current user info
- `POST /upload` - Upload a document
- `POST /chat` - Ask a question
- `GET /documents` - List your documents
- `DELETE /documents/{id}` - Delete a document

See [MULTI_USER_AUTH.md](MULTI_USER_AUTH.md) for detailed API documentation.

## Configuration

Edit `backend/main.py` to:
- Change the Ollama model (default: llama2)
- Adjust chunk size and overlap
- Configure vector store settings

## Troubleshooting

**Ollama not found:**
```bash
# Install Ollama
brew install ollama

# Start Ollama
ollama serve

# Pull llama2
ollama pull llama2
```

**Port conflicts:**
Edit ports in `start.sh` and update CORS settings in `backend/main.py`

## License

MIT
