"use client"

import { useState, useRef } from "react"
import { Upload, FileText, X } from "lucide-react"
import { Button } from "./ui/button"
import { Card, CardContent } from "./ui/card"
import axios from "axios"
import { getAuthHeaders } from "@/lib/auth"

interface FileUploadProps {
  onUploadSuccess: () => void
}

export function FileUpload({ onUploadSuccess }: FileUploadProps) {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")
  const inputRef = useRef<HTMLInputElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0]
      const validExtensions = [".pdf", ".docx", ".pptx", ".xlsx", ".html", ".png", ".jpg", ".jpeg", ".tiff"]
      const isValid = validExtensions.some(ext => droppedFile.name.toLowerCase().endsWith(ext))

      if (isValid) {
        setFile(droppedFile)
        setError("")
      } else {
        setError("Supported: PDF, DOCX, PPTX, XLSX, HTML, PNG, JPG, TIFF")
      }
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setError("")
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file")
      return
    }

    setUploading(true)
    setMessage("")
    setError("")

    const formData = new FormData()
    formData.append("file", file)

    try {
      const response = await axios.post(`/api/upload`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          ...getAuthHeaders()
        },
      })

      setMessage(`✓ ${response.data.message} (${response.data.chunks} chunks)`)
      setFile(null)
      if (inputRef.current) inputRef.current.value = ""
      onUploadSuccess()
    } catch (err: any) {
      // Handle authentication errors specifically
      if (err.response?.status === 401 || err.response?.status === 403) {
        setError("Authentication failed. Please refresh the page to login again.")
      } else {
        setError(err.response?.data?.detail || "Upload failed")
      }
    } finally {
      setUploading(false)
    }
  }

  return (
    <Card>
      <CardContent className="p-6">
        <h2 className="text-xl font-semibold mb-4">Upload Document</h2>

        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive
              ? "border-blue-500 bg-blue-50 dark:bg-blue-950"
              : "border-gray-300 dark:border-gray-700"
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.docx,.pptx,.xlsx,.html,.png,.jpg,.jpeg,.tiff"
            onChange={handleFileChange}
            className="hidden"
            id="file-upload"
          />

          {file ? (
            <div className="flex items-center justify-center gap-2">
              <FileText className="h-6 w-6 text-blue-600" />
              <span className="font-medium">{file.name}</span>
              <button
                onClick={() => setFile(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          ) : (
            <>
              <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p className="mb-2 text-sm text-gray-600 dark:text-gray-400">
                <label
                  htmlFor="file-upload"
                  className="font-semibold text-blue-600 hover:text-blue-700 cursor-pointer"
                >
                  Click to upload
                </label>{" "}
                or drag and drop
              </p>
              <p className="text-xs text-gray-500">PDF, DOCX, PPTX, XLSX, HTML, Images</p>
            </>
          )}
        </div>

        <Button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="w-full mt-4"
        >
          {uploading ? "Uploading..." : "Upload & Process"}
        </Button>

        {message && (
          <div className="mt-4 p-3 bg-green-50 dark:bg-green-950 text-green-700 dark:text-green-300 rounded-md text-sm">
            {message}
          </div>
        )}
        {error && (
          <div className="mt-4 p-3 bg-red-50 dark:bg-red-950 text-red-700 dark:text-red-300 rounded-md text-sm">
            {error}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
