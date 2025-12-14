"""
Script Parser Module

Parses meditation scripts into segments for TTS processing.
Handles sentence splitting and pause marker extraction.
"""

import re
from dataclasses import dataclass
from typing import List, Literal
from enum import Enum


class SegmentType(str, Enum):
    """Type of script segment."""
    TEXT = "text"
    PAUSE = "pause"


@dataclass
class ScriptSegment:
    """
    A segment of the meditation script.
    
    Attributes:
        type: Either "text" (to be spoken) or "pause" (silence)
        content: The text content (for text segments) or empty (for pauses)
        duration: Duration in seconds (only for pause segments)
    """
    type: SegmentType
    content: str = ""
    duration: float = 0.0


class ScriptParser:
    """
    Parses meditation scripts into processable segments.
    
    Handles:
    - Sentence boundary detection (。！？.!?\n)
    - Pause marker extraction ([2s], [5s], [10s])
    - Segment ordering for sequential TTS processing
    """
    
    # Regex patterns
    PAUSE_PATTERN = re.compile(r'\[(\d+)s\]')
    SENTENCE_ENDINGS = re.compile(r'([。！？.!?\n]+)')
    
    def parse(self, script: str) -> List[ScriptSegment]:
        """
        Parse a meditation script into segments.
        
        Args:
            script: The full meditation script text
            
        Returns:
            List of ScriptSegment objects in order
        """
        segments = []
        
        # First, split by pause markers
        parts = self.PAUSE_PATTERN.split(script)
        
        i = 0
        while i < len(parts):
            part = parts[i]
            
            # Check if this is a pause duration (number captured by regex)
            if i > 0 and parts[i-1] == '' or (i > 0 and self.PAUSE_PATTERN.match(f"[{part}s]") is None):
                # This is text content
                if part.strip():
                    # Split into sentences for better streaming
                    sentences = self._split_sentences(part)
                    for sentence in sentences:
                        if sentence.strip():
                            segments.append(ScriptSegment(
                                type=SegmentType.TEXT,
                                content=sentence.strip(),
                            ))
            
            # Check if next part is a pause duration
            if i + 1 < len(parts):
                try:
                    duration = int(parts[i + 1])
                    segments.append(ScriptSegment(
                        type=SegmentType.PAUSE,
                        duration=float(duration),
                    ))
                    i += 2  # Skip the duration part
                    continue
                except (ValueError, IndexError):
                    pass
            
            i += 1
        
        return self._merge_and_clean(segments)
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Split by sentence endings but keep the punctuation
        parts = self.SENTENCE_ENDINGS.split(text)
        
        sentences = []
        current = ""
        
        for part in parts:
            if self.SENTENCE_ENDINGS.match(part):
                # This is punctuation, append to current sentence
                current += part
                if current.strip():
                    sentences.append(current.strip())
                current = ""
            else:
                current = part
        
        # Don't forget the last part if it doesn't end with punctuation
        if current.strip():
            sentences.append(current.strip())
        
        return sentences
    
    def _merge_and_clean(self, segments: List[ScriptSegment]) -> List[ScriptSegment]:
        """
        Merge consecutive segments of same type and clean up.
        
        Args:
            segments: Raw segments list
            
        Returns:
            Cleaned segments list
        """
        if not segments:
            return []
        
        cleaned = []
        
        for segment in segments:
            if segment.type == SegmentType.TEXT and not segment.content.strip():
                continue
            if segment.type == SegmentType.PAUSE and segment.duration <= 0:
                continue
            cleaned.append(segment)
        
        return cleaned
    
    def parse_streaming(self, text_chunk: str, buffer: str = "") -> tuple[List[ScriptSegment], str]:
        """
        Parse text in streaming mode.
        
        Accumulates text until a complete sentence or pause marker is found.
        
        Args:
            text_chunk: New text chunk from LLM stream
            buffer: Accumulated text from previous chunks
            
        Returns:
            Tuple of (complete segments, remaining buffer)
        """
        full_text = buffer + text_chunk
        segments = []
        
        # Look for pause markers
        pause_match = self.PAUSE_PATTERN.search(full_text)
        if pause_match:
            # Extract text before pause
            before_pause = full_text[:pause_match.start()]
            if before_pause.strip():
                segments.append(ScriptSegment(
                    type=SegmentType.TEXT,
                    content=before_pause.strip(),
                ))
            
            # Add pause
            duration = int(pause_match.group(1))
            segments.append(ScriptSegment(
                type=SegmentType.PAUSE,
                duration=float(duration),
            ))
            
            # Continue with remaining text
            remaining = full_text[pause_match.end():]
            return segments, remaining
        
        # Look for complete sentences
        last_sentence_end = -1
        for match in self.SENTENCE_ENDINGS.finditer(full_text):
            last_sentence_end = match.end()
        
        if last_sentence_end > 0:
            complete_text = full_text[:last_sentence_end]
            remaining = full_text[last_sentence_end:]
            
            sentences = self._split_sentences(complete_text)
            for sentence in sentences:
                if sentence.strip():
                    segments.append(ScriptSegment(
                        type=SegmentType.TEXT,
                        content=sentence.strip(),
                    ))
            
            return segments, remaining
        
        # No complete segment yet, keep buffering
        return [], full_text
