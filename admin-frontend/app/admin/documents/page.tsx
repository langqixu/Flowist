
"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { api, Document } from "@/lib/api"
import { FileText, Plus, Trash2, Edit, AlertCircle } from "lucide-react"
import { toast } from "sonner"

export default function DocumentsPage() {
    const [documents, setDocuments] = useState<Document[]>([])
    const [loading, setLoading] = useState(true)
    const [deletingId, setDeletingId] = useState<string | null>(null)
    const router = useRouter()

    const fetchDocuments = async () => {
        try {
            setLoading(true)
            const data = await api.getDocuments()
            setDocuments(data)
        } catch (error) {
            toast.error("Failed to fetch documents")
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchDocuments()
    }, [])

    const handleDelete = async () => {
        if (!deletingId) return

        try {
            const [category, filename] = deletingId.split("/")
            await api.deleteDocument(category, filename)
            toast.success("Document deleted")
            fetchDocuments()
        } catch (error) {
            toast.error("Failed to delete document")
        } finally {
            setDeletingId(null)
        }
    }

    const DocumentList = ({ category }: { category: string }) => {
        const filteredDocs = documents.filter(doc => doc.category === category)

        if (filteredDocs.length === 0) {
            return (
                <div className="text-center py-12 text-muted-foreground border rounded-lg bg-gray-50/50">
                    No documents found in this category.
                </div>
            )
        }

        return (
            <div className="space-y-3">
                {filteredDocs.map(doc => (
                    <div key={doc.id} className="flex items-center justify-between p-4 border rounded-lg bg-white hover:bg-gray-50/50 transition-colors">
                        <div className="flex items-center space-x-3">
                            <div className="p-2 bg-blue-50 text-blue-600 rounded">
                                <FileText className="h-5 w-5" />
                            </div>
                            <div>
                                <h3 className="font-medium text-sm">{doc.name}</h3>
                                <p className="text-xs text-muted-foreground">
                                    {new Date(doc.last_modified * 1000).toLocaleString()} • {Math.round(doc.size / 1024 * 10) / 10} KB
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center space-x-2">
                            <Link href={`/admin/documents/${doc.category}%2F${doc.name}`}>
                                <Button variant="ghost" size="icon">
                                    <Edit className="h-4 w-4" />
                                </Button>
                            </Link>

                            <Button
                                variant="destructive"
                                size="sm"
                                onClick={() => setDeletingId(doc.id)}
                            >
                                <Trash2 className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>
                ))}
            </div>
        )
    }

    return (
        <div className="space-y-8">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold">Documents</h1>
                <Link href="/admin/documents/new">
                    <Button>
                        <Plus className="mr-2 h-4 w-4" />
                        New Document
                    </Button>
                </Link>
            </div>

            <Tabs defaultValue="techniques" className="w-full">
                <TabsList>
                    <TabsTrigger value="techniques">Techniques</TabsTrigger>
                    <TabsTrigger value="scripts">Scripts</TabsTrigger>
                    <TabsTrigger value="metaphors">Metaphors</TabsTrigger>
                </TabsList>

                <TabsContent value="techniques" className="mt-4">
                    <DocumentList category="techniques" />
                </TabsContent>
                <TabsContent value="scripts" className="mt-4">
                    <DocumentList category="scripts" />
                </TabsContent>
                <TabsContent value="metaphors" className="mt-4">
                    <DocumentList category="metaphors" />
                </TabsContent>
            </Tabs>

            <Dialog open={!!deletingId} onOpenChange={(open) => !open && setDeletingId(null)}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Delete Document?</DialogTitle>
                        <DialogDescription>
                            This action cannot be undone. This will permanently delete the file from the knowledge base.
                        </DialogDescription>
                    </DialogHeader>
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setDeletingId(null)}>Cancel</Button>
                        <Button variant="destructive" onClick={handleDelete}>Delete</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    )
}
