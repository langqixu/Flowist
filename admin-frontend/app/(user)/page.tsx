"use client"

import { useState, useRef, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Send, Cloud, MapPin, Clock } from "lucide-react"
import { AudioPlayer } from "@/lib/audio-player"

export default function Home() {
    const [input, setInput] = useState("")
    const [isSessionActive, setIsSessionActive] = useState(false)
    const [currentSubtitle, setCurrentSubtitle] = useState("")
    const [allText, setAllText] = useState("")
    const [isPlaying, setIsPlaying] = useState(false)
    const [isSubmitting, setIsSubmitting] = useState(false)
    const isSubmittingRef = useRef(false) // Synchronous lock

    // Audio state
    const audioPlayerRef = useRef<AudioPlayer | null>(null)

    // Context States
    const [time, setTime] = useState("Night")
    const [weather, setWeather] = useState("Raining")
    const [location, setLocation] = useState("Home")

    const times = ["Morning", "Afternoon", "Evening", "Night"]
    const weathers = ["Sunny", "Raining", "Cloudy", "Snowy"]
    const locations = ["Home", "Office", "Transport", "Nature"]

    const cycleState = (current: string, options: string[], setter: (val: string) => void) => {
        const idx = options.indexOf(current)
        const next = options[(idx + 1) % options.length]
        setter(next)
    }

    useEffect(() => {
        // Initialize audio player on client side
        audioPlayerRef.current = new AudioPlayer((playing) => setIsPlaying(playing))

        return () => {
            if (audioPlayerRef.current) {
                audioPlayerRef.current.cleanup()
            }
        }
    }, [])

    const handleStartSession = async () => {
        if (!input.trim() || isSubmittingRef.current) return

        console.log("handleStartSession called") // Debug log
        isSubmittingRef.current = true
        setIsSubmitting(true)

        // Resume audio context (required for Web Audio API)
        // audioPlayerRef.current is guaranteed to exist due to useEffect
        await audioPlayerRef.current?.resumeContext()

        setIsSessionActive(true)
        setAllText("")
        setCurrentSubtitle("")

        // Start SSE stream
        try {
            console.log('[DEBUG] Initiating fetch to /api/meditation/session/audio-text-stream')
            const response = await fetch("/api/meditation/session/audio-text-stream", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_id: "demo_user",
                    user_feeling_input: input,
                    current_context: {
                        local_time: time,
                        weather: weather,
                        location: location,
                    },
                }),
            })

            console.log('[DEBUG] Fetch response status:', response.status, response.statusText)
            console.log('[DEBUG] Response headers:', response.headers.get('content-type'))

            if (!response.body) {
                console.error('[DEBUG] No response body!')
                return
            }

            console.log('[DEBUG] Starting SSE stream reader')
            const reader = response.body.getReader()
            const decoder = new TextDecoder()
            let buffer = ""
            const processedMessages = new Set<string>()  // Dedup using seq:type
            let messageCount = 0

            while (true) {
                const { done, value } = await reader.read()
                if (done) {
                    console.log('[DEBUG] Reader done, total messages:', messageCount)
                    break
                }

                // Decode and append to buffer
                const chunk = decoder.decode(value, { stream: true })
                buffer += chunk
                console.log('[DEBUG] Received chunk, buffer size:', buffer.length)

                // Split by double newline (SSE message delimiter)
                const messages = buffer.split("\n\n")

                // Keep the last incomplete message in buffer
                buffer = messages.pop() || ""

                console.log('[DEBUG] Split into', messages.length, 'messages')

                for (const message of messages) {
                    if (message.startsWith("data: ")) {
                        messageCount++
                        try {
                            const data = JSON.parse(message.slice(6))
                            console.log('[DEBUG] Parsed message #' + messageCount + ':', data.type, data.seq || 'no-seq')

                            // Create unique message key
                            const msgKey = `${data.seq}:${data.type}`

                            // Dedup check
                            if (data.seq && processedMessages.has(msgKey)) {
                                console.log('[DEBUG] Skipping duplicate message:', msgKey)
                                continue
                            }
                            if (data.seq) {
                                processedMessages.add(msgKey)
                            }

                            if (data.type === "text") {
                                console.log('[DEBUG] Processing text:', data.content)
                                setCurrentSubtitle(data.content)
                                setAllText(prev => prev + data.content + " ")
                            } else if (data.type === "audio_ref") {
                                console.log('[DEBUG] Processing audio_ref for seq:', data.seq, 'URL:', data.url)

                                // Fix URL for Next.js proxy
                                let url = data.url
                                if (url.startsWith("/api/v1")) {
                                    url = url.replace("/api/v1", "/api")
                                }

                                console.log('[DEBUG] About to call addAudioUrl with:', url)
                                await audioPlayerRef.current?.addAudioUrl(url)
                            } else if (data.type === "pause") {
                                console.log('[DEBUG] Processing pause:', data.duration, 'seconds')
                                await new Promise(resolve => setTimeout(resolve, data.duration * 1000))
                            } else if (data.type === "done") {
                                console.log('[DEBUG] Session done')
                                setCurrentSubtitle("")
                                setIsSubmitting(false)
                                isSubmittingRef.current = false
                            }
                        } catch (error) {
                            console.error("[DEBUG] Failed to parse SSE message:", error, message.slice(0, 100))
                        }
                    } else {
                        console.log('[DEBUG] Non-data message:', message.slice(0, 50))
                    }
                }
            }
        } catch (error) {
            console.error("Session failed:", error)
            setIsSubmitting(false)
            isSubmittingRef.current = false
        }
    }

    const handleEndSession = () => {
        setIsSessionActive(false)
        audioPlayerRef.current?.stop()
        setInput("")
        setCurrentSubtitle("")
    }

    return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-50 dark:bg-zinc-950 p-4 relative overflow-hidden font-sans">
            {/* Ambient Background */}
            <div className="absolute inset-0 z-0 pointer-events-none transition-colors duration-1000 ease-in-out"
                style={{
                    background: time === 'Night'
                        ? 'radial-gradient(circle at 50% 0%, rgba(30, 30, 60, 0.4), transparent 70%)'
                        : 'radial-gradient(circle at 50% 0%, rgba(255, 200, 100, 0.1), transparent 70%)'
                }}
            />

            <AnimatePresence mode="wait">
                {!isSessionActive ? (
                    <motion.div
                        key="input"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="w-full max-w-2xl z-10 space-y-8"
                    >
                        {/* Header / Context */}
                        <div className="flex flex-col items-center gap-6">
                            <h1 className="text-5xl font-extralight tracking-tight text-zinc-900 dark:text-zinc-100">
                                Flowist
                            </h1>
                            {/* Audio Debug Controls */}
                            <div className="flex gap-2 text-xs text-white/50 mb-2">
                                <div>Status: {isPlaying ? "Playing 🔊" : "Idle ⏸️"}</div>
                                <div>Queue: {audioPlayerRef.current?.audioQueue.length || 0}</div>
                                <button
                                    onClick={() => {
                                        audioPlayerRef.current?.audioContext?.resume();
                                        console.log("Resumed AudioContext");
                                    }}
                                    className="underline hover:text-white"
                                >
                                    Force Resume Audio
                                </button>
                                <button
                                    onClick={() => {
                                        // Test beep
                                        const ctx = audioPlayerRef.current?.audioContext;
                                        if (ctx) {
                                            const osc = ctx.createOscillator();
                                            osc.connect(ctx.destination);
                                            osc.start();
                                            osc.stop(ctx.currentTime + 0.1);
                                            console.log("Test beep played");
                                        }
                                    }}
                                    className="underline hover:text-white ml-2"
                                >
                                    Test Sound
                                </button>
                            </div>
                            <div className="flex gap-3">
                                {[
                                    { icon: Clock, value: time, options: times, setter: setTime },
                                    { icon: Cloud, value: weather, options: weathers, setter: setWeather },
                                    { icon: MapPin, value: location, options: locations, setter: setLocation }
                                ].map((item, i) => (
                                    <button
                                        key={i}
                                        onClick={() => cycleState(item.value, item.options, item.setter)}
                                        className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/40 border border-white/20 text-sm text-zinc-700 dark:text-zinc-300 shadow-sm backdrop-blur-md hover:bg-white/60 transition-all cursor-pointer active:scale-95"
                                    >
                                        <item.icon size={14} />
                                        <span>{item.value}</span>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Input Area */}
                        <div className="relative group">
                            <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/10 to-purple-500/10 rounded-3xl blur-2xl opacity-50 group-hover:opacity-75 transition-opacity" />
                            <textarea
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="How are you feeling right now?"
                                className="w-full min-h-[140px] p-8 rounded-3xl border border-white/20 bg-white/70 dark:bg-zinc-900/70 shadow-xl backdrop-blur-xl text-xl ring-1 ring-zinc-200/50 focus:ring-2 focus:ring-indigo-500/20 outline-none resize-none placeholder:text-zinc-400/70 text-zinc-800 dark:text-zinc-200 transition-all"
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter' && !e.shiftKey) {
                                        e.preventDefault()
                                        handleStartSession()
                                    }
                                }}
                            />
                            <button
                                onClick={handleStartSession}
                                disabled={!input.trim()}
                                className="absolute bottom-6 right-6 p-3 rounded-full bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 hover:scale-105 disabled:opacity-50 disabled:scale-100 transition-all shadow-lg"
                            >
                                <Send size={20} />
                            </button>
                        </div>
                    </motion.div>
                ) : (
                    <motion.div
                        key="session"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="w-full max-w-4xl z-10 space-y-8"
                    >
                        {/* Subtitle Display */}
                        <div className="min-h-[200px] flex items-center justify-center">
                            <motion.p
                                key={currentSubtitle}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0 }}
                                className="text-3xl font-serif text-center text-zinc-800 dark:text-zinc-200 leading-relaxed px-8"
                            >
                                {currentSubtitle}
                            </motion.p>
                        </div>

                        {/* Controls */}
                        <div className="flex justify-center gap-4">
                            <button
                                onClick={handleEndSession}
                                className="px-6 py-3 rounded-full bg-zinc-800 dark:bg-zinc-200 text-white dark:text-zinc-900 hover:scale-105 transition-all"
                            >
                                End Session
                            </button>
                        </div>

                        {/* Full transcript (optional, can be hidden) */}
                        <div className="text-xs text-zinc-500 dark:text-zinc-400 text-center max-w-2xl mx-auto opacity-50">
                            {allText}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    )
}
