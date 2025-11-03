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
