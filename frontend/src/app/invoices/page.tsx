import InvoiceList from "@/components/InvoiceList"

export default function InvoicesPage() {
  return (
    <div className="container mx-auto">
      <h1 className="text-3xl font-bold mb-4">Invoices</h1>
      <InvoiceList />
    </div>
  )
}

