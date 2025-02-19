"use client"

import { useState, useEffect } from "react"
import FileUpload from "@/components/FileUpload"
import InvoiceDisplay from "@/components/InvoiceDisplay"

export default function Home() {
  const [invoices, setInvoices] = useState<Record<string, any>>({})

  useEffect(() => {
    // Recuperar los IDs de las facturas del localStorage
    const storedInvoiceIds = JSON.parse(localStorage.getItem("processedInvoices") || "[]")

    // Obtener los datos completos de cada factura
    storedInvoiceIds.forEach((invoiceNumber: string) => {
      fetchInvoiceData(invoiceNumber)
    })
  }, [])

  const fetchInvoiceData = async (invoiceNumber: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api_v2/invoices/${invoiceNumber}`)
      if (response.ok) {
        const data = await response.json()
        setInvoices((prevInvoices) => ({
          ...prevInvoices,
          [data.filename]: {
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
      [data.filename]: {
        ...prevInvoices[data.filename],
        ...data,
      },
    }))

    // Si el estado es 'completed', guardar el número de factura en localStorage
    if (data.status === "completed" && data.data && data.data.invoice_number) {
      const storedInvoices = JSON.parse(localStorage.getItem("processedInvoices") || "[]")
      if (!storedInvoices.includes(data.data.invoice_number)) {
        storedInvoices.push(data.data.invoice_number)
        localStorage.setItem("processedInvoices", JSON.stringify(storedInvoices))
      }
    }
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 text-center">Invoice Analyzer</h1>
      <FileUpload onProgressUpdate={handleProgressUpdate} />
      <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {Object.entries(invoices).map(([filename, invoice]) => (
          <InvoiceDisplay key={filename} invoice={invoice} />
        ))}
      </div>
    </div>
  )
}