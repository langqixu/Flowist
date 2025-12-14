"""
User Data Models

Defines the user profile structure for memory and personalization.
Based on PRD Section 3.2 Memory System requirements.
"""

from typing import Optional

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """
    User profile for personalization and memory.
    
    Stores basic user information used for building rapport
    and personalizing meditation guidance.
    
    Based on PRD Section 3.2: User Profile requirements.
    
    Attributes:
        user_id: Unique user identifier
        name: User's preferred name/nickname
        occupation: User's occupation (optional)
        meditation_level: User's meditation experience level
        preferences: Additional user preferences
    """
    user_id: str = Field(
        ...,
        description="Unique user identifier",
        examples=["u12345"],
    )
    name: str = Field(
        ...,
        description="User's preferred name or nickname",
        examples=["小明", "Alice"],
    )
    occupation: Optional[str] = Field(
        default=None,
        description="User's occupation",
        examples=["软件工程师", "Teacher"],
    )
    meditation_level: str = Field(
        default="beginner",
        description="User's meditation experience level",
        examples=["beginner", "intermediate", "advanced"],
    )
    preferences: Optional[dict] = Field(
        default=None,
        description="Additional user preferences (e.g., preferred techniques, voice style)",
        examples=[{"preferred_duration": 10, "preferred_voice": "calm"}],
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "u12345",
                    "name": "小明",
                    "occupation": "软件工程师",
                    "meditation_level": "beginner",
                    "preferences": {"preferred_duration": 10},
                }
            ]
        }
    }
