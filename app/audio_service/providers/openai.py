"""
OpenAI TTS Provider Implementation

Uses OpenAI's Text-to-Speech API with streaming support.
"""

from typing import AsyncGenerator, List

from openai import AsyncOpenAI

from app.config import get_settings
from app.audio_service.providers.base import TTSProvider


class OpenAITTSProvider(TTSProvider):
    """
    OpenAI TTS implementation.
    
    Uses the OpenAI Speech API with streaming for low-latency audio generation.
    Recommended for meditation due to natural-sounding voices.
    """
    
    VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    def __init__(self):
        """Initialize OpenAI TTS provider."""
        settings = get_settings()
        
        client_kwargs = {"api_key": settings.openai_api_key}
        if settings.openai_base_url:
            client_kwargs["base_url"] = settings.openai_base_url
        
        self.client = AsyncOpenAI(**client_kwargs)
        self.model = settings.openai_tts_model
        self.default_voice = settings.openai_tts_voice
    
    async def generate_audio_stream(
        self,
        text: str,
        voice: str = "default",
    ) -> AsyncGenerator[bytes, None]:
        """
        Generate audio stream from text using OpenAI TTS.
        
        Args:
            text: Text to convert to speech
            voice: Voice ID (alloy, echo, fable, onyx, nova, shimmer)
            
        Yields:
            Audio chunks in MP3 format
        """
        if voice == "default":
            voice = self.default_voice
        
        if voice not in self.VOICES:
            voice = self.default_voice
        
        # Use streaming with response_format="mp3" for broader compatibility
        async with self.client.audio.speech.with_streaming_response.create(
            model=self.model,
            voice=voice,
            input=text,
            response_format="mp3",
        ) as response:
            async for chunk in response.iter_bytes(chunk_size=4096):
                yield chunk
    
    async def generate_audio(
        self,
        text: str,
        voice: str = "default",
    ) -> bytes:
        """
        Generate complete audio from text.
        
        Args:
            text: Text to convert to speech
            voice: Voice ID
            
        Returns:
            Complete MP3 audio data
        """
        if voice == "default":
            voice = self.default_voice
        
        if voice not in self.VOICES:
            voice = self.default_voice
        
        response = await self.client.audio.speech.create(
            model=self.model,
            voice=voice,
            input=text,
            response_format="mp3",
        )
        
        return response.content
    
    @property
    def supported_voices(self) -> List[str]:
        """Return list of supported voices."""
        return self.VOICES.copy()
    
    @property
    def audio_format(self) -> str:
        """Return audio format (mp3)."""
        return "mp3"
