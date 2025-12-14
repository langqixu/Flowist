
"use client"

import dynamic from 'next/dynamic'
import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { api } from "@/lib/api"
import { toast } from "sonner"
import { ArrowLeft, Save, Loader2 } from "lucide-react"
import Link from "next/link"

// Dynamic import
const MdEditor = dynamic(() => import('react-markdown-editor-lite'), {
    ssr: false,
})
import 'react-markdown-editor-lite/lib/index.css';
import MarkdownIt from 'markdown-it';

const mdParser = new MarkdownIt();

export default function NewDocumentPage() {
    const router = useRouter()

    const [category, setCategory] = useState("techniques")
    const [filename, setFilename] = useState("")
    const [content, setContent] = useState("# New Document\n\nStart writing here...")
    const [saving, setSaving] = useState(false)

    const handleCreate = async () => {
        if (!filename.trim()) {
            toast.error("Filename is required")
            return
        }

        if (!filename.endsWith(".md")) {
            toast.error("Filename must end with .md")
            return
        }

        try {
            setSaving(true)
            await api.createDocument(category, filename, content)
            toast.success("Document created")
            router.push("/admin/documents")
        } catch (error) {
            toast.error("Failed to create document. Does file exist?")
        } finally {
            setSaving(false)
        }
    }

    return (
        <div className="space-y-6 h-full flex flex-col">
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                    <Link href="/admin/documents">
                        <Button variant="ghost" size="icon">
                            <ArrowLeft className="h-4 w-4" />
                        </Button>
                    </Link>
                    <div className="flex items-center space-x-4">
                        <h1 className="text-2xl font-bold">New Document</h1>

                        <select
                            className="p-2 border rounded-md bg-white text-sm"
                            value={category}
                            onChange={(e) => setCategory(e.target.value)}
                        >
                            <option value="techniques">Techniques</option>
                            <option value="scripts">Scripts</option>
                            <option value="metaphors">Metaphors</option>
                        </select>

                        <input
                            type="text"
                            placeholder="filename.md"
                            className="p-2 border rounded-md w-64 text-sm"
                            value={filename}
                            onChange={(e) => setFilename(e.target.value)}
                        />
                    </div>
                </div>

                <Button onClick={handleCreate} disabled={saving}>
                    {saving ? (
                        <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Creating...
                        </>
                    ) : (
                        <>
                            <Save className="mr-2 h-4 w-4" />
                            Create Document
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
                />
            </div>
        </div>
    )
}
