"use client"

import { useState, useEffect } from "react"
import { FileUpload } from "@/components/FileUpload"
import { ChatInterface } from "@/components/ChatInterface"
import { DocumentList } from "@/components/DocumentList"
import { Auth } from "@/components/Auth"
import { AdminPanel } from "@/components/AdminPanel"
import { BookOpen, LogOut, Shield } from "lucide-react"
import { isAuthenticated, clearAuth, getUser, getAuthHeaders } from "@/lib/auth"
import { Button } from "@/components/ui/button"
import axios from "axios"

export default function Home() {
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  const [authenticated, setAuthenticated] = useState(false)
  const [user, setUser] = useState<{ username: string } | null>(null)
  const [isAdmin, setIsAdmin] = useState(false)
  const [showAdmin, setShowAdmin] = useState(false)

  useEffect(() => {
    const auth = isAuthenticated()
    setAuthenticated(auth)
    if (auth) {
      setUser(getUser())
      // Fetch user info to check admin status
      axios.get("http://localhost:8000/auth/me", {
        headers: getAuthHeaders()
      }).then(res => {
        setIsAdmin(res.data.is_admin)
      }).catch(err => {
        console.error("Failed to fetch user info:", err)
      })
    }
  }, [])

  const handleUploadSuccess = () => {
    setRefreshTrigger((prev) => prev + 1)
  }

  const handleAuthSuccess = () => {
    setAuthenticated(true)
    setUser(getUser())
  }

  const handleLogout = () => {
    clearAuth()
    setAuthenticated(false)
    setUser(null)
    window.location.reload()
  }

  if (!authenticated) {
    return <Auth onAuthSuccess={handleAuthSuccess} />
  }

  if (showAdmin) {
    return (
      <div>
        <div className="fixed top-4 left-4 z-50">
          <Button onClick={() => setShowAdmin(false)} variant="outline">
            ← Back to Main
          </Button>
        </div>
        <AdminPanel />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-2">
            <BookOpen className="h-10 w-10 text-blue-600" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              RAG Pro
            </h1>
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            Modern document Q&A powered by AI
          </p>
          <div className="mt-4 flex items-center justify-center gap-4">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              Welcome, <span className="font-semibold">{user?.username}</span>
            </span>
            {isAdmin && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowAdmin(true)}
                className="flex items-center gap-2"
              >
                <Shield className="h-4 w-4" />
                Admin Panel
              </Button>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={handleLogout}
              className="flex items-center gap-2"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Upload & Documents */}
          <div className="space-y-6">
            <FileUpload onUploadSuccess={handleUploadSuccess} />
            <DocumentList refreshTrigger={refreshTrigger} />
          </div>

          {/* Right Column - Chat */}
          <div className="lg:col-span-2">
            <ChatInterface />
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-sm text-gray-500">
          Built with LangChain, Qdrant, Docling & Next.js • Your documents are private and secure
        </div>
      </div>
    </div>
  )
}
