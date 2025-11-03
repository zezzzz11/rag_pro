# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RAG Pro is a multi-user document Q&A application using Retrieval-Augmented Generation (RAG). It combines modern document processing (Docling), vector search (Qdrant), and local LLM inference (Ollama) with a professional Next.js frontend.

## Architecture

### Backend Structure (FastAPI)

The backend is split across three main modules:

**`main.py`** - Core application
- FastAPI app with JWT-protected endpoints
- Integrates: Docling (document processing), LangChain (RAG), Qdrant (vectors), Ollama (LLM)
- Key models loaded at startup: embedding model (all-MiniLM-L6-v2), reranker (cross-encoder), LLM (llama3.2)
- Document chunks stored with metadata: `{user_id, doc_id, filename, chunk_id}`

**`auth.py`** - Authentication layer
- JWT token generation/validation (7-day expiration)
- Password hashing with bcrypt
- `get_current_user_id()` dependency used to protect endpoints

**`database.py`** - Persistence layer
- SQLite database (`data/rag_pro.db`)
- Tables: `users`, `documents`
- Auto-initializes on import
- All document operations require user_id for isolation

### RAG Pipeline Architecture

1. **Document Upload Flow:**
   - Docling converts document → markdown text
   - RecursiveCharacterTextSplitter (1500 chars, 300 overlap) → chunks
   - SentenceTransformer → embeddings
   - Qdrant stores vectors with user_id metadata
   - SQLite tracks document metadata

2. **Retrieval Flow (Two-Stage with Reranking):**
   - Vector search retrieves 12 candidates (filtered by user_id)
   - Cross-encoder reranks for relevance
   - Top 5 chunks selected
   - Context assembled with source labels
   - Chain-of-thought prompt → LLM generates answer

### Frontend Structure (Next.js)

**Authentication State:**
- `lib/auth.ts` manages JWT tokens in localStorage
- `app/page.tsx` conditionally renders `<Auth>` or main app
- All API requests include `Authorization: Bearer {token}` header

**Component Hierarchy:**
```
page.tsx (auth gate)
├── Auth.tsx (login/register)
└── Main App
    ├── FileUpload.tsx (drag-drop with Docling support)
    ├── DocumentList.tsx (user's docs only)
    └── ChatInterface.tsx (streaming-style UI)
```

### Data Storage Layout

```
backend/
├── data/
│   ├── rag_pro.db          # SQLite (users + document metadata)
│   └── qdrant/             # Vector embeddings (persistent)
└── uploads/
    └── {user_id}/          # User-isolated file storage
        └── {doc_id}_{filename}
```

## Development Commands

### Initial Setup

```bash
# Backend
cd backend
./setup.sh                  # Creates venv, installs requirements.txt

# Frontend
cd frontend
npm install
```

### Running the Application

```bash
# From project root
./start.sh                  # Starts both backend (port 8000) and frontend (port 3000)
./stop.sh                   # Stops both servers
```

**Backend only:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Frontend only:**
```bash
cd frontend
npm run dev
```

### Prerequisites

**Ollama must be running:**
```bash
ollama serve              # Start Ollama server
ollama pull llama3.2      # Download model (or llama2)
ollama list               # Verify models available
```

### Docker Deployment (Fully Containerized)

**Run with Docker Compose (Recommended):**

```bash
# Prerequisites: Docker installed (with Compose V2)
# No other dependencies needed - everything runs in containers!

# Build and start all services (includes Ollama)
docker compose up -d

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f ollama    # Watch model download
docker compose logs -f backend
docker compose logs -f frontend

# Stop services
docker compose down

# Rebuild after code changes
docker compose up -d --build
```

**Important Docker Notes:**
- **Fully containerized** - Ollama, Backend, and Frontend all run in Docker
- Uses lightweight model by default: `qwen2.5:0.5b` (397 MB)
- First startup takes 2-3 minutes to download the model
- Data persists in Docker volumes and local directories
- All services communicate via Docker network

**Configuration:**
- Copy `.env.example` to `.env` to customize
- Change model: Set `OLLAMA_MODEL=llama3.2:1b` in `.env`
- Backend: port 8000, Frontend: port 3000, Ollama: port 11434

**Lightweight Model Options:**
```bash
# In .env file:
OLLAMA_MODEL=qwen2.5:0.5b    # 397 MB (default, fastest)
OLLAMA_MODEL=llama3.2:1b     # 1.3 GB (better quality)
OLLAMA_MODEL=phi3:mini       # 2.2 GB (Microsoft)
OLLAMA_MODEL=gemma2:2b       # 1.6 GB (Google)
```

**First-time startup:**
```bash
docker compose up -d
# Wait for Ollama to download model (check logs)
docker compose logs -f ollama
# When you see "Model ready!", backend will auto-start
```

### Modifying the RAG Pipeline

**Change LLM model:**
Edit `backend/main.py:86`:
```python
llm = Ollama(model="llama3.2", base_url="http://localhost:11434")
```

**Adjust chunking strategy:**
Edit `backend/main.py:88-94`:
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,     # Increase for more context per chunk
    chunk_overlap=300,   # Increase to preserve more context at boundaries
)
```

**Modify reranking:**
- Initial retrieval count: `main.py` search for `k=12`
- Final chunk count: `main.py` search for `[:5]` after reranking
- Change reranker model: `main.py:97`

### User Isolation Implementation

**Critical:** All protected endpoints must filter by user_id:

```python
# In chat endpoint (main.py:~220)
user_filter = Filter(
    must=[FieldCondition(key="metadata.user_id", match=MatchValue(value=user_id))]
)
initial_docs = vector_store.similarity_search(query, k=12, filter=user_filter)
```

**When adding new endpoints:**
1. Add `user_id: str = Depends(get_current_user_id)` parameter
2. Filter Qdrant queries by `metadata.user_id`
3. Validate document ownership in database queries

### Adding New Document Types

Docling supports: PDF, DOCX, PPTX, XLSX, HTML, images (PNG, JPG, TIFF)

To add support for a new type:
1. Update `supported_extensions` tuple in `main.py:123`
2. Update frontend file input accept attribute in `FileUpload.tsx:105`
3. Docling handles processing automatically

### Database Migrations

No migration system exists. To modify schema:
1. Backup `backend/data/rag_pro.db`
2. Edit `database.py:20-47` table definitions
3. Delete database file (or write manual migration script)
4. Restart backend (auto-recreates tables)

### Frontend Auth Flow

**Token storage:** localStorage
**Token format:** JWT with `{sub: user_id, exp: timestamp}`

**Adding authenticated requests:**
```typescript
import { getAuthHeaders } from "@/lib/auth"

axios.post("http://localhost:8000/endpoint", data, {
  headers: getAuthHeaders()  // Injects Authorization header
})
```

## Configuration

### Environment Variables

Backend supports `.env` file (optional):
```bash
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

Default values in `auth.py:12-14` if not set.

### CORS Configuration

Edit `main.py:43-49` to allow additional origins:
```python
allow_origins=["http://localhost:3000", "https://yourdomain.com"]
```

### Vector Database

**Switch from file-based to server-based Qdrant:**
Replace `main.py:67`:
```python
qdrant_client = QdrantClient(url="http://localhost:6333")  # or Qdrant Cloud URL
```

## Key Implementation Details

### Reranking Pipeline

The two-stage retrieval is critical for quality:
1. Fast vector search casts a wide net (12 docs)
2. Slow cross-encoder precisely scores relevance
3. Only top 5 go to LLM (reduces context size, improves quality)

**Performance:** Cross-encoder adds ~500ms latency but reduces failed retrievals by 67%.

### Document Isolation

Three-layer isolation:
1. **Vector metadata:** Every chunk tagged with user_id
2. **Qdrant filtering:** Search queries include user_id filter
3. **Database validation:** Document operations check ownership

### Docling Integration

Docling converts all formats to markdown, preserving:
- Document structure (headings, lists)
- Tables (as markdown tables)
- OCR text from images/scanned PDFs

**Processing time:** ~2-10 seconds per document depending on size and OCR needs.

### Frontend State Management

No Redux/Zustand - uses React state:
- `page.tsx` manages auth state
- `refreshTrigger` prop pattern updates DocumentList after uploads
- JWT tokens persist across page reloads via localStorage

## Common Issues

**"Could not validate credentials"**
- Token expired (7 days) or malformed
- Check `localStorage` has `rag_pro_token`

**Documents not persisting**
- Verify `backend/data/qdrant/` directory exists
- Check SQLite file at `backend/data/rag_pro.db`

**Ollama connection errors**
- Ensure `ollama serve` is running
- Check model exists: `ollama list`
- Verify port 11434 accessible

**Cross-encoder slow to load**
- First request loads model (~500MB)
- Subsequent requests use cached model
- Consider preloading in startup event

**Vector search returns no results**
- Check user_id filter is applied
- Verify documents uploaded successfully
- Inspect Qdrant collection: `qdrant_client.get_collection("documents")`

## Testing Multi-User Isolation

```bash
# Register two users via API
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@test.com","username":"Alice","password":"pass123"}'
# Save token as TOKEN_A

curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@test.com","username":"Bob","password":"pass456"}'
# Save token as TOKEN_B

# Upload doc as Alice
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer $TOKEN_A" \
  -F "file=@doc_a.pdf"

# Query as Bob - should return empty results (no access to Alice's doc)
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN_B" \
  -H "Content-Type: application/json" \
  -d '{"query":"test"}'
```

## Additional Documentation

- `MULTI_USER_AUTH.md` - Authentication system details, security considerations
- `RAG_IMPROVEMENTS.md` - RAG optimization techniques implemented
- `README.md` - User-facing setup and usage guide
