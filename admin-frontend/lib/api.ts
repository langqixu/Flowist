export const generateAudioUrl = (
    input: string,
    context: { time: string; weather: string; location: string }
) => {
    const params = new URLSearchParams({
        user_id: "demo_user",
        feeling: input,
        time: context.time,
        weather: context.weather,
        location: context.location,
    })
    return `/api/meditation/session/audio?${params.toString()}`
}

export const streamMeditation = async (
    input: string,
    context: { time: string; weather: string; location: string },
    onChunk: (text: string) => void
) => {
    const response = await fetch("/api/meditation/session/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id: "demo_user",
            user_feeling_input: input,
            current_context: {
                local_time: context.time,
                weather: context.weather,
                location: context.location,
            },
        }),
    })

    if (!response.body) return

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split("\n\n")

        for (const line of lines) {
            if (line.startsWith("data: ")) {
                const data = line.slice(6)
                if (data === "[DONE]") break
                if (data.startsWith("[ERROR]")) console.error(data)
                else onChunk(data)
            }
        }
    }
}

// Types for admin dashboard
export interface Stats {
    document_count: number
    chunk_count: number
    collection_name?: string
    persist_directory?: string
}

export interface Document {
    id: string
    name: string
    category: string
    last_modified: number
}

// API object for admin operations
export const api = {
    async getStats(): Promise<Stats> {
        const response = await fetch("/api/admin/stats")
        if (!response.ok) throw new Error("Failed to fetch stats")
        return response.json()
    },

    async getDocuments(): Promise<Document[]> {
        const response = await fetch("/api/admin/documents")
        if (!response.ok) throw new Error("Failed to fetch documents")
        return response.json()
    },

    async reimportKnowledgeBase(): Promise<{ status: string; message: string }> {
        const response = await fetch("/api/admin/vectordb/reimport", {
            method: "POST"
        })
        if (!response.ok) throw new Error("Failed to trigger re-import")
        return response.json()
    }
}
