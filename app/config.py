"""
Flowist Configuration Module

Centralized configuration management using pydantic-settings.
Loads environment variables from .env file.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_base_url: str = ""  # Optional: custom API endpoint (e.g., DeepSeek, Azure, Ollama)
    
    # ChromaDB Configuration
    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_name: str = "flowist_knowledge"
    chroma_memory_collection_name: str = "flowist_memory"
    
    # Optional: Anthropic (Claude)
    anthropic_api_key: str = ""
    
    # Optional: ElevenLabs TTS
    elevenlabs_api_key: str = ""
    
    # Application Settings
    app_env: str = "development"
    debug: bool = True
    
    # TTS Configuration
    tts_provider: str = "openai"  # "openai" | "elevenlabs" | "minimax"
    openai_tts_model: str = "tts-1"  # tts-1 for speed, tts-1-hd for quality
    openai_tts_voice: str = "nova"  # Warm voice suitable for meditation
    elevenlabs_voice_id: str = ""
    minimax_api_key: str = ""
    minimax_group_id: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.
    
    Returns:
        Settings: Application configuration instance.
    """
    return Settings()
