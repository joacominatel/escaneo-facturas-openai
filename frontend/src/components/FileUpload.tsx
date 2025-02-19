"use client"

import type React from "react"

import { useState, useEffect, useCallback } from "react"
import { io, type Socket } from "socket.io-client"
import { Upload, File, X } from "lucide-react"
import { useDropzone } from "react-dropzone"

interface FileUploadProps {
  onProgressUpdate: (data: any) => void
}

export default function FileUpload({ onProgressUpdate }: FileUploadProps) {
  const [files, setFiles] = useState<File[]>([])
  const [socket, setSocket] = useState<Socket | null>(null)
  const [isUploading, setIsUploading] = useState(false)

  useEffect(() => {
    const newSocket = io(process.env.NEXT_PUBLIC_API_URL || "http://localhost:3000")
    setSocket(newSocket)

    return () => {
      newSocket.disconnect()
    }
  }, [])

  useEffect(() => {
    if (socket) {
      socket.on("progress", (data) => {
        onProgressUpdate(data)
      })
    }
  }, [socket, onProgressUpdate])

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles((prevFiles) => [...prevFiles, ...acceptedFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
  })

  const removeFile = (fileToRemove: File) => {
    setFiles((prevFiles) => prevFiles.filter((file) => file !== fileToRemove))
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!files.length || !socket || isUploading) return

    setIsUploading(true)
    const formData = new FormData()
    files.forEach((file) => {
      formData.append("files", file)
    })
    if (socket.id) {
      formData.append("socket_id", socket.id)
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api_v2/analyze`, {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error("File upload failed")
      }

      const result = await response.json()
      console.log("Upload successful:", result)

      // Actualizar el estado de las facturas subidas
      files.forEach((file) => {
        onProgressUpdate({
          filename: file.name,
          status: "uploading",
          message: "File uploaded, waiting for analysis",
        })
      })
    } catch (error) {
      console.error("Error uploading file:", error)
      // Actualizar el estado de las facturas con error
      files.forEach((file) => {
        onProgressUpdate({
          filename: file.name,
          status: "error",
          message: "Error uploading file",
        })
      })
    } finally {
      setIsUploading(false)
      setFiles([])
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mb-4">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-300"
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-gray-400" />
        <p className="mt-2 text-sm text-gray-600">Drag 'n' drop some PDF files here, or click to select files</p>
      </div>
      {files.length > 0 && (
        <div className="mt-4">
          <h3 className="text-lg font-semibold mb-2">Selected Files:</h3>
          <ul className="space-y-2">
            {files.map((file) => (
              <li key={file.name} className="flex items-center justify-between bg-gray-100 p-2 rounded">
                <div className="flex items-center">
                  <File className="h-5 w-5 mr-2 text-gray-500" />
                  <span className="text-sm">{file.name}</span>
                </div>
                <button type="button" onClick={() => removeFile(file)} className="text-red-500 hover:text-red-700">
                  <X className="h-5 w-5" />
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
      <button
        type="submit"
        className={`mt-4 w-full bg-blue-500 text-white px-4 py-2 rounded transition-colors ${
          files.length && !isUploading ? "hover:bg-blue-600" : "opacity-50 cursor-not-allowed"
        }`}
        disabled={!files.length || isUploading}
      >
        {isUploading ? "Uploading..." : "Upload and Analyze"}
      </button>
    </form>
  )
}