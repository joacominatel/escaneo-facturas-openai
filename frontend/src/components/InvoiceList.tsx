"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

interface Invoice {
  id: string
  invoice_number: string
  date: string
  total_amount: number
  // Add other relevant fields
}

const InvoiceList = () => {
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [page, setPage] = useState(1)
  const [totalInvoices, setTotalInvoices] = useState(0)

  const limit = 20

  useEffect(() => {
    const fetchInvoices = async () => {
      setLoading(true)
      setError(null)
      try {
        const offset = (page - 1) * limit
        const searchQuery = searchTerm ? `?search=${searchTerm}&offset=${offset}&limit=${limit}` : `?offset=${offset}&limit=${limit}`
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api_v2/invoices${searchQuery}`,
        )
        if (!response.ok) {
          throw new Error("Failed to fetch invoices")
        }
        const data = await response.json()
        setInvoices(data)
        setTotalInvoices(data.length)
      } catch (err) {
        setError("An error occurred while fetching invoices")
      } finally {
        setLoading(false)
      }
    }

    fetchInvoices()
  }, [searchTerm, page])

  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setPage(1)
  }

  const totalPages = Math.ceil(totalInvoices / limit)

  return (
    <div>
      <form onSubmit={handleSearch} className="mb-4 flex gap-2">
        <Input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search by advertising number"
          className="flex-grow"
        />
        <Button type="submit">Search</Button>
      </form>

      {loading && <p>Loading...</p>}
      {error && <p className="text-red-500">{error}</p>}

      {!loading && !error && (
        <>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Invoice Number</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Total Amount</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {invoices.map((invoice) => (
                <TableRow key={invoice.id}>
                  <TableCell>{invoice.invoice_number}</TableCell>
                  <TableCell>{invoice.date}</TableCell>
                  <TableCell>{invoice.total_amount}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <div className="mt-4 flex justify-between items-center">
            <Button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}>
              Previous
            </Button>
            <span>
              Page {page} of {totalPages}
            </span>
            <Button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages}>
              Next
            </Button>
          </div>
        </>
      )}
    </div>
  )
}

export default InvoiceList

