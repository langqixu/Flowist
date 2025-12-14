"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { api, Stats, Document } from "@/lib/api"
import { FileText, Database, Activity } from "lucide-react"

export default function DashboardPage() {
    const [stats, setStats] = useState<Stats | null>(null)
    const [recentDocs, setRecentDocs] = useState<Document[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        async function fetchData() {
            try {
                const [statsData, docsData] = await Promise.all([
                    api.getStats(),
                    api.getDocuments()
                ])
                setStats(statsData)
                // Sort by last modified
                setRecentDocs(docsData.sort((a, b) => b.last_modified - a.last_modified).slice(0, 5))
            } catch (error) {
                console.error("Failed to fetch dashboard data", error)
            } finally {
                setLoading(false)
            }
        }
        fetchData()
    }, [])

    if (loading) return <div>Loading...</div>

    return (
        <div className="space-y-8">
            <h1 className="text-3xl font-bold">Dashboard</h1>

            <div className="grid gap-4 md:grid-cols-3">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
                        <FileText className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{recentDocs.length}</div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Vector ID Chunks</CardTitle>
                        <Database className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats?.document_count || 0}</div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">System Status</CardTitle>
                        <Activity className="h-4 w-4 text-green-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-green-600">Active</div>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-4 md:grid-cols-1">
                <Card>
                    <CardHeader>
                        <CardTitle>Recent Updates</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {recentDocs.map((doc) => (
                                <div key={doc.id} className="flex items-center justify-between border-b pb-2 last:border-0">
                                    <div className="flex items-center space-x-4">
                                        <FileText className="h-4 w-4 text-muted-foreground" />
                                        <div>
                                            <p className="text-sm font-medium">{doc.name}</p>
                                            <p className="text-xs text-muted-foreground">{doc.category}</p>
                                        </div>
                                    </div>
                                    <div className="text-xs text-muted-foreground">
                                        {new Date(doc.last_modified * 1000).toLocaleString()}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
