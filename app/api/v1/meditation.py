"""
Meditation API Endpoints

Provides HTTP endpoints for:
- Generating meditation sessions
- Streaming meditation scripts
- Streaming synchronized audio and text
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
import base64
import logging
import time
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
from pydantic import BaseModel
from typing import Optional

from app.models.context import ContextPayload
from app.core.meditation_service import MeditationService

router = APIRouter()

# Initialize meditation service (singleton for the API)
meditation_service = MeditationService()


class SessionFeedbackRequest(BaseModel):
    """Request body for session feedback."""
    summary: str
    technique_used: str
    user_feedback: Optional[str] = None


@router.post("/session")
async def create_meditation_session(payload: ContextPayload):
    """
    Create a new meditation session.
    
    Receives user context and feeling input, triggers the meditation
    generation pipeline (RAG -> Memory -> Prompt -> LLM).
    
    Args:
        payload: ContextPayload containing user_id, current_context, 
                 and user_feeling_input.
    
    Returns:
        Generated meditation script with session metadata.
    """
    try:
        # Generate meditation script using the service
        result = await meditation_service.generate_meditation(
            context_payload=payload,
        )
        
        return {
            "status": "success",
            "session_id": result["session_id"],
            "user_id": result["user_id"],
            "script": result["script"],
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate meditation: {str(e)}"
        )


from app.core.session_audio import audio_manager
from fastapi import Response

@router.get("/audio/{session_id}/{seq_id}")
async def get_meditation_audio(session_id: str, seq_id: int):
    """
    Retrieve cached audio chunk for a session.
    """
    audio_data = audio_manager.get_chunk(session_id, seq_id)
    if not audio_data:
        raise HTTPException(status_code=404, detail="Audio chunk not found")
        
    return Response(content=audio_data, media_type="audio/mpeg")


@router.post("/session/stream")
async def create_meditation_session_stream(payload: ContextPayload):
    """
    Create a new meditation session with streaming response (SSE).
    
    Same as /session but streams the response as it's generated,
    reducing perceived latency.
    
    Args:
        payload: ContextPayload containing user_id, current_context, 
                 and user_feeling_input.
    
    Returns:
        StreamingResponse with text/event-stream content type.
    """
    async def generate():
        try:
            async for chunk in meditation_service.generate_meditation_stream(
                context_payload=payload,
            ):
                # SSE format: data: <content>\n\n
                yield f"data: {chunk}\n\n"
            
            # Signal end of stream
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/session/{session_id}/feedback")
async def submit_session_feedback(
    session_id: str,
    feedback: SessionFeedbackRequest,
    user_id: str,
):
    """
    Submit feedback for a completed session.
    
    Stores the session summary in memory for future recall.
    
    Args:
        session_id: The unique session identifier
        feedback: Summary, technique used, and optionally user feedback
        user_id: The user who completed the session
    
    Returns:
        Confirmation of feedback storage.
    """
    try:
        meditation_service.save_session_summary(
            user_id=user_id,
            session_id=session_id,
            summary=feedback.summary,
            technique_used=feedback.technique_used,
            user_feedback=feedback.user_feedback,
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "message": "Session summary stored successfully.",
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store session feedback: {str(e)}"
        )




@router.post("/session/audio")
async def create_meditation_audio_session(payload: ContextPayload):
    """
    Create a meditation session with audio response (POST).
    """
    from app.audio_service.audio_service import AudioService
    
    # 1. Generate Script (Sync/Await) - Fails with 500 if error
    try:
        print(f"DEBUG: Generating meditation script for user {payload.user_id}", flush=True)
        result = await meditation_service.generate_meditation(context_payload=payload)
        script = result["script"]
        print(f"DEBUG: Script generated ({len(script)} chars)", flush=True)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Script generation failed: {e}")

    # 2. Init Audio Service
    try:
        print(f"DEBUG: Initializing AudioService...", flush=True)
        audio_service = AudioService()
        print(f"DEBUG: AudioService initialized successfully", flush=True)
    except Exception as e:
        print(f"DEBUG: AudioService init failed: {e}", flush=True)
        raise HTTPException(status_code=500, detail=f"Audio service init failed: {e}")
    
    # 3. Stream Audio
    async def generate_audio():
        print("DEBUG: Starting audio stream...", flush=True)
        try:
            chunk_count = 0
            total_bytes = 0
            async for chunk in audio_service.generate_audio_from_text(script):
                if chunk.data:
                    chunk_count += 1
                    total_bytes += len(chunk.data)
                    yield chunk.data
            print(f"DEBUG: Stream finished. Chunks: {chunk_count}, Bytes: {total_bytes}", flush=True)
            
            if total_bytes == 0:
                print("ERROR: Generated 0 bytes of audio!", flush=True)
                
        except Exception as e:
            print(f"ERROR: Audio streaming failed: {e}", flush=True)
            import traceback
            traceback.print_exc()
            # Can't change status code here as headers are sent
    
    return StreamingResponse(
        generate_audio(),
        media_type="audio/mpeg",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/session/audio")
async def create_meditation_audio_session_get(
    user_id: str,
    feeling: str,
    time: str = "Night",
    weather: str = "Raining",
    location: str = "Home",
):
    """
    Create a meditation session with audio response (GET).
    
    Simplified endpoint for direct audio streaming in browsers/mobile apps.
    Example: <audio src="/api/v1/meditation/session/audio?user_id=123&feeling=stressed..." />
    """
    from app.models.context import CurrentContext
    
    payload = ContextPayload(
        user_id=user_id,
        user_feeling_input=feeling,
        current_context=CurrentContext(
            local_time=time,
            weather=weather,
            location=location,
        )
    )
    
    return await create_meditation_audio_session(payload)


@router.post("/session/audio-text-stream")
async def create_meditation_audio_text_stream(payload: ContextPayload):
    """
    Create a meditation session with synchronized audio and text streaming.
    
    Streams both text and audio in real-time, allowing frontend to:
    1. Display text as subtitles
    2. Play audio chunks incrementally
    3. Show background music immediately
    
    This approach naturally avoids rate limiting by spacing TTS requests
    with LLM generation time (1-3s per sentence).
    
    Response format (SSE):
    - {"type": "text", "content": "Sentence..."}
    - {"type": "audio", "content": "base64_audio", "text": "Sentence..."}
    - {"type": "pause", "duration": 5}
    - {"type": "done"}
    """
    import base64
    from app.audio_service.audio_service import AudioService
    
    audio_service = AudioService()
    
    async def generate():
        try:
            # Generate a unique session ID for this stream if not present
            import uuid
            session_id = str(uuid.uuid4())
            
            start_time = time.time()
            logger.info(f"[SSE] Stream started, session: {session_id}")
            
            # Send session start event with ID
            yield f"data: {json.dumps({'type': 'session_start', 'session_id': session_id})}\n\n"
            
            logger.info("Starting audio-text-stream generation for user: %s", payload.user_id)
            sentence_buffer = ""
            sentence_count = 0
            processed_hashes = set()  # Use hash for dedup
            
            # Stream text from LLM
            async for text_chunk in meditation_service.generate_meditation_stream(
                context_payload=payload,
            ):
                # Accumulate text into sentences
                sentence_buffer += text_chunk
                
                # Process complete sentences
                import re
                import hashlib
                
                while True:
                    # Find first complete sentence or pause marker
                    match = re.search(r'([^。！？\n]+[。！？]|\[\d+s\])', sentence_buffer)
                    if not match:
                        break
                    
                    sentence = match.group(1).strip()
                    if not sentence:
                        # Remove empty match and continue
                        sentence_buffer = sentence_buffer[match.end():]
                        continue
                    
                    # Dedup check using hash of sentence content
                    sentence_hash = hashlib.md5(sentence.encode('utf-8')).hexdigest()
                    if sentence_hash in processed_hashes:
                        logger.debug("Skipping duplicate sentence (hash: %s)", sentence_hash[:8])
                        sentence_buffer = sentence_buffer[match.end():]
                        continue
                    
                    processed_hashes.add(sentence_hash)
                    sentence_count += 1
                    elapsed = time.time() - start_time
                    logger.info(f"[SSE] Processing sentence {sentence_count} at {elapsed:.2f}s: {sentence[:30]}")
                    
                    # Send text with sequence ID for frontend dedup
                    yield f"data: {json.dumps({'seq': sentence_count, 'type': 'text', 'content': sentence})}\n\n"
                    logger.info(f"[SSE] Yielded text event for seq {sentence_count}")
                    
                    # Remove processed sentence from buffer
                    sentence_buffer = sentence_buffer[match.end():]
                    
                    # Check if it's a pause marker
                    if sentence.startswith('[') and sentence.endswith(']'):
                        pause_match = re.search(r'\[(\d+)s\]', sentence)
                        if pause_match:
                            duration = int(pause_match.group(1))
                            logger.debug("Found pause marker: %ds", duration)
                            yield f"data: {json.dumps({'seq': sentence_count, 'type': 'pause', 'duration': duration})}\n\n"
                        continue
                    
                    # Generate audio for this sentence
                    logger.debug("Generating TTS audio for sentence %d", sentence_count)
                    try:
                        audio_data = b""
                        # Use internal retry loop to ensure buffer is cleared on retry
                        async for attempt in AsyncRetrying(
                            stop=stop_after_attempt(5),
                            wait=wait_exponential(multiplier=1, min=2, max=10),
                            retry=retry_if_exception_type(Exception),
                            reraise=True
                        ):
                            with attempt:
                                audio_data = b""  # CRITICAL: Reset buffer on each attempt
                                async for audio_chunk in audio_service.generate_audio_from_text(sentence):
                                    if audio_chunk.data:
                                        audio_data += audio_chunk.data
                                
                                # CRITICAL FIX: audio_service suppresses exceptions. 
                                # If we get no data, it likely failed. Manually raise to trigger retry.
                                if not audio_data:
                                    logger.warning("TTS returned empty data (likely rate limit), triggering retry...")
                                    raise Exception("Empty audio data from TTS provider")
                        
                        logger.info("TTS generated %d bytes for sentence %d", len(audio_data), sentence_count)
                        
                        if audio_data:
                            # CRITICAL CHANGE: Store audio and send Ref
                            audio_manager.store_chunk(session_id, sentence_count, audio_data)
                            
                            # Calculate exact audio duration using mutagen
                            try:
                                from mutagen.mp3 import MP3
                                from io import BytesIO
                                audio_info = MP3(BytesIO(audio_data))
                                audio_duration = audio_info.info.length
                                logger.info(f"Calculated exact duration: {audio_duration:.2f}s")
                            except Exception as e:
                                logger.error(f"Failed to calculate exact duration with mutagen: {e}")
                                # Fallback to bitrate estimation
                                audio_duration = len(audio_data) / (128000 / 8)
                            
                            # Construct Audio URL
                            audio_url = f"/api/v1/meditation/audio/{session_id}/{sentence_count}"
                            
                            event_data = {
                                'seq': sentence_count, 
                                'type': 'audio_ref', 
                                'url': audio_url,
                                'text': sentence,
                                'duration': audio_duration  # Exact duration
                            }
                            yield f"data: {json.dumps(event_data)}\n\n"
                        else:
                            logger.error("No audio data generated for sentence %d", sentence_count)
                        
                    except Exception as e:
                        logger.error("Audio generation failed for sentence %d: %s", sentence_count, e)
                        # We still yield text even if audio fails
            
            # Process any remaining text in buffer
            if sentence_buffer.strip():
                sentence_count += 1
                logger.debug("Processing final buffer", )
                yield f"data: {json.dumps({'seq': sentence_count, 'type': 'text', 'content': sentence_buffer.strip()})}\n\n"
            
            logger.info("Stream complete. Total sentences: %d", sentence_count)
            # Signal completion
            yield f"data: {json.dumps({'seq': sentence_count + 1, 'type': 'done'})}\n\n"
            
        except Exception as e:
            logger.exception("Stream generation failed")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/session/{session_id}")
async def get_meditation_session(session_id: str):
    """
    Retrieve a meditation session by ID.
    
    Args:
        session_id: The unique session identifier.
    
    Returns:
        Session details (placeholder for now).
    """
    # TODO: Implement session retrieval from database
    return {
        "session_id": session_id,
        "status": "not_implemented",
    }
