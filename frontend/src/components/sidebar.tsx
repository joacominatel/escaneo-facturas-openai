"use client"

import { Home, MessageSquare, Settings } from 'lucide-react'
import { usePathname } from "next/navigation"
import Link from "next/link"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/theme-toggle"

const sidebarItems = [
  { icon: Home, label: "Home", href: "/" },
  { icon: MessageSquare, label: "Chat", href: "/chat" },
  { icon: Settings, label: "Settings", href: "/settings" },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="flex h-full w-16 flex-col items-center space-y-8 bg-background py-4">
      {sidebarItems.map(({ icon: Icon, label, href }) => (
        <Link key={href} href={href}>
          <Button
            variant="ghost"
            size="icon"
            className={cn(
              "h-12 w-12",
              pathname === href && "bg-muted"
            )}
          >
            <Icon className="h-6 w-6" />
            <span className="sr-only">{label}</span>
          </Button>
        </Link>
      ))}
      <div className="flex-1" />
      <ThemeToggle />
    </div>
  )
}

