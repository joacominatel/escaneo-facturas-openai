"use client"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Upload, FileUp, Cloud, ChevronDown, ChevronUp, X, Loader } from 'lucide-react'
import { motion, AnimatePresence } from "framer-motion"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { InvoiceResultsWidget } from "@/components/invoice-results-widget"
import axios from "axios"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api_v2"

interface InvoiceResult {
  file_name: string
  file_id: string
  results: string[]
  status: string
}

export default function AIChatAttachment() {
  const [files, setFiles] = useState<File[]>([])
  const [question, setQuestion] = useState("")
  const [dragActive, setDragActive] = useState(false)
  const [isCollapsibleOpen, setIsCollapsibleOpen] = useState(false)
  const [notification, setNotification] = useState<{ type: 'success' | 'error', message: string } | null>(null)
  const [processedResults, setProcessedResults] = useState<InvoiceResult[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isLoading, setIsLoading] = useState(false)

  // test data for InvoiceResultsWidget

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
    if (e.dataTransfer.files) {
      handleFiles(Array.from(e.dataTransfer.files))
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault()
    if (e.target.files) {
      handleFiles(Array.from(e.target.files))
    }
  }

  const handleFiles = (newFiles: File[]) => {
    const validFiles = newFiles.filter(file => 
      file.type === "application/pdf" || file.type === "application/zip" || file.name.endsWith('.zip')
    )
    // if (validFiles.length + files.length > 10) {
    //   showNotification('error', 'You can upload a maximum of 10 files.')
    //   return
    // }
    if (validFiles.length !== newFiles.length) {
      showNotification('error', 'Please upload only .pdf files.')
    }
    setFiles(prevFiles => [...prevFiles, ...validFiles].slice(0, 10))
  }

  const removeFile = (index: number) => {
    setFiles(prevFiles => prevFiles.filter((_, i) => i !== index))
  }

  const onButtonClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click()
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    if (files.length === 0) {
      showNotification('error', 'Please upload at least one file.')
      return
    }

    const formData = new FormData()
    files.forEach(file => formData.append("files", file))
    formData.append("question", question)
    
    try {
      const response = await axios.post(`${API_URL}/analyze`, formData)
      console.log(response)
      if (response) {
        setProcessedResults(prevResults => [...prevResults, ...response.data])      }
      showNotification('success', 'Files and question sent to AI chat.')
      setFiles([])
      setQuestion("")
    } catch (error) {
      console.error(error)
      showNotification('error', 'Failed to send files and question to AI chat.')
    } finally {
      setIsLoading(false)
    }
  }

  const showNotification = (type: 'success' | 'error', message: string) => {
    setNotification({ type, message })
    setTimeout(() => setNotification(null), 3000)
  }

  const fileSummary = () => {
    const zipCount = files.filter(file => file.type === "application/zip" || file.name.endsWith('.zip')).length
    const pdfCount = files.filter(file => file.type === "application/pdf").length
    return `${zipCount} .zip ${zipCount === 1 ? 'file' : 'files'} - ${pdfCount} .pdf ${pdfCount === 1 ? 'file' : 'files'}`
  }

  const handleDeleteAllResults = () => {
    setProcessedResults([])
    showNotification('success', 'All invoice results deleted.')
  }

  const handleDeleteOneResult = (index: number) => {
    setProcessedResults(prevResults => prevResults.filter((_, i) => i !== index))
    showNotification('success', 'Invoice result deleted.')
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Attach Files to AI Chat</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <div
              className={`border-2 border-dashed rounded-lg p-4 text-center ${
                dragActive ? "border-primary" : "border-input"
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
                multiple
              />
              {files.length > 0 ? (
                <Collapsible
                  open={isCollapsibleOpen}
                  onOpenChange={setIsCollapsibleOpen}
                  className="w-full"
                >
                  <div className="flex justify-between items-center">
                    <p className="text-sm text-muted-foreground">{fileSummary()}</p>
                    <CollapsibleTrigger asChild>
                      <Button variant="ghost" size="sm" className="p-0">
                        {isCollapsibleOpen ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                      </Button>
                    </CollapsibleTrigger>
                  </div>
                  <CollapsibleContent className="mt-2">
                    <ul className="space-y-1">
                      {files.map((file, index) => (
                        <li key={index} className="flex justify-between items-center text-sm">
                          <span className="truncate">{file.name}</span>
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => removeFile(index)}
                            className="ml-2 p-0 h-6 w-6"
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </li>
                      ))}
                    </ul>
                  </CollapsibleContent>
                </Collapsible>
              ) : (
                <>
                  <Upload className="mx-auto h-12 w-12 text-muted-foreground" />
                  <p className="mt-2 text-sm text-muted-foreground">
                    Drag and drop files here, or click to select files
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
          {isLoading ? (
              <>
                <Loader className="mr-2 h-4 w-4 animate-spin" />
                Submitting...
              </>
            ) : (
              'Submit'
            )}
          </Button>
        </CardFooter>
      </Card>
      <InvoiceResultsWidget 
        results={processedResults}
        onDeleteAll={handleDeleteAllResults}
        onDeleteOne={handleDeleteOneResult}
      />
      <AnimatePresence>
        {notification && (
          <motion.div
            initial={{ opacity: 0, y: 50, x: "-50%" }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className={`fixed bottom-4 left-1/2 transform -translate-x-1/2 px-4 py-2 rounded-md text-white ${
              notification.type === 'success' ? 'bg-green-500' : 'bg-red-500'
            }`}
          >
            {notification.message}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

