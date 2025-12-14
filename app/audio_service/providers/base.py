"""
TTS Provider Base Interface

Defines the abstract protocol for TTS providers.
All concrete implementations must follow this interface.
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, List


class TTSProvider(ABC):
    """
    Abstract base class for TTS providers.
    
    All TTS providers (OpenAI, ElevenLabs, MiniMax) must implement this interface.
    This allows the AudioService to work with any provider interchangeably.
    """
    
    @abstractmethod
    async def generate_audio_stream(
        self,
        text: str,
        voice: str = "default",
    ) -> AsyncGenerator[bytes, None]:
        """
        Generate audio from text in streaming mode.
        
        Args:
            text: The text to convert to speech
            voice: Voice identifier (provider-specific)
            
        Yields:
            Audio data chunks in bytes (PCM or MP3 depending on provider)
        """
        pass
    
    @abstractmethod
    async def generate_audio(
        self,
        text: str,
        voice: str = "default",
    ) -> bytes:
        """
        Generate complete audio from text.
        
        Args:
            text: The text to convert to speech
            voice: Voice identifier (provider-specific)
            
        Returns:
            Complete audio data in bytes
        """
        pass
    
    @property
    @abstractmethod
    def supported_voices(self) -> List[str]:
        """
        List of supported voice identifiers.
        
        Returns:
            List of voice IDs supported by this provider
        """
        pass
    
    @property
    @abstractmethod
    def audio_format(self) -> str:
        """
        The audio format produced by this provider.
        
        Returns:
            Audio format string (e.g., "mp3", "pcm", "wav")
        """
        pass
    
    @staticmethod
    def generate_silence(duration_seconds: float, sample_rate: int = 24000) -> bytes:
        """
        Generate silent audio for pause segments.
        
        Args:
            duration_seconds: Duration of silence in seconds
            sample_rate: Audio sample rate (default 24000 for OpenAI)
            
        Returns:
            PCM audio data representing silence
        """
        # 16-bit mono PCM: 2 bytes per sample
        num_samples = int(sample_rate * duration_seconds)
        return bytes(num_samples * 2)  # Zero bytes = silence
