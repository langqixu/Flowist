
"use client"

import dynamic from 'next/dynamic'
import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { api } from "@/lib/api"
import { toast } from "sonner"
import { ArrowLeft, Save, Loader2 } from "lucide-react"
import Link from "next/link"

// Dynamic import for editor to avoid SSR issues
const MdEditor = dynamic(() => import('react-markdown-editor-lite'), {
    ssr: false,
    loading: () => <div className="h-96 w-full bg-gray-50 flex items-center justify-center">Loading editor...</div>
})
import 'react-markdown-editor-lite/lib/index.css';
import MarkdownIt from 'markdown-it';

const mdParser = new MarkdownIt();

export default function EditDocumentPage() {
    const params = useParams()
    const router = useRouter()
    // decodeURIComponent to handle encoded slashes/spaces
    const id = decodeURIComponent(params.id as string)
    const [category, filename] = id.split("/")

    const [content, setContent] = useState("")
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)

    useEffect(() => {
        async function fetchDoc() {
            try {
                const data = await api.getDocument(category, filename)
                setContent(data.content)
            } catch (error) {
                toast.error("Failed to load document")
                router.push("/admin/documents")
            } finally {
                setLoading(false)
            }
        }

        if (category && filename) {
            fetchDoc()
        }
    }, [category, filename, router])

    const handleSave = async () => {
        try {
            setSaving(true)
            await api.updateDocument(category, filename, content)
            toast.success("Document saved")
        } catch (error) {
            toast.error("Failed to save document")
        } finally {
            setSaving(false)
        }
    }

    if (loading) return <div>Loading...</div>

    return (
        <div className="space-y-6 h-full flex flex-col">
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                    <Link href="/admin/documents">
                        <Button variant="ghost" size="icon">
                            <ArrowLeft className="h-4 w-4" />
                        </Button>
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold">{filename}</h1>
                        <p className="text-sm text-muted-foreground capitalize">{category}</p>
                    </div>
                </div>

                <Button onClick={handleSave} disabled={saving}>
                    {saving ? (
                        <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Saving...
                        </>
                    ) : (
                        <>
                            <Save className="mr-2 h-4 w-4" />
                            Save Changes
                        </>
                    )}
                </Button>
            </div>

            <div className="flex-1 border rounded-lg overflow-hidden min-h-[600px]">
                <MdEditor
                    style={{ height: '100%' }}
                    renderHTML={text => mdParser.render(text)}
                    value={content}
                    onChange={({ text }) => setContent(text)}
                    view={{ menu: true, md: true, html: true }}
                    canView={{
                        menu: true,
                        md: true,
                        html: true,
                        fullScreen: true,
                        hideMenu: true,
                        both: true
                    }}
                />
            </div>
        </div>
    )
}
