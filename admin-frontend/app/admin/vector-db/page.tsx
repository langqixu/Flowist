"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { api, Stats } from "@/lib/api"
import { toast } from "sonner"
import { Loader2, RefreshCw, Database } from "lucide-react"

export default function VectorDBPage() {
    const [stats, setStats] = useState<Stats | null>(null)
    const [loading, setLoading] = useState(false)
    const [importing, setImporting] = useState(false)

    const fetchStats = async () => {
        try {
            setLoading(true)
            const data = await api.getStats()
            setStats(data)
        } catch (error) {
            toast.error("Failed to fetch stats")
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchStats()
    }, [])

    const handleReimport = async () => {
        try {
            setImporting(true)
            toast.info("Starting knowledge base import...")

            const result = await api.reimport()

            if (result.status === "success") {
                toast.success("Import completed successfully")
                fetchStats() // Refresh stats
            } else {
                toast.error(`Import failed: ${result.message}`)
            }
        } catch (error) {
            toast.error("Failed to reimport knowledge base")
        } finally {
            setImporting(false)
        }
    }

    return (
        <div className="space-y-8">
            <h1 className="text-3xl font-bold">Vector Database Management</h1>

            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                        <Database className="h-5 w-5" />
                        <span>ChromaDB Status</span>
                    </CardTitle>
                    <CardDescription>Current status of the vector database used for RAG</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="grid gap-4 md:grid-cols-2">
                        <div className="p-4 border rounded-lg">
                            <div className="text-sm font-medium text-muted-foreground">Total Vector Chunks</div>
                            <div className="text-2xl font-bold mt-1">
                                {stats?.document_count || 0}
                            </div>
                        </div>

                        <div className="p-4 border rounded-lg">
                            <div className="text-sm font-medium text-muted-foreground">Collection Name</div>
                            <div className="text-2xl font-bold mt-1">
                                {stats?.collection_name || "-"}
                            </div>
                        </div>
                    </div>

                    <div className="flex flex-col space-y-4 pt-4 border-t">
                        <div>
                            <h3 className="text-lg font-medium">Re-import Knowledge Base</h3>
                            <p className="text-sm text-muted-foreground mt-1">
                                This will scan all markdown files in the <code>knowledge_base/</code> directory,
                                generate embeddings, and update the vector database. Existing data will be reset.
                            </p>
                        </div>

                        <Button
                            onClick={handleReimport}
                            disabled={importing || loading}
                            className="w-full sm:w-auto"
                        >
                            {importing ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Importing...
                                </>
                            ) : (
                                <>
                                    <RefreshCw className="mr-2 h-4 w-4" />
                                    Re-import All Documents
                                </>
                            )}
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
