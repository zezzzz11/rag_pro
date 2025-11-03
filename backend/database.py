"""Simple SQLite database for user and document management."""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

DATABASE_PATH = Path("data/rag_pro.db")
DATABASE_PATH.parent.mkdir(exist_ok=True)


def get_db():
    """Get database connection."""
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables."""
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            chunks INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# User operations
def create_user(user_id: str, username: str, email: str, hashed_password: str, is_admin: bool = False):
    """Create a new user."""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (id, username, email, hashed_password, is_admin) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, email, hashed_password, 1 if is_admin else 0)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Get user by ID."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


# Document operations
def create_document(doc_id: str, user_id: str, filename: str, file_path: str, chunks: int):
    """Create a document record."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO documents (id, user_id, filename, file_path, chunks) VALUES (?, ?, ?, ?, ?)",
        (doc_id, user_id, filename, file_path, chunks)
    )
    conn.commit()
    conn.close()


def get_user_documents(user_id: str) -> List[Dict]:
    """Get all documents for a user."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, filename, chunks, created_at FROM documents WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_document(doc_id: str, user_id: str) -> Optional[Dict]:
    """Get a specific document (with ownership check)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM documents WHERE id = ? AND user_id = ?",
        (doc_id, user_id)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def delete_document(doc_id: str, user_id: str) -> bool:
    """Delete a document (with ownership check)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM documents WHERE id = ? AND user_id = ?",
        (doc_id, user_id)
    )
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# Admin operations
def get_all_users() -> List[Dict]:
    """Get all users (admin only)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, email, is_admin, created_at FROM users ORDER BY created_at DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_documents() -> List[Dict]:
    """Get all documents across all users (admin only)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.id, d.filename, d.chunks, d.created_at, d.user_id, u.username, u.email
        FROM documents d
        JOIN users u ON d.user_id = u.id
        ORDER BY d.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_user_admin(user_id: str) -> bool:
    """Delete a user and all their documents (admin only)."""
    conn = get_db()
    cursor = conn.cursor()
    try:
        # Delete user's documents first
        cursor.execute("DELETE FROM documents WHERE user_id = ?", (user_id,))
        # Delete user
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        return deleted
    finally:
        conn.close()


def delete_document_admin(doc_id: str) -> bool:
    """Delete any document (admin only, no ownership check)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def get_stats() -> Dict:
    """Get system statistics (admin only)."""
    conn = get_db()
    cursor = conn.cursor()

    # Total users
    cursor.execute("SELECT COUNT(*) as count FROM users")
    total_users = cursor.fetchone()['count']

    # Total documents
    cursor.execute("SELECT COUNT(*) as count FROM documents")
    total_documents = cursor.fetchone()['count']

    # Total chunks
    cursor.execute("SELECT SUM(chunks) as total FROM documents")
    total_chunks = cursor.fetchone()['total'] or 0

    conn.close()

    return {
        "total_users": total_users,
        "total_documents": total_documents,
        "total_chunks": total_chunks
    }


# Initialize database on module import
init_db()
