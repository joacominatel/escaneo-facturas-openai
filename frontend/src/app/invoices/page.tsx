import { InvoiceList } from "@/components/invoice-list"

export default function InvoicesPage() {
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6">Invoices</h1>
      <InvoiceList />
    </div>
  )
}

