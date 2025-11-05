"use client"

import { useEffect, useState } from "react"
import { FileText, Trash2 } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { Button } from "./ui/button"
import axios from "axios"
import { getAuthHeaders } from "@/lib/auth"

interface Document {
  id: string
  filename: string
  chunks: number
}

interface DocumentListProps {
  refreshTrigger: number
}

export function DocumentList({ refreshTrigger }: DocumentListProps) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(false)

  const fetchDocuments = async () => {
    setLoading(true)
    try {
      const response = await axios.get("http://localhost:8000/documents", {
        headers: getAuthHeaders()
      })
      setDocuments(response.data)
    } catch (error: any) {
      console.error("Failed to fetch documents:", error)
      // If authentication fails, clear the document list
      if (error.response?.status === 401 || error.response?.status === 403) {
        setDocuments([])
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [refreshTrigger])

  const handleDelete = async (id: string) => {
    try {
      await axios.delete(`http://localhost:8000/documents/${id}`, {
        headers: getAuthHeaders()
      })
      fetchDocuments()
    } catch (error: any) {
      console.error("Failed to delete document:", error)
      // If authentication fails, refresh the page to force re-login
      if (error.response?.status === 401 || error.response?.status === 403) {
        alert("Authentication failed. Please login again.")
        window.location.reload()
      }
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Uploaded Documents</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <p className="text-sm text-gray-500">Loading...</p>
        ) : documents.length === 0 ? (
          <p className="text-sm text-gray-500">No documents uploaded yet</p>
        ) : (
          <div className="space-y-2">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <div className="flex items-center gap-3 flex-1">
                  <FileText className="h-5 w-5 text-blue-600" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{doc.filename}</p>
                    <p className="text-xs text-gray-500">{doc.chunks} chunks</p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDelete(doc.id)}
                  className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
