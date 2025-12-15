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
