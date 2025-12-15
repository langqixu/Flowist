interface AudioItem {
    buffer: AudioBuffer
    text: string
    duration: number
}

export class AudioPlayer {
    public audioContext: AudioContext
    public audioQueue: AudioItem[] = []
    public isPlaying = false
    private currentSource: AudioBufferSourceNode | null = null
    private processedUrls = new Set<string>() // Deduplication
    public onStatusChange?: (isPlaying: boolean) => void
    public onSubtitleChange?: (text: string) => void

    private isDestroyed = false

    constructor(
        onStatusChange?: (isPlaying: boolean) => void,
        onSubtitleChange?: (text: string) => void
    ) {
        this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
        this.onStatusChange = onStatusChange
        this.onSubtitleChange = onSubtitleChange
        this.onStatusChange?.(false)
    }

    async resumeContext() {
        if (this.isDestroyed) return
        if (this.audioContext.state === 'suspended') {
            await this.audioContext.resume()
        }
    }

    async addAudioUrl(url: string, text: string = "", duration: number = 0) {
        if (this.isDestroyed) return

        // Strict Deduplication
        if (this.processedUrls.has(url)) {
            return
        }
        this.processedUrls.add(url)

        try {
            const response = await fetch(url)
            if (!response.ok) {
                console.error('[AudioPlayer] Failed to fetch audio:', response.statusText)
                return
            }

            if (this.isDestroyed) return

            const arrayBuffer = await response.arrayBuffer()
            if (this.isDestroyed) return

            const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer)

            if (this.isDestroyed) return

            this.audioQueue.push({
                buffer: audioBuffer,
                text,
                duration
            })

            if (!this.isPlaying) {
                this.playNext()
            }
        } catch (error) {
            console.error('[AudioPlayer] Failed to process audio URL:', error)
        }
    }

    private playNext() {
        if (this.isDestroyed) return

        if (this.audioQueue.length === 0) {
            this.isPlaying = false
            this.onStatusChange?.(false)
            this.onSubtitleChange?.("") // Clear subtitle when done
            return
        }

        const item = this.audioQueue.shift()!
        this.isPlaying = true
        this.onStatusChange?.(true)

        // SYNC POINT: Update subtitle exactly when audio starts
        this.onSubtitleChange?.(item.text)

        // Create source
        const source = this.audioContext.createBufferSource()
        source.buffer = item.buffer
        source.connect(this.audioContext.destination)

        source.onended = () => {
            if (this.isDestroyed) return
            this.playNext()
        }

        this.currentSource = source
        source.start(0)
    }

    stop() {
        this.cleanup()
    }

    cleanup() {
        this.isDestroyed = true

        if (this.currentSource) {
            this.currentSource.stop()
        }

        try {
            this.audioContext.close()
        } catch (e) {
            console.error('Error closing audio context:', e)
        }

        this.audioQueue = []
        this.processedUrls.clear()
        this.isPlaying = false
        this.onStatusChange?.(false)
        this.onSubtitleChange?.("")
    }
}
