"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { Button } from "./ui/button"
import axios from "axios"
import { getAuthHeaders } from "@/lib/auth"
import { Users, FileText, Database, Trash2, Shield } from "lucide-react"

interface User {
  id: string
  username: string
  email: string
  is_admin: number
  created_at: string
}

interface Document {
  id: string
  filename: string
  chunks: number
  created_at: string
  user_id: string
  username: string
  email: string
}

interface Stats {
  total_users: number
  total_documents: number
  total_chunks: number
}

export function AdminPanel() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [users, setUsers] = useState<User[]>([])
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<"stats" | "users" | "documents">("stats")
  const [error, setError] = useState("")

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      setError("")

      // Load stats
      const statsRes = await axios.get(`/api/admin/stats`, {
        headers: getAuthHeaders(),
      })
      setStats(statsRes.data)

      // Load users
      const usersRes = await axios.get(`/api/admin/users`, {
        headers: getAuthHeaders(),
      })
      setUsers(usersRes.data.users)

      // Load documents
      const docsRes = await axios.get(`/api/admin/documents`, {
        headers: getAuthHeaders(),
      })
      setDocuments(docsRes.data.documents)
    } catch (err: any) {
      if (err.response?.status === 403) {
        setError("Admin access required")
      } else if (err.response?.status === 401) {
        setError("Authentication failed. Please login again.")
      } else {
        setError("Failed to load admin data")
      }
    } finally {
      setLoading(false)
    }
  }

  const deleteUser = async (userId: string, username: string) => {
    if (!confirm(`Are you sure you want to delete user "${username}" and all their documents?`)) {
      return
    }

    try {
      await axios.delete(`/api/admin/users/${userId}`, {
        headers: getAuthHeaders(),
      })
      loadData()
    } catch (err: any) {
      if (err.response?.status === 401 || err.response?.status === 403) {
        alert("Authentication failed. Please refresh the page to login again.")
        window.location.reload()
      } else {
        alert(err.response?.data?.detail || "Failed to delete user")
      }
    }
  }

  const deleteDocument = async (docId: string, filename: string) => {
    if (!confirm(`Are you sure you want to delete document "${filename}"?`)) {
      return
    }

    try {
      await axios.delete(`/api/admin/documents/${docId}`, {
        headers: getAuthHeaders(),
      })
      loadData()
    } catch (err: any) {
      if (err.response?.status === 401 || err.response?.status === 403) {
        alert("Authentication failed. Please refresh the page to login again.")
        window.location.reload()
      } else {
        alert(err.response?.data?.detail || "Failed to delete document")
      }
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-xl">Loading admin panel...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-red-600">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{error}</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Shield className="h-8 w-8" />
            Admin Control Panel
          </h1>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          <Button
            onClick={() => setActiveTab("stats")}
            variant={activeTab === "stats" ? "default" : "outline"}
          >
            <Database className="h-4 w-4 mr-2" />
            Statistics
          </Button>
          <Button
            onClick={() => setActiveTab("users")}
            variant={activeTab === "users" ? "default" : "outline"}
          >
            <Users className="h-4 w-4 mr-2" />
            Users ({users.length})
          </Button>
          <Button
            onClick={() => setActiveTab("documents")}
            variant={activeTab === "documents" ? "default" : "outline"}
          >
            <FileText className="h-4 w-4 mr-2" />
            Documents ({documents.length})
          </Button>
        </div>

        {/* Stats Tab */}
        {activeTab === "stats" && stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Total Users
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold">{stats.total_users}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Total Documents
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold">{stats.total_documents}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  Total Chunks
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold">{stats.total_chunks}</div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === "users" && (
          <Card>
            <CardHeader>
              <CardTitle>All Users</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {users.map((user) => (
                  <div
                    key={user.id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div>
                      <div className="font-semibold flex items-center gap-2">
                        {user.username}
                        {user.is_admin === 1 && (
                          <span className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded">
                            Admin
                          </span>
                        )}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        {user.email}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-500">
                        Created: {new Date(user.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    {user.is_admin !== 1 && (
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => deleteUser(user.id, user.username)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Documents Tab */}
        {activeTab === "documents" && (
          <Card>
            <CardHeader>
              <CardTitle>All Documents</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div>
                      <div className="font-semibold">{doc.filename}</div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">
                        Owner: {doc.username} ({doc.email})
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-500">
                        {doc.chunks} chunks • Uploaded: {new Date(doc.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => deleteDocument(doc.id, doc.filename)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
