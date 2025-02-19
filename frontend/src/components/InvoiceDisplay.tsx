"use client"

import { useState } from "react"
import { ChevronDown, ChevronUp, FileText, Loader, AlertCircle, Trash2 } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"

interface InvoiceDisplayProps {
  invoice: {
    invoice_number: string
    date: string
    amount: string
    bill_to: string
    items: Array<{ description: string; subtotal: string }>
    status: string
  }
  onDelete: () => void
}

export default function InvoiceDisplay({ invoice, onDelete }: InvoiceDisplayProps) {
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
            <span className="font-semibold">Invoice: {invoice.invoice_number}</span>
          </div>
          <div className="flex items-center">
            {getStatusIcon()}
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                onDelete()
              }}
            >
              <Trash2 className="h-4 w-4 text-red-500" />
            </Button>
          </div>
        </div>
        <p className="text-sm text-gray-600 mt-1">Date: {invoice.date}</p>
        <p className="text-sm text-gray-600">Amount: ${invoice.amount}</p>
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
              <p className="text-sm">
                <strong>Bill To:</strong> {invoice.bill_to}
              </p>
              <h4 className="font-semibold mt-2 mb-1">Items:</h4>
              <ul className="text-sm">
                {invoice.items.map((item, index) => (
                  <li key={index}>
                    <p>
                      <strong>Description:</strong> {item.description}
                    </p>
                    <p>
                      <strong>Subtotal:</strong> ${item.subtotal}
                    </p>
                  </li>
                ))}
              </ul>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}