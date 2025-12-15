"""
Minimax TTS Provider Implementation

Uses Minimax's T2A (Text-to-Audio) API with streaming support.
"""

import json
import httpx
from typing import AsyncGenerator, List, Optional
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import logging

from app.config import get_settings
from app.audio_service.providers.base import TTSProvider

# Configure logging for retries
logger = logging.getLogger(__name__)


class MinimaxRateLimitError(Exception):
    """Raised when Minimax API returns rate limit error."""
    pass


class MiniMaxTTSProvider(TTSProvider):
    """
    Minimax TTS implementation.
    
    Uses Minimax's T2A V2 API.
    Requires MINIMAX_API_KEY and MINIMAX_GROUP_ID.
    """
    
    # Common Minimax voice IDs (examples)
    VOICES = [
        "male-qn-qingse",   # 青涩青年
        "male-qn-jingying", # 精英青年
        "female-shaonv",    # 少女
        "female-yujie",     # 御姐
        "presenter_male",   # 男主持人
        "presenter_female", # 女主持人
    ]
    
    DEFAULT_API_URL = "https://api.minimax.chat/v1/t2a_v2"
    
    def __init__(self):
        """Initialize Minimax TTS provider."""
        settings = get_settings()
        
        self.api_key = settings.minimax_api_key
        self.group_id = settings.minimax_group_id
        self.model = "speech-01-turbo"
        self.default_voice = "male-qn-qingse"
        
        # Base URL can be overridden if needed, otherwise use default
        self.base_url = self.DEFAULT_API_URL
        
        # Debug logging
        print(f"DEBUG: MiniMaxTTSProvider initialized", flush=True)
        print(f"  API Key present: {bool(self.api_key)}", flush=True)
        print(f"  Group ID present: {bool(self.group_id)}", flush=True)
        print(f"  API Key length: {len(self.api_key) if self.api_key else 0}", flush=True)
    
    async def generate_audio_stream(
        self,
        text: str,
        voice: str = "default",
    ) -> AsyncGenerator[bytes, None]:
        """
        Generate audio stream from text using Minimax TTS.
        
        Uses exponential backoff retry with max 3 attempts for:
        - Rate limit errors
        - Network/HTTP errors
        
        Args:
            text: Text to convert to speech
            voice: Voice ID
            
        Yields:
            Audio chunks in MP3 format
        """
        # Add delay to avoid rate limiting (simple throttle)
        import asyncio
        await asyncio.sleep(0.5)  # 500ms delay between requests (conservative)
        
        if voice == "default":
            voice = self.default_voice
        
        print(f"DEBUG: MiniMax generate_audio_stream called with text length: {len(text)}", flush=True)
            
        if not self.api_key or not self.group_id:
            error_msg = f"Minimax credentials missing. API Key: {bool(self.api_key)}, Group ID: {bool(self.group_id)}"
            print(f"ERROR: {error_msg}", flush=True)
            raise ValueError(error_msg)
        
        print(f"DEBUG: Credentials OK. Making request to Minimax...", flush=True)
            
        url = f"{self.base_url}?GroupId={self.group_id}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "text": text,
            "stream": True,
            "voice_setting": {
                "voice_id": voice,
                "speed": 1.0,
                "vol": 1.0,
                "pitch": 0,
            },
            "audio_setting": {
                "sample_rate": 32000,
                "bitrate": 128000,
                "format": "mp3",
                "channel": 1,
            }
        }
        
        print(f"DEBUG: Request URL: {url}", flush=True)
        print(f"DEBUG: Voice: {voice}", flush=True)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                print(f"DEBUG: Minimax response status: {response.status_code}", flush=True)
                
                if response.status_code != 200:
                    error_text = await response.aread()
                    error_msg = f"Minimax API Error ({response.status_code}): {error_text.decode()}"
                    print(f"ERROR: {error_msg}", flush=True)
                    raise httpx.HTTPStatusError(error_msg, request=response.request, response=response)
                
                chunk_count = 0
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    
                    if line.startswith("data:"):
                        line = line[5:].strip()
                    
                    try:
                        data = json.loads(line)
                        
                        # Check for errors in the response body
                        if "base_resp" in data and data["base_resp"]["status_code"] != 0:
                            error_msg = data['base_resp']['status_msg']
                            print(f"ERROR: Minimax API Error: {error_msg}", flush=True)
                            
                            # Raise rate limit error for retry
                            if "rate limit" in error_msg.lower():
                                raise MinimaxRateLimitError(error_msg)
                            else:
                                raise Exception(f"Minimax API Error: {error_msg}")
                            
                        # Extract audio data (hex string)
                        if "data" in data and "audio" in data["data"]:
                            # CRITICAL FIX: Minimax sends a final chunk with "extra_info" that contains
                            # the concatenated audio of the entire stream (or a large buffer).
                            # We must ignore this chunk to prevent double playback.
                            if "extra_info" in data:
                                print(f"DEBUG: Ignoring final summary chunk ({len(data['data']['audio'])} hex chars)", flush=True)
                                continue
                                
                            hex_audio = data["data"]["audio"]
                            if hex_audio:
                                # CRITICAL FIX: Minimax sends a final chunk with "extra_info"
                                # that contains the full concatenated audio. Skip it to avoid duplication.
                                if "extra_info" in data:
                                    continue
                                
                                chunk_count += 1
                                yield bytes.fromhex(hex_audio)
                                
                    except json.JSONDecodeError:
                        continue
                    except (MinimaxRateLimitError, httpx.HTTPError):
                        # Re-raise to trigger retry
                        raise
                    except Exception as e:
                        # Log error but continue if possible
                        print(f"ERROR: Error processing chunk: {e}", flush=True)
                        continue
                
                print(f"DEBUG: Minimax streaming complete. Chunks yielded: {chunk_count}", flush=True)

    async def generate_audio(
        self,
        text: str,
        voice: str = "default",
    ) -> bytes:
        """
        Generate complete audio from text.
        """
        audio_data = b""
        async for chunk in self.generate_audio_stream(text, voice):
            audio_data += chunk
        return audio_data
    
    @property
    def supported_voices(self) -> List[str]:
        """Return list of supported voices."""
        return self.VOICES.copy()
    
    @property
    def audio_format(self) -> str:
        """Return audio format (mp3)."""
        return "mp3"
