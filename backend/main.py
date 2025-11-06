import os
import uuid
from typing import List, Optional
from pathlib import Path
from datetime import timedelta

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, Filter, FieldCondition, MatchValue

from docling.document_converter import DocumentConverter
from sentence_transformers import CrossEncoder

# Import auth and database modules
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user_id,
    get_current_admin_user_id,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from database import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    create_document as db_create_document,
    get_user_documents,
    get_document,
    delete_document as db_delete_document,
    get_all_users,
    get_all_documents,
    delete_user_admin,
    delete_document_admin,
    get_stats,
    get_db
)

# Initialize FastAPI
app = FastAPI(title="RAG Pro API - Multi-User")

# CORS - Now only needed for Next.js server-side calls
# All browser requests go through Next.js API routes, so we only need to allow the Next.js server
# In Docker: Next.js runs in the same network, in dev: localhost:3000
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
allowed_origins = allowed_origins_env.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

QDRANT_PATH = Path("data/qdrant")
QDRANT_PATH.mkdir(parents=True, exist_ok=True)

COLLECTION_NAME = "documents"

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

# Initialize Qdrant (PERSISTENT storage)
qdrant_client = QdrantClient(path=str(QDRANT_PATH))

# Create collection if it doesn't exist
try:
    qdrant_client.get_collection(COLLECTION_NAME)
except:
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

# Initialize vector store
vector_store = Qdrant(
    client=qdrant_client,
    collection_name=COLLECTION_NAME,
    embeddings=embeddings,
)

# Initialize LLM (use environment variable for model selection)
# Use environment variable for Ollama URL (for Docker compatibility)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
llm = Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)

# Text splitter - Improved chunking strategy
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,  # Larger chunks for better context
    chunk_overlap=300,  # More overlap to preserve context across chunks
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)

# Initialize reranking model (cross-encoder for better relevance scoring)
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# Initialize Docling converter
doc_converter = DocumentConverter()


# Pydantic models
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    username: str


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = []


class DocumentInfo(BaseModel):
    id: str
    filename: str
    chunks: int
    created_at: str


def extract_text_with_docling(file_path: str) -> str:
    """Extract text from document using Docling."""
    try:
        result = doc_converter.convert(file_path)
        text = result.document.export_to_markdown()
        return text
    except Exception as e:
        raise Exception(f"Docling processing failed: {str(e)}")


@app.get("/")
def read_root():
    return {"message": "RAG Pro API - Multi-User with Authentication"}


# Authentication endpoints
@app.post("/auth/register", response_model=Token)
async def register(user: UserRegister):
    """Register a new user."""
    # Check if user exists
    if get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user.password)

    if not create_user(user_id, user.username, user.email, hashed_password):
        raise HTTPException(status_code=400, detail="Could not create user")

    # Create access token
    access_token = create_access_token(
        data={"sub": user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user_id,
        username=user.username
    )


@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin):
    """Login a user."""
    db_user = get_user_by_email(user.email)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": db_user["id"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=db_user["id"],
        username=db_user["username"]
    )


@app.get("/auth/me")
async def get_current_user(user_id: str = Depends(get_current_user_id)):
    """Get current user information."""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "is_admin": user.get("is_admin", 0) == 1
    }


# Document operations (with user isolation)
@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id)
):
    """Upload and process a document (user-specific)."""
    try:
        # Validate file type
        supported_extensions = ('.pdf', '.docx', '.pptx', '.xlsx', '.html', '.png', '.jpg', '.jpeg', '.tiff')
        if not file.filename.lower().endswith(supported_extensions):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported: {', '.join(supported_extensions)}"
            )

        # Generate unique ID
        doc_id = str(uuid.uuid4())

        # Save file with user_id prefix
        user_upload_dir = UPLOAD_DIR / user_id
        user_upload_dir.mkdir(exist_ok=True)
        file_path = user_upload_dir / f"{doc_id}_{file.filename}"

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Extract text using Docling
        text = extract_text_with_docling(str(file_path))

        if not text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the document")

        # Split into chunks
        chunks = text_splitter.split_text(text)

        # Add metadata with user_id for isolation
        metadatas = [
            {
                "user_id": user_id,
                "doc_id": doc_id,
                "filename": file.filename,
                "chunk_id": i
            }
            for i in range(len(chunks))
        ]

        # Add to vector store
        vector_store.add_texts(chunks, metadatas=metadatas)

        # Save to database
        db_create_document(doc_id, user_id, file.filename, str(file_path), len(chunks))

        return {
            "message": "Document uploaded and processed successfully",
            "doc_id": doc_id,
            "filename": file.filename,
            "chunks": len(chunks)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Chat with the documents (only user's own documents)."""
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        # Step 1: Retrieve documents with user_id filter
        # Note: Qdrant filter to only search user's documents
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        user_filter = Filter(
            must=[
                FieldCondition(
                    key="metadata.user_id",
                    match=MatchValue(value=user_id)
                )
            ]
        )

        # Search with filter
        initial_docs = vector_store.similarity_search(
            request.query,
            k=12,
            filter=user_filter
        )

        if not initial_docs:
            return ChatResponse(
                response="I couldn't find any relevant information in your uploaded documents. Please upload documents first.",
                sources=[]
            )

        # Step 2: Rerank documents
        pairs = [[request.query, doc.page_content] for doc in initial_docs]
        scores = reranker.predict(pairs)

        doc_score_pairs = list(zip(initial_docs, scores))
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
        reranked_docs = [doc for doc, score in doc_score_pairs[:5]]

        # Step 3: Build enhanced context
        context_parts = []
        for i, doc in enumerate(reranked_docs, 1):
            filename = doc.metadata.get("filename", "Unknown")
            context_parts.append(f"[Source {i}: {filename}]\n{doc.page_content}")

        context = "\n\n---\n\n".join(context_parts)

        # Step 4: Enhanced prompt with chain-of-thought
        prompt = f"""You are a helpful assistant analyzing documents to answer questions accurately.

Context from relevant documents:
{context}

Question: {request.query}

Instructions:
1. First, identify which parts of the context are relevant to the question
2. Think through the answer step by step
3. Provide a clear, accurate answer based on the context
4. If the context doesn't contain enough information, say so clearly
5. Cite which source(s) you used in your answer

Answer:"""

        # Generate response
        response = llm.invoke(prompt)

        # Extract unique sources
        sources = list(set([doc.metadata.get("filename", "Unknown") for doc in reranked_docs]))

        return ChatResponse(response=response, sources=sources)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.get("/documents", response_model=List[DocumentInfo])
async def list_documents(user_id: str = Depends(get_current_user_id)):
    """List all documents for the current user."""
    docs = get_user_documents(user_id)
    return [
        DocumentInfo(
            id=doc["id"],
            filename=doc["filename"],
            chunks=doc["chunks"],
            created_at=doc["created_at"]
        )
        for doc in docs
    ]


@app.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a document (only if owned by user)."""
    # Check ownership
    doc = get_document(doc_id, user_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        # Delete file
        file_path = Path(doc["file_path"])
        if file_path.exists():
            file_path.unlink()

        # Delete from vector store (filter by user_id and doc_id)
        # Note: This is a limitation - Qdrant doesn't have easy metadata-based deletion
        # In production, you'd track point IDs or use a different approach

        # Delete from database
        if not db_delete_document(doc_id, user_id):
            raise HTTPException(status_code=404, detail="Could not delete document")

        return {"message": "Document deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


# Admin endpoints
@app.get("/admin/stats")
async def get_admin_stats(admin_id: str = Depends(get_current_admin_user_id)):
    """Get system statistics (admin only)."""
    return get_stats()


@app.get("/admin/users")
async def get_admin_users(admin_id: str = Depends(get_current_admin_user_id)):
    """Get all users (admin only)."""
    users = get_all_users()
    # Remove hashed passwords from response
    for user in users:
        user.pop("hashed_password", None)
    return {"users": users}


@app.get("/admin/documents")
async def get_admin_documents(admin_id: str = Depends(get_current_admin_user_id)):
    """Get all documents (admin only)."""
    documents = get_all_documents()
    return {"documents": documents}


@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    admin_id: str = Depends(get_current_admin_user_id)
):
    """Delete a user and all their documents (admin only)."""
    # Don't allow admin to delete themselves
    if user_id == admin_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete user's files
    user_upload_dir = Path(f"uploads/{user_id}")
    if user_upload_dir.exists():
        import shutil
        shutil.rmtree(user_upload_dir)

    # Delete from database (will cascade delete documents)
    if delete_user_admin(user_id):
        return {"message": f"User {user['username']} deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete user")


@app.delete("/admin/documents/{doc_id}")
async def delete_document_as_admin(
    doc_id: str,
    admin_id: str = Depends(get_current_admin_user_id)
):
    """Delete any document (admin only)."""
    # Get document info before deleting
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    doc = cursor.fetchone()
    conn.close()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc_dict = dict(doc)

    # Delete file
    file_path = Path(doc_dict["file_path"])
    if file_path.exists():
        file_path.unlink()

    # Delete from database
    if delete_document_admin(doc_id):
        return {"message": "Document deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete document")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
