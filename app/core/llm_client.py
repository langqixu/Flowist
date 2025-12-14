"""
LLM Client Module

Wrapper for LLM API calls (OpenAI/Claude).
Supports streaming responses for low-latency meditation generation.
"""

from typing import AsyncGenerator

from openai import AsyncOpenAI

from app.config import get_settings


class LLMClient:
    """
    LLM API client wrapper.
    
    Provides unified interface for LLM calls with streaming support.
    """
    
    def __init__(self):
        settings = get_settings()
        
        # Initialize OpenAI client with optional custom base_url
        client_kwargs = {"api_key": settings.openai_api_key}
        if settings.openai_base_url:
            client_kwargs["base_url"] = settings.openai_base_url
        
        self.client = AsyncOpenAI(**client_kwargs)
        self.model = settings.openai_model
    
    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """
        Generate meditation script with streaming.
        
        Args:
            prompt: Complete formatted prompt
            
        Yields:
            Text chunks as they are generated
        """
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            stream=True,
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def generate(self, prompt: str) -> str:
        """
        Generate meditation script (non-streaming).
        
        Args:
            prompt: Complete formatted prompt
            
        Returns:
            Complete generated text
        """
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        
        return response.choices[0].message.content or ""
