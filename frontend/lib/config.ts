// Backend URL for server-side API calls (Next.js API routes)
// In Docker: uses container name, In local dev: uses localhost
export const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

// Frontend now calls its own API routes at /api/*
// No need for NEXT_PUBLIC_API_URL anymore
