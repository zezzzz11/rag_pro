import os
import uuid
from typing import List, Optional
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Qdrant
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from docling.document_converter import DocumentConverter
import json

# Initialize FastAPI
app = FastAPI(title="RAG Pro API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

COLLECTION_NAME = "documents"

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

# Initialize Qdrant (in-memory for now)
qdrant_client = QdrantClient(":memory:")

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

# Initialize LLM (llama3 for better reasoning)
llm = Ollama(model="llama3.2", base_url="http://localhost:11434")

# Text splitter - Improved chunking strategy
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,  # Larger chunks for better context
    chunk_overlap=300,  # More overlap to preserve context across chunks
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)

# Initialize reranking model (cross-encoder for better relevance scoring)
from sentence_transformers import CrossEncoder
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# Store for document metadata
documents_db = {}

# Initialize Docling converter
doc_converter = DocumentConverter()


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = []


class DocumentInfo(BaseModel):
    id: str
    filename: str
    chunks: int


def extract_text_with_docling(file_path: str) -> str:
    """Extract text from document using Docling."""
    try:
        # Convert document
        result = doc_converter.convert(file_path)

        # Export to markdown for better structure preservation
        text = result.document.export_to_markdown()

        return text
    except Exception as e:
        raise Exception(f"Docling processing failed: {str(e)}")


@app.get("/")
def read_root():
    return {"message": "RAG Pro API - Modern Document Q&A"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document."""
    try:
        # Validate file type - Docling supports many formats
        supported_extensions = ('.pdf', '.docx', '.pptx', '.xlsx', '.html', '.png', '.jpg', '.jpeg', '.tiff')
        if not file.filename.lower().endswith(supported_extensions):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported: {', '.join(supported_extensions)}"
            )

        # Generate unique ID
        doc_id = str(uuid.uuid4())

        # Save file
        file_path = UPLOAD_DIR / f"{doc_id}_{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Extract text using Docling
        text = extract_text_with_docling(str(file_path))

        if not text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the document")

        # Split into chunks
        chunks = text_splitter.split_text(text)

        # Add metadata to chunks
        metadatas = [{"doc_id": doc_id, "filename": file.filename, "chunk_id": i} for i in range(len(chunks))]

        # Add to vector store
        vector_store.add_texts(chunks, metadatas=metadatas)

        # Store document info
        documents_db[doc_id] = {
            "filename": file.filename,
            "chunks": len(chunks),
            "path": str(file_path)
        }

        return {
            "message": "Document uploaded and processed successfully",
            "doc_id": doc_id,
            "filename": file.filename,
            "chunks": len(chunks)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the documents using improved RAG with reranking."""
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        # Step 1: Initial retrieval - Get more candidates
        initial_docs = vector_store.similarity_search(request.query, k=12)

        if not initial_docs:
            return ChatResponse(
                response="I couldn't find any relevant information in the uploaded documents.",
                sources=[]
            )

        # Step 2: Rerank documents using cross-encoder for better relevance
        # Create query-document pairs for reranking
        pairs = [[request.query, doc.page_content] for doc in initial_docs]

        # Get relevance scores
        scores = reranker.predict(pairs)

        # Sort documents by score and take top 5
        doc_score_pairs = list(zip(initial_docs, scores))
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
        reranked_docs = [doc for doc, score in doc_score_pairs[:5]]

        # Step 3: Build enhanced context with metadata
        context_parts = []
        for i, doc in enumerate(reranked_docs, 1):
            filename = doc.metadata.get("filename", "Unknown")
            context_parts.append(f"[Source {i}: {filename}]\n{doc.page_content}")

        context = "\n\n---\n\n".join(context_parts)

        # Step 4: Enhanced prompt with chain-of-thought reasoning
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
async def list_documents():
    """List all uploaded documents."""
    return [
        DocumentInfo(id=doc_id, filename=info["filename"], chunks=info["chunks"])
        for doc_id, info in documents_db.items()
    ]


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document."""
    if doc_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        # Delete file
        file_path = Path(documents_db[doc_id]["path"])
        if file_path.exists():
            file_path.unlink()

        # Note: Qdrant in-memory doesn't support deleting by metadata filter easily
        # In production, you'd use persistent Qdrant and delete by doc_id

        # Remove from db
        del documents_db[doc_id]

        return {"message": "Document deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
