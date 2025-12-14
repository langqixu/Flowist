"""
Audio Service Module

Orchestrates the complete TTS pipeline:
LLM Text Stream -> ScriptParser -> TTS Provider -> Audio Stream
"""

from dataclasses import dataclass
from typing import AsyncGenerator, Optional, List
from enum import Enum

from app.config import get_settings
from app.audio_service.script_parser import ScriptParser, ScriptSegment, SegmentType
from app.audio_service.providers.base import TTSProvider
from app.audio_service.providers.openai import OpenAITTSProvider


class AudioChunkType(str, Enum):
    """Type of audio chunk."""
    AUDIO = "audio"
    SILENCE = "silence"
    METADATA = "metadata"


@dataclass
class AudioChunk:
    """
    A chunk of audio data with metadata.
    
    Attributes:
        type: Type of chunk (audio, silence, metadata)
        data: Audio bytes (empty for metadata)
        duration: Estimated duration in seconds
        text: Original text (for debugging/display)
    """
    type: AudioChunkType
    data: bytes = b""
    duration: float = 0.0
    text: str = ""


class AudioService:
    """
    Orchestrates TTS generation pipeline.
    
    Handles:
    - Provider selection based on config
    - Script parsing for sentence-level streaming
    - Pause generation
    - Audio chunk assembly
    """
    
    def __init__(self, provider: Optional[TTSProvider] = None):
        """
        Initialize AudioService.
        
        Args:
            provider: Optional TTS provider. If not provided, uses config.
        """
        self.parser = ScriptParser()
        self.provider = provider or self._create_provider()
    
    def _create_provider(self) -> TTSProvider:
        """Create TTS provider based on configuration."""
        settings = get_settings()
        provider_name = settings.tts_provider.lower()
        
        if provider_name == "openai":
            return OpenAITTSProvider()
        elif provider_name == "elevenlabs":
            # TODO: Implement ElevenLabsTTSProvider
            raise NotImplementedError("ElevenLabs provider not yet implemented. Use 'openai'.")
        elif provider_name == "minimax":
            from app.audio_service.providers.minimax import MiniMaxTTSProvider
            return MiniMaxTTSProvider()
        else:
            # Default to OpenAI
            return OpenAITTSProvider()
    
    async def generate_audio_from_text(
        self,
        text: str,
        voice: str = "default",
    ) -> AsyncGenerator[AudioChunk, None]:
        """
        Generate audio chunks from text (single sentence or phrase).
        
        Args:
            text: Text to convert to speech (should be a single sentence)
            voice: Voice identifier for TTS
            
        Yields:
            AudioChunk: Audio data
        """
        # Skip empty text
        if not text or not text.strip():
            return
        
        # Directly generate speech without parsing
        # (parsing is already done in the API layer for sentence splitting)
        print(f"DEBUG: AudioService calling TTS for: '{text[:50]}...'", flush=True)
        
        audio_data = b""
        try:
            async for chunk in self.provider.generate_audio_stream(text.strip(), voice):
                audio_data += chunk
            
            print(f"DEBUG: TTS returned {len(audio_data)} bytes", flush=True)
            
            # Estimate duration (rough: ~150 words/min for meditation)
            word_count = len(text.split())
            estimated_duration = word_count / 2.5  # ~2.5 words per second
            
            yield AudioChunk(
                type=AudioChunkType.AUDIO,
                data=audio_data,
                duration=estimated_duration,
                text=text,
            )
        except Exception as e:
            print(f"ERROR: TTS provider failed: {e}", flush=True)
            import traceback
            traceback.print_exc()
    
    def _merge_short_segments(
        self,
        segments: List[ScriptSegment],
        min_length: int = 50,  # Increased from 20 to 50 for more aggressive merging
    ) -> List[ScriptSegment]:
        """
        Merge adjacent short text segments to reduce API calls.
        
        Args:
            segments: List of parsed segments
            min_length: Minimum character length for a segment
            
        Returns:
            List of merged segments
        """
        if not segments:
            return segments
        
        merged = []
        current_text = []
        
        for segment in segments:
            if segment.type == "pause":
                # Flush accumulated text before pause
                if current_text:
                    merged_segment = ScriptSegment(
                        type="text",
                        content=" ".join(current_text),
                        duration=None,
                    )
                    merged.append(merged_segment)
                    current_text = []
                # Add pause
                merged.append(segment)
            else:  # text segment
                current_text.append(segment.content)
                
                # If accumulated text is long enough, flush it
                combined_length = sum(len(t) for t in current_text)
                if combined_length >= min_length:
                    merged_segment = ScriptSegment(
                        type="text",
                        content=" ".join(current_text),
                        duration=None,
                    )
                    merged.append(merged_segment)
                    current_text = []
        
        # Flush any remaining text
        if current_text:
            merged_segment = ScriptSegment(
                type="text",
                content=" ".join(current_text),
                duration=None,
            )
            merged.append(merged_segment)
        
        return merged
    
    async def generate_audio_stream(
        self,
        text_stream: AsyncGenerator[str, None],
        voice: str = "default",
    ) -> AsyncGenerator[AudioChunk, None]:
        """
        Generate audio from a streaming text source (e.g., LLM).
        
        Processes text as it arrives, generating audio with minimal latency.
        
        Args:
            text_stream: Async generator yielding text chunks
            voice: Voice identifier
            
        Yields:
            AudioChunk objects as soon as segments are ready
        """
        buffer = ""
        
        async for text_chunk in text_stream:
            # Parse incrementally
            segments, buffer = self.parser.parse_streaming(text_chunk, buffer)
            
            # Process complete segments immediately
            for segment in segments:
                async for chunk in self._process_segment(segment, voice):
                    yield chunk
        
        # Process any remaining buffer
        if buffer.strip():
            final_segment = ScriptSegment(
                type=SegmentType.TEXT,
                content=buffer.strip(),
            )
            async for chunk in self._process_segment(final_segment, voice):
                yield chunk
    
    async def _process_segment(
        self,
        segment: ScriptSegment,
        voice: str,
    ) -> AsyncGenerator[AudioChunk, None]:
        """
        Process a single segment into audio.
        
        Args:
            segment: Script segment to process
            voice: Voice identifier
            
        Yields:
            AudioChunk with audio data
        """
        if segment.type == SegmentType.PAUSE:
            # Generate silence
            silence_data = TTSProvider.generate_silence(segment.duration)
            yield AudioChunk(
                type=AudioChunkType.SILENCE,
                data=silence_data,
                duration=segment.duration,
                text=f"[{segment.duration}s pause]",
            )
        
        elif segment.type == SegmentType.TEXT:
            # Generate speech
            audio_data = b""
            async for chunk in self.provider.generate_audio_stream(segment.content, voice):
                audio_data += chunk
            
            # Estimate duration (rough: ~150 words/min for meditation)
            word_count = len(segment.content.split())
            estimated_duration = word_count / 2.5  # ~2.5 words per second
            
            yield AudioChunk(
                type=AudioChunkType.AUDIO,
                data=audio_data,
                duration=estimated_duration,
                text=segment.content,
            )
    
    async def generate_complete_audio(
        self,
        text: str,
        voice: str = "default",
    ) -> bytes:
        """
        Generate complete audio file from text.
        
        Concatenates all audio chunks into a single audio stream.
        Note: This mixes MP3 and PCM which won't play correctly.
        For production, use generate_audio_from_text and handle formats properly.
        
        Args:
            text: Complete meditation script
            voice: Voice identifier
            
        Returns:
            Complete audio data (may need post-processing)
        """
        audio_data = b""
        async for chunk in self.generate_audio_from_text(text, voice):
            if chunk.type in (AudioChunkType.AUDIO, AudioChunkType.SILENCE):
                audio_data += chunk.data
        return audio_data
