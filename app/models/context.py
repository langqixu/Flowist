"""
Context Data Models

Defines the input payload structure from frontend to backend.
Strictly follows PRD Section 4.1 naming conventions.
"""

from pydantic import BaseModel, Field


class CurrentContext(BaseModel):
    """
    Environment context information.
    
    Captured from client device to provide situational awareness.
    
    Attributes:
        local_time: Local time string, e.g., "23:15"
        weather: Weather condition, e.g., "Heavy Rain"
        location: Location type, e.g., "Home", "Office"
    """
    local_time: str = Field(
        ...,
        description="Local time in HH:MM format",
        examples=["23:15", "07:30"],
    )
    weather: str = Field(
        ...,
        description="Current weather condition",
        examples=["Heavy Rain", "Sunny", "Cloudy"],
    )
    location: str = Field(
        ...,
        description="Location type",
        examples=["Home", "Office", "Outdoors"],
    )


class ContextPayload(BaseModel):
    """
    Input payload from frontend to backend.
    
    Contains user identification, environmental context, and 
    user's current feeling/state description.
    
    Follows PRD Section 4.1 structure exactly.
    
    Attributes:
        user_id: Unique user identifier
        current_context: Environmental context (time, weather, location)
        user_feeling_input: User's description of current state
    """
    user_id: str = Field(
        ...,
        description="Unique user identifier",
        examples=["u12345"],
    )
    current_context: CurrentContext = Field(
        ...,
        description="Current environmental context",
    )
    user_feeling_input: str = Field(
        ...,
        description="User's description of their current feeling/state",
        examples=["今天工作压力很大，脑子停不下来，肩膀很紧。"],
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "u12345",
                    "current_context": {
                        "local_time": "23:15",
                        "weather": "Heavy Rain",
                        "location": "Home",
                    },
                    "user_feeling_input": "今天工作压力很大，脑子停不下来，肩膀很紧。",
                }
            ]
        }
    }
