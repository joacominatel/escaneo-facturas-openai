"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { io, type Socket } from "socket.io-client"

interface FileUploadProps {
  onProgressUpdate: (data: any) => void
}

export default function FileUpload({ onProgressUpdate }: FileUploadProps) {
  const [files, setFiles] = useState<FileList | null>(null)
  const [socket, setSocket] = useState<Socket | null>(null)

  useEffect(() => {
    const newSocket = io(process.env.NEXT_PUBLIC_API_URL)
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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(e.target.files)
    }
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!files || !socket) return

    const formData = new FormData()
    for (let i = 0; i < files.length; i++) {
      formData.append("files", files[i])
    }
    formData.append("socket_id", socket.id)

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
    } catch (error) {
      console.error("Error uploading file:", error)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mb-4">
      <input type="file" onChange={handleFileChange} multiple accept=".pdf" className="mb-2" />
      <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded" disabled={!files}>
        Upload and Analyze
      </button>
    </form>
  )
}

