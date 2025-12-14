"""
Audio Service Module

Provides TTS (Text-to-Speech) capabilities with provider-agnostic design.
"""

from app.audio_service.script_parser import ScriptParser, ScriptSegment
from app.audio_service.audio_service import AudioService

__all__ = ["ScriptParser", "ScriptSegment", "AudioService"]
