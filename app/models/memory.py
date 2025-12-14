"""
Memory Data Models

Defines the session memory structure stored in VectorDB.
Strictly follows PRD Section 4.2 naming conventions.
"""

from typing import Optional

from pydantic import BaseModel, Field


class SessionMemory(BaseModel):
    """
    Session memory structure stored in VectorDB.
    
    Captures the summary of each meditation session for retrieval
    and continuity across sessions.
    
    Follows PRD Section 4.2 structure exactly.
    
    Attributes:
        session_id: Unique session identifier
        date: Session date in YYYY-MM-DD format
        summary: Summary of the session (user's pain points, context)
        technique_used: Meditation technique applied
        user_feedback: Optional user feedback after session
    """
    session_id: str = Field(
        ...,
        description="Unique session identifier",
        examples=["s_9876"],
    )
    date: str = Field(
        ...,
        description="Session date in YYYY-MM-DD format",
        examples=["2023-10-27"],
    )
    summary: str = Field(
        ...,
        description="Summary of the session including user's state and context",
        examples=["User reported high anxiety due to deadline. Shoulders were tense."],
    )
    technique_used: str = Field(
        ...,
        description="Meditation technique applied during the session",
        examples=["Body Scan", "Box Breathing", "4-7-8 Breathing"],
    )
    user_feedback: Optional[str] = Field(
        default=None,
        description="Optional user feedback after the session",
        examples=["Felt better but still distracted."],
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "session_id": "s_9876",
                    "date": "2023-10-27",
                    "summary": "User reported high anxiety due to deadline. Shoulders were tense.",
                    "technique_used": "Body Scan",
                    "user_feedback": "Felt better but still distracted.",
                }
            ]
        }
    }
