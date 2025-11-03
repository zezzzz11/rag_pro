# Multi-User Authentication & Document Isolation

RAG Pro now supports **multi-user authentication** with **complete document isolation**. Each user's documents are private and secure.

## ✅ What's Implemented

### 1. **User Authentication**
- JWT token-based authentication
- Secure password hashing with bcrypt
- Registration and login endpoints
- 7-day token expiration

### 2. **Document Isolation**
- Each user can only access their own documents
- User ID stored with every document chunk in vector database
- Filtered retrieval ensures cross-user privacy
- File system isolation (documents stored in user-specific folders)

### 3. **Persistent Storage**
- SQLite database for user and document metadata
- Persistent Qdrant vector storage (no more in-memory)
- All data survives server restarts

### 4. **Security Features**
- Password hashing with bcrypt
- JWT tokens for stateless authentication
- Bearer token authentication on all protected endpoints
- User ownership validation on all operations

---

## 🚀 How It Works

### Registration Flow:
```
1. User enters email, username, password
2. Backend hashes password
3. Creates user record in database
4. Returns JWT token
5. Frontend stores token in localStorage
6. All subsequent requests include token
```

### Document Upload Flow:
```
1. User uploads document (with JWT token)
2. Backend extracts user_id from token
3. Saves file in /uploads/{user_id}/ directory
4. Processes document with Docling
5. Stores chunks with metadata: {user_id, doc_id, filename}
6. Adds to vector store with user_id filter
7. Creates database record
```

### Chat/Retrieval Flow:
```
1. User sends query (with JWT token)
2. Backend extracts user_id from token
3. Searches vector store WITH user_id filter
4. Only retrieves user's own documents
5. Reranks and generates answer
6. Returns response
```

---

## 📁 Storage Structure

### File System:
```
rag-pro/
├── backend/
│   ├── uploads/
│   │   ├── {user_id_1}/
│   │   │   ├── {doc_id}_document1.pdf
│   │   │   └── {doc_id}_document2.docx
│   │   └── {user_id_2}/
│   │       └── {doc_id}_document3.pdf
│   └── data/
│       ├── rag_pro.db (SQLite database)
│       └── qdrant/ (Vector embeddings)
```

### Database Schema:

**users table:**
```sql
id TEXT PRIMARY KEY           -- UUID
username TEXT UNIQUE          -- Display name
email TEXT UNIQUE            -- Login identifier
hashed_password TEXT         -- bcrypt hash
created_at TIMESTAMP         -- Registration date
```

**documents table:**
```sql
id TEXT PRIMARY KEY          -- Document UUID
user_id TEXT                 -- Owner (foreign key)
filename TEXT                -- Original filename
file_path TEXT               -- Location on disk
chunks INTEGER               -- Number of chunks
created_at TIMESTAMP         -- Upload date
```

### Vector Store Metadata:
```python
{
  "user_id": "uuid",        # For filtering
  "doc_id": "uuid",         # Document identifier
  "filename": "name.pdf",   # For display
  "chunk_id": 0             # Chunk index
}
```

---

## 🔒 Security Considerations

### What's Secure:
✅ Passwords are hashed (never stored in plaintext)
✅ JWT tokens expire after 7 days
✅ User ID verified on every request
✅ Vector search filtered by user_id
✅ File system isolation per user
✅ Database ownership checks

### What's NOT Production-Ready:
⚠️ SECRET_KEY should be changed (currently hardcoded)
⚠️ No HTTPS (use reverse proxy in production)
⚠️ No rate limiting
⚠️ No email verification
⚠️ No password reset flow
⚠️ No 2FA/MFA
⚠️ SQLite not recommended for high concurrency
⚠️ No backup/recovery system

---

## 🔧 Configuration

### Environment Variables (optional):

Create `/backend/.env`:
```bash
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days
```

### Change Token Expiration:
In `backend/auth.py`:
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
```

---

## 📊 API Endpoints

### Public Endpoints (no auth required):
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login existing user

### Protected Endpoints (requires Bearer token):
- `GET /auth/me` - Get current user info
- `POST /upload` - Upload document
- `POST /chat` - Chat with documents
- `GET /documents` - List user's documents
- `DELETE /documents/{id}` - Delete document

### Example API Usage:

**Register:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"testuser","password":"securepass"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securepass"}'
```

**Upload (with token):**
```bash
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@document.pdf"
```

**Chat (with token):**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"query":"What is this document about?"}'
```

---

## 🧪 Testing Multi-User Isolation

### Test Scenario:
1. Register User A and upload Document A
2. Register User B and upload Document B
3. User A queries → should only see Document A results
4. User B queries → should only see Document B results
5. User A tries to delete User B's document → 404 Not Found

### Manual Test:
```bash
# Register User A
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@test.com","username":"Alice","password":"pass123"}'
# Save token as TOKEN_A

# Register User B
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@test.com","username":"Bob","password":"pass456"}'
# Save token as TOKEN_B

# Upload as User A
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer $TOKEN_A" \
  -F "file=@doc_a.pdf"

# Upload as User B
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer $TOKEN_B" \
  -F "file=@doc_b.pdf"

# Query as User A - should only see doc_a results
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{"query":"test"}'

# List docs as User A - should only see doc_a
curl -X GET http://localhost:8000/documents \
  -H "Authorization: Bearer $TOKEN_A"
```

---

## 🐛 Troubleshooting

### "Could not validate credentials"
- Token expired (7 days)
- Token malformed
- **Solution:** Login again to get new token

### "Document not found" when deleting
- Document belongs to different user
- Document doesn't exist
- **Solution:** Check document ownership

### Documents not persisting after restart
- Check `/backend/data/` directory exists
- Check Qdrant path is correct
- **Solution:** Verify `QDRANT_PATH = Path("data/qdrant")`

### Can see other users' documents
- **This should never happen!**
- Check `user_filter` is applied in chat endpoint
- Verify metadata.user_id is set during upload
- **Critical security issue if true**

---

## 🚀 Production Deployment Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` to random secure value
- [ ] Enable HTTPS/TLS
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up database backups
- [ ] Add rate limiting (slowapi, etc.)
- [ ] Implement email verification
- [ ] Add password reset flow
- [ ] Set up monitoring and logging
- [ ] Use environment variables for all secrets
- [ ] Add CORS whitelist for production domain
- [ ] Set up reverse proxy (nginx)
- [ ] Configure persistent volume for Qdrant
- [ ] Add health check endpoints
- [ ] Implement audit logging
- [ ] Set up alerting for failures

---

## 📈 Scalability Notes

### Current Limitations:
- SQLite: ~100 concurrent users max
- In-process Qdrant: Limited to single server
- File storage: Limited to disk space

### For Production Scale:
- Migrate to PostgreSQL or MongoDB
- Use Qdrant Cloud or hosted instance
- Implement object storage (S3, MinIO)
- Add Redis for caching
- Implement load balancing
- Consider microservices architecture

---

## 🔐 Security Best Practices

### For Users:
- Use strong, unique passwords
- Don't share tokens
- Logout when done
- Tokens stored in localStorage (cleared on logout)

### For Developers:
- Never log passwords
- Sanitize all inputs
- Validate file types strictly
- Limit file sizes
- Implement rate limiting
- Monitor for suspicious activity
- Regular security audits
- Keep dependencies updated

---

## 📝 License & Legal

### Data Privacy:
- All documents stored locally
- No external API calls (except Ollama)
- User data never leaves your server
- GDPR compliant (with proper setup)

### User Rights:
Users can:
- Delete their documents at any time
- Export their data (implement custom endpoint)
- Request account deletion (implement custom endpoint)

---

**Status:** ✅ Fully Implemented and Working

**Tested:** User isolation verified
**Security:** Basic authentication implemented
**Production Ready:** Needs additional hardening (see checklist)
