"use client"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Upload, FileUp, Cloud } from 'lucide-react'
import axios from "axios"

export default function AIChatAttachment() {
  const [file, setFile] = useState<File | null>(null)
  const [question, setQuestion] = useState("")
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  // get from environment variable
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api_v2"

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
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = (file: File) => {
    if (file.type === "application/pdf" || file.type === "application/zip") {
      setFile(file)
    } else {
      alert("Please upload only .pdf or .zip files")
    }
  }

  const onButtonClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click()
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // use next_public_api_url to send the file and question to the AI chat
    const formData = new FormData()
    formData.append("file", file as Blob)
    formData.append("question", question)
    const response = axios.post(`${API_URL}/process_invoices`, formData)
    console.log(response)
    alert("Files and question sent to AI chat")
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Attach File to AI Chat</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <div
              className={`border-2 border-dashed rounded-lg p-4 text-center ${
                dragActive ? "border-primary" : "border-gray-300"
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                onChange={handleChange}
                accept=".pdf,.zip"
              />
              {file ? (
                <p className="text-sm text-gray-500">{file.name}</p>
              ) : (
                <>
                  <Upload className="mx-auto h-12 w-12 text-gray-400" />
                  <p className="mt-2 text-sm text-gray-500">
                    Drag and drop a file here, or click to select a file
                  </p>
                </>
              )}
              <div className="mt-4 flex justify-center gap-4">
                <Button type="button" variant="outline" size="sm" onClick={onButtonClick}>
                  <FileUp className="mr-2 h-4 w-4" />
                  Upload from PC
                </Button>
                <Button type="button" variant="outline" size="sm">
                  <Cloud className="mr-2 h-4 w-4" />
                  OneDrive
                </Button>
              </div>
            </div>
            <div className="mt-4">
              <Textarea
                placeholder="Type your question here..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                className="min-h-[100px]"
              />
            </div>
          </form>
        </CardContent>
        <CardFooter>
          <Button className="w-full" type="submit" onClick={handleSubmit}>
            Submit
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}

