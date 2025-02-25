"use client"

import { useState, useEffect } from "react"
import { useToast } from "@/hooks/use-toast"
import FileUpload from "@/components/FileUpload"
import InvoiceDisplay from "@/components/InvoiceDisplay"
import { Button } from "@/components/ui/button"

export default function Home() {
  const [invoices, setInvoices] = useState<Record<string, any>>({})
  const { toast } = useToast()

  useEffect(() => {
    const storedInvoiceIds = JSON.parse(localStorage.getItem("processedInvoices") || "[]")
    storedInvoiceIds.forEach((invoiceNumber: string) => {
      fetchInvoiceData(invoiceNumber)
    })
  }, [])

  const fetchInvoiceData = async (invoiceNumber: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api_v2/invoices/invoice_number/${invoiceNumber}`)
      if (response.ok) {
        const data = await response.json()
        console.log("Fetched invoice data:", data)
        setInvoices((prevInvoices) => ({
          ...prevInvoices,
          [data.invoice_number]: {
            ...data,
            status: "completed",
          },
        }))
      }
    } catch (error) {
      console.error(`Error fetching invoice data for ${invoiceNumber}:`, error)
    }
  }

  const handleProgressUpdate = (data: any) => {
    setInvoices((prevInvoices) => ({
      ...prevInvoices,
      [data.invoice_number]: {
        ...prevInvoices[data.invoice_number],
        ...data,
      },
    }))

    if (data.status === "completed" && data.invoice_number) {
      const storedInvoices = JSON.parse(localStorage.getItem("processedInvoices") || "[]")
      if (!storedInvoices.includes(data.invoice_number)) {
        storedInvoices.push(data.invoice_number)
        localStorage.setItem("processedInvoices", JSON.stringify(storedInvoices))
      }
    }
  }

  const deleteInvoice = (invoiceNumber: string) => {
    setInvoices((prevInvoices) => {
      const newInvoices = { ...prevInvoices }
      delete newInvoices[invoiceNumber]
      return newInvoices
    })

    const storedInvoices = JSON.parse(localStorage.getItem("processedInvoices") || "[]")
    const updatedInvoices = storedInvoices.filter((number: string) => number !== invoiceNumber)
    localStorage.setItem("processedInvoices", JSON.stringify(updatedInvoices))

    toast({
      title: "Invoice deleted",
      description: `Invoice ${invoiceNumber} has been removed from the history.`,
    })
  }

  const deleteAllInvoices = () => {
    setInvoices({})
    localStorage.removeItem("processedInvoices")
    toast({
      title: "All invoices deleted",
      description: "All invoices have been removed from the history.",
    })
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 text-center">Invoice Analyzer</h1>
      <FileUpload onProgressUpdate={handleProgressUpdate} />
      <div className="mt-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-semibold">Recent Invoices</h2>
          <Button variant="destructive" onClick={deleteAllInvoices}>
            Delete All
          </Button>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Object.entries(invoices).map(([invoiceNumber, invoice]) => (
            <InvoiceDisplay key={invoiceNumber} invoice={invoice} onDelete={() => deleteInvoice(invoiceNumber)} />
          ))}
        </div>
      </div>
    </div>
  )
}