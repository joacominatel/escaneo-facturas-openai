"use client"

import { useState } from "react"
import FileUpload from "@/components/FileUpload"
import ProgressDisplay from "@/components/ProgressDisplay"

export default function Home() {
  const [progress, setProgress] = useState<any[]>([])

  const handleProgressUpdate = (data: any) => {
    setProgress((prevProgress) => [...prevProgress, data])
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">PDF Analyzer</h1>
      <FileUpload onProgressUpdate={handleProgressUpdate} />
      <ProgressDisplay progress={progress} />
    </div>
  )
}

