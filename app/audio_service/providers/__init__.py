"""
TTS Provider Interface and Implementations

Defines the abstract interface for TTS providers and concrete implementations.
"""

from app.audio_service.providers.base import TTSProvider
from app.audio_service.providers.openai import OpenAITTSProvider

__all__ = ["TTSProvider", "OpenAITTSProvider"]
