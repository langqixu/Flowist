
export class AudioPlayer {
    public audioContext: AudioContext
    public audioQueue: AudioBuffer[] = []
    public isPlaying = false
    private currentSource: AudioBufferSourceNode | null = null
    private processedUrls = new Set<string>() // Deduplication
    public onStatusChange?: (isPlaying: boolean) => void

    constructor(onStatusChange?: (isPlaying: boolean) => void) {
        this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
        this.onStatusChange = onStatusChange
        this.onStatusChange?.(false)
    }

    async resumeContext() {
        if (this.audioContext.state === 'suspended') {
            console.log('Resuming audio context')
            await this.audioContext.resume()
            console.log('Audio context resumed, state:', this.audioContext.state)
        }
    }

    async addAudioUrl(url: string) {
        // Strict Deduplication
        if (this.processedUrls.has(url)) {
            console.log('Skipping duplicate audio URL:', url)
            return
        }
        this.processedUrls.add(url)

        console.log('Fetching audio from URL:', url)

        try {
            const response = await fetch(url)
            if (!response.ok) {
                console.error('Failed to fetch audio:', response.statusText)
                return
            }

            const arrayBuffer = await response.arrayBuffer()
            console.log('Fetched audio bytes:', arrayBuffer.byteLength)

            const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer)
            console.log('Audio decoded successfully, duration:', audioBuffer.duration)

            this.audioQueue.push(audioBuffer)

            if (!this.isPlaying) {
                this.playNext()
            }
        } catch (error) {
            console.error('Failed to process audio URL:', error)
        }
    }

    private playNext() {
        if (this.audioQueue.length === 0) {
            this.isPlaying = false
            this.onStatusChange?.(false)
            return
        }

        this.isPlaying = true
        this.onStatusChange?.(true)

        const buffer = this.audioQueue.shift()!

        // Create source
        const source = this.audioContext.createBufferSource()
        source.buffer = buffer
        source.connect(this.audioContext.destination)

        source.onended = () => {
            console.log('Audio chunk ended, playing next')
            this.playNext()
        }

        this.currentSource = source
        source.start(0)
    }

    stop() {
        this.cleanup()
    }

    cleanup() {
        if (this.currentSource) {
            this.currentSource.stop()
        }
        // Don't close context on simple stop, usually we keep it for reuse unless unmounting
        // But for cleanup (unmount), we close.
        // Let's decide: stop() clears queue and stops playing. cleanup() closes context.

        this.audioQueue = []
        this.processedUrls.clear()
        this.isPlaying = false
        this.onStatusChange?.(false)
    }
}
