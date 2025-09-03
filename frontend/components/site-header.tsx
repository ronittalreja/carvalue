"use client"

import Link from "next/link"
import Image from "next/image"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"

const links = [
  { href: "/predict", label: "Predict" },
  { href: "/demand", label: "Demand Index" },
  { href: "/compare", label: "Compare" },
  { href: "/saved", label: "Saved" },
  { href: "/about", label: "About" },
]

export function SiteHeader() {
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-30 w-full border-b bg-white/80 backdrop-blur">
      <div className="mx-auto max-w-6xl px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <Image src="/images/logo-mark.png" alt="Car Value logo" width={28} height={28} className="rounded-sm" />
          <span className="font-semibold text-lg tracking-tight">Car Value</span>
        </Link>

        <nav className="flex items-center gap-6">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={cn(
                "text-sm text-gray-600 hover:text-gray-900 transition-colors",
                pathname === l.href && "text-gray-900 font-medium",
              )}
            >
              {l.label}
            </Link>
          ))}
        </nav>

        {/* Login/Signup removed as requested */}
        <div className="w-10" aria-hidden="true" />
      </div>
    </header>
  )
}
