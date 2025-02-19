"use client"

import { useState } from "react"
import { ChevronDown, ChevronUp, FileText, Loader, AlertCircle } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

interface InvoiceDisplayProps {
  invoice: any
}

export default function InvoiceDisplay({ invoice }: InvoiceDisplayProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const toggleExpand = () => {
    if (invoice.status === "completed") {
      setIsExpanded(!isExpanded)
    }
  }

  const getStatusIcon = () => {
    switch (invoice.status) {
      case "completed":
        return isExpanded ? (
          <ChevronUp className="h-5 w-5 text-gray-500" />
        ) : (
          <ChevronDown className="h-5 w-5 text-gray-500" />
        )
      case "error":
        return <AlertCircle className="h-5 w-5 text-red-500" />
      default:
        return <Loader className="h-5 w-5 text-blue-500 animate-spin" />
    }
  }

  return (
    <div className="bg-white shadow-md rounded-lg overflow-hidden">
      <div
        className={`p-4 cursor-pointer ${invoice.status === "completed" ? "hover:bg-gray-50" : ""}`}
        onClick={toggleExpand}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <FileText className="h-6 w-6 text-blue-500 mr-2" />
            <span className="font-semibold">{invoice.filename}</span>
          </div>
          {getStatusIcon()}
        </div>
        <p className="text-sm text-gray-600 mt-1">{invoice.message}</p>
      </div>
      <AnimatePresence>
        {isExpanded && invoice.status === "completed" && (
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: "auto" }}
            exit={{ height: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="p-4 bg-gray-50 border-t">
              <h3 className="font-semibold mb-2">Invoice Details:</h3>
              <pre className="text-sm overflow-x-auto">{JSON.stringify(invoice.data, null, 2)}</pre>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}