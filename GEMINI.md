# GEMINI.md

This file provides an overview of the RAG Pro project, a multi-user, document-based question-answering system.

## Project Overview

The project consists of two main components:

*   **`rag-pro`**: A sophisticated, multi-user RAG (Retrieval-Augmented Generation) application with a web-based interface. It allows users to register, upload documents, and ask questions about them. The backend uses a vector database (Qdrant) for efficient document retrieval and a large language model (Ollama) for generating answers.
*   **Root Directory Project**: A simpler, single-user RAG application. This was likely an initial prototype.

## `rag-pro` Application

### Architecture

*   **Frontend**: A Next.js/React application providing the user interface for authentication, file uploads, and chat.
*   **Backend**: A Python/FastAPI application that handles user authentication, document processing, and the RAG pipeline.

### Technologies Used

*   **Frontend**:
    *   Next.js
    *   React
    *   TypeScript
    *   Tailwind CSS
*   **Backend**:
    *   Python
    *   FastAPI
    *   LangChain
    *   Qdrant (Vector Store)
    *   Ollama (LLM)
    *   Hugging Face Transformers (Embeddings)
    *   Docling (Document Conversion)

### How to Run the `rag-pro` Project

1.  **Start the Backend**:
    *   Navigate to the `rag-pro/backend` directory.
    *   Install dependencies: `pip install -r requirements.txt`
    *   Run the setup script: `bash setup.sh`
    *   Start the backend server: `bash start-backend.sh`

2.  **Start the Frontend**:
    *   Navigate to the `rag-pro/frontend` directory.
    *   Install dependencies: `npm install`
    *   Start the frontend development server: `npm run dev`

3.  **Access the Application**:
    *   Open your web browser and go to `http://localhost:3000`.

## Root Directory Project

This is a simpler version of the RAG application.

### How to Run the Root Directory Project

1.  **Start the Backend**:
    *   Navigate to the `backend` directory.
    *   Install dependencies: `pip install -r requirements.txt`
    *   Start the backend server: `uvicorn main:app --host 0.0.0.0 --port 8001`

2.  **Start the Frontend**:
    *   Navigate to the `frontend` directory.
    *   Install dependencies: `npm install`
    *   Start the frontend development server: `npm start`

3.  **Access the Application**:
    *   Open your web browser and go to `http://localhost:3000`.
