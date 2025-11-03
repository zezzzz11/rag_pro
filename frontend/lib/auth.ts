// Authentication utilities

export interface User {
  id: string
  username: string
  email: string
}

export interface AuthToken {
  access_token: string
  token_type: string
  user_id: string
  username: string
}

const TOKEN_KEY = "rag_pro_token"
const USER_KEY = "rag_pro_user"

export function setAuth(token: AuthToken) {
  localStorage.setItem(TOKEN_KEY, token.access_token)
  localStorage.setItem(USER_KEY, JSON.stringify({
    id: token.user_id,
    username: token.username
  }))
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function getUser(): { id: string; username: string } | null {
  const user = localStorage.getItem(USER_KEY)
  return user ? JSON.parse(user) : null
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function isAuthenticated(): boolean {
  return getToken() !== null
}

export function getAuthHeaders() {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}
