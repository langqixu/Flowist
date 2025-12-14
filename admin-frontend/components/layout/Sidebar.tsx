"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { LayoutDashboard, FileText, Database, Settings } from "lucide-react"

export function Sidebar() {
    const pathname = usePathname()

    return (
        <div className="pb-12 w-64 border-r bg-gray-50/40 hidden md:block">
            <div className="space-y-4 py-4">
                <div className="px-3 py-2">
                    <h2 className="mb-2 px-4 text-lg font-semibold tracking-tight">
                        Flowist Admin
                    </h2>
                    <div className="space-y-1">
                        <Link href="/admin/dashboard">
                            <Button variant={pathname === "/admin/dashboard" ? "secondary" : "ghost"} className="w-full justify-start">
                                <LayoutDashboard className="mr-2 h-4 w-4" />
                                Dashboard
                            </Button>
                        </Link>
                        <Link href="/admin/documents">
                            <Button variant={pathname.startsWith("/admin/documents") ? "secondary" : "ghost"} className="w-full justify-start">
                                <FileText className="mr-2 h-4 w-4" />
                                Documents
                            </Button>
                        </Link>
                        <Link href="/admin/vector-db">
                            <Button variant={pathname === "/admin/vector-db" ? "secondary" : "ghost"} className="w-full justify-start">
                                <Database className="mr-2 h-4 w-4" />
                                Vector DB
                            </Button>
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    )
}
