
import logging
from typing import Dict, Optional, Tuple
import time

logger = logging.getLogger(__name__)

class SessionAudioManager:
    """
    Manages in-memory cache of generated audio chunks for meditation sessions.
    This allows audio to be retrieved via standard HTTP GET requests rather than SSE push.
    """
    def __init__(self):
        # Structure: {session_id: {seq_id: (audio_bytes, timestamp)}}
        self._cache: Dict[str, Dict[int, Tuple[bytes, float]]] = {}
        # Simple cleanup threshold (e.g., sessions older than 1 hour)
        self._last_cleanup = time.time()
        
    def store_chunk(self, session_id: str, seq_id: int, audio_data: bytes):
        """Store an audio chunk in memory."""
        if session_id not in self._cache:
            self._cache[session_id] = {}
            
        self._cache[session_id][seq_id] = (audio_data, time.time())
        logger.debug(f"Stored audio chunk for session {session_id}, seq {seq_id} ({len(audio_data)} bytes)")
        
        # Periodic cleanup check
        if time.time() - self._last_cleanup > 3600:
            self.cleanup()

    def get_chunk(self, session_id: str, seq_id: int) -> Optional[bytes]:
        """Retrieve an audio chunk."""
        if session_id in self._cache and seq_id in self._cache[session_id]:
            return self._cache[session_id][seq_id][0]
        return None

    def cleanup(self, max_age_seconds: int = 3600):
        """Remove old sessions."""
        now = time.time()
        sessions_to_remove = []
        
        for session_id, chunks in self._cache.items():
            # Check timestamp of the first available chunk as proxy
            if not chunks:
                sessions_to_remove.append(session_id)
                continue
                
            first_seq = next(iter(chunks))
            _, timestamp = chunks[first_seq]
            
            if now - timestamp > max_age_seconds:
                sessions_to_remove.append(session_id)
                
        for session_id in sessions_to_remove:
            del self._cache[session_id]
            logger.info(f"Cleaned up expired audio session: {session_id}")
            
        self._last_cleanup = now

# Global singleton
audio_manager = SessionAudioManager()
