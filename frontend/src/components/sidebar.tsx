"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Home, FileText } from "lucide-react"

const Sidebar = () => {
  const pathname = usePathname()

  return (
    <aside className="bg-gray-800 text-white w-16 flex flex-col items-center py-4">
      <Link href="/" className={`mb-4 p-2 rounded ${pathname === "/" ? "bg-gray-700" : ""}`}>
        <Home size={24} />
      </Link>
      <Link href="/invoices" className={`mb-4 p-2 rounded ${pathname === "/invoices" ? "bg-gray-700" : ""}`}>
        <FileText size={24} />
      </Link>
    </aside>
  )
}

export default Sidebar