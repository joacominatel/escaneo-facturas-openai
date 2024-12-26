"use client"

import React, { useState, useEffect, useRef, useCallback } from 'react'
import axios from 'axios'
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { Button } from "@/components/ui/button"
import { ChevronDown, RefreshCw } from 'lucide-react'
import { useRouter } from 'next/navigation'

interface Invoice {
  id: string
  invoice_number: string
  amount: number
  date: string
  bill_to: string
  billing_period: string
  currency: string
  invoice_total: number
  items: {
    description: string
    advertising_number: string[]
    subtotal: number
  }[]
  payment_terms: string
  subtotal: number
  vat: number
  created_at: string
  updated_at: string
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api_v2"

export function InvoiceList() {
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)
  const [filter, setFilter] = useState('')

  const observer = useRef<IntersectionObserver | null>(null)
  const lastInvoiceElementRef = useCallback((node: HTMLTableRowElement | null) => {
    if (loading) return
    if (observer.current) observer.current.disconnect()
    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        setPage(prevPage => prevPage + 1)
      }
    })
    if (node) observer.current.observe(node)
  }, [loading, hasMore])

  const fetchInvoices = useCallback(async () => {
    if (loading || !hasMore) return
    setLoading(true)
    setError(null)
    try {
      const response = await axios.get(`${API_URL}/invoices?page=${page}&limit=20${filter ? `&filter=${filter}` : ''}`)
      setInvoices(prevInvoices => {
        const newInvoices: Invoice[] = response.data.filter((newInvoice: Invoice) =>
          !prevInvoices.some((prevInvoice: Invoice) => prevInvoice.id === newInvoice.id)
        )
        return [...prevInvoices, ...newInvoices]
      })
      setHasMore(response.data.length === 20)
      console.log(response.data)
    } catch (err) {
      setError('An error occurred while fetching invoices')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }, [page, filter, loading, hasMore])

  useEffect(() => {
    fetchInvoices()
  }, [fetchInvoices, page])

  useEffect(() => {
    setInvoices([])
    setPage(1)
    setHasMore(true)
  }, [filter])

  const router = useRouter()

  useEffect(() => {
    setInvoices([])
    setPage(1)
    setHasMore(true)
    setFilter('')

    // clean up
    return () => {
      setInvoices([])
      setPage(1)
      setHasMore(true)
      setFilter('')
    }
  }, [router])

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFilter(e.target.value)
  }

  const handleReload = useCallback(() => {
    setInvoices([])
    setPage(1)
    setHasMore(true)
    setFilter('')
  }, [fetchInvoices])

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Invoices</CardTitle>
        <div className='flex justify-between items-center mt-4'>
          <Input
            placeholder="Filter by advertising number"
            value={filter}
            onChange={handleFilterChange}
            className="max-w-sm"
          />
          <Button
            onClick={handleReload}
            variant="outline"
            size="icon"
            >
            <RefreshCw className="h-4 w-4" />
            <span className="sr-only">Reload</span>
            </Button>
        </div>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Invoice Number</TableHead>
              <TableHead>Items</TableHead>
              <TableHead>Amount</TableHead>
              <TableHead>Date</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {invoices.map((invoice, index) => (
              <TableRow
                key={invoice.id}
                ref={index === invoices.length - 1 ? lastInvoiceElementRef : null}
              >
                <TableCell>{invoice.invoice_number}</TableCell>
                <TableCell>
                  <Collapsible>
                    <CollapsibleTrigger asChild>
                      <Button variant="ghost" size="sm">
                        {invoice.items.length} items ({invoice.items.reduce((acc, item) => acc + item.advertising_number.length, 0)} OPs)
                        <ChevronDown className="h-4 w-4 ml-2" />
                      </Button>
                    </CollapsibleTrigger>
                    <CollapsibleContent>
                      {invoice.items.map((item, itemIndex) => (
                        <div key={itemIndex} className="mt-2">
                          <strong>{item.description}</strong>: {item.advertising_number.join(', ')}
                        </div>
                      ))}
                    </CollapsibleContent>
                  </Collapsible>
                </TableCell>                <TableCell>{invoice.amount}</TableCell>
                <TableCell>{invoice.date}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        {loading && <p className="text-center mt-4">Loading...</p>}
        {error && <p className="text-center mt-4 text-red-500">{error}</p>}
      </CardContent>
    </Card>
  )
}

