"""
Meditation Service Module

Main orchestrator for meditation generation.
Coordinates RAG, Memory, User Profile, Prompt Assembly, and LLM calls.

Implements PRD Phase 3 (Agent Core Logic).
"""

from typing import AsyncGenerator, Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.core.llm_client import LLMClient
from app.core.prompt_builder import PromptBuilder
from app.models.context import ContextPayload
from app.models.user import UserProfile
from app.models.memory import SessionMemory
from app.rag_service.retriever import KnowledgeRetriever
from app.memory_service.manager import MemoryManager
from app.user_service.manager import UserProfileManager


class MeditationService:
    """
    Main meditation generation service.
    
    Orchestrates the complete pipeline:
    1. Retrieve/create user profile
    2. Retrieve relevant knowledge (RAG)
    3. Retrieve user memory
    4. Assemble prompt
    5. Generate meditation script via LLM
    6. Store session summary (post-generation)
    """
    
    def __init__(
        self,
        memory_manager: Optional[MemoryManager] = None,
        user_manager: Optional[UserProfileManager] = None,
        knowledge_retriever: Optional[KnowledgeRetriever] = None,
        llm_client: Optional[LLMClient] = None,
    ):
        """
        Initialize MeditationService with dependencies.
        
        Args:
            memory_manager: Manager for user session history
            user_manager: Manager for user profiles
            knowledge_retriever: RAG knowledge retriever
            llm_client: LLM API client
        """
        self.prompt_builder = PromptBuilder()
        self.llm_client = llm_client or LLMClient()
        self.knowledge_retriever = knowledge_retriever or KnowledgeRetriever()
        self.memory_manager = memory_manager or MemoryManager()
        self.user_manager = user_manager or UserProfileManager()
    
    def _format_memory_for_prompt(self, memories: List[Dict[str, Any]]) -> str:
        """
        Format retrieved memories into a prompt-friendly string.
        
        Args:
            memories: List of memory items from MemoryManager
            
        Returns:
            Formatted string for the prompt
        """
        if not memories:
            return "No previous sessions found."
        
        formatted = []
        for mem in memories:
            content = mem.get("content", "")
            metadata = mem.get("metadata", {})
            date = metadata.get("date", "Unknown date")
            formatted.append(f"[{date}] {content}")
        
        return "\n\n".join(formatted)
    
    async def generate_meditation(
        self,
        context_payload: ContextPayload,
        user_profile: Optional[UserProfile] = None,
    ) -> Dict[str, Any]:
        """
        Generate a complete meditation script.
        
        Args:
            context_payload: User's current context and feeling
            user_profile: Optional user profile (if not provided, will be retrieved/created)
            
        Returns:
            Dict containing:
                - session_id: Unique session identifier
                - script: Generated meditation script
                - technique: Detected/used technique (placeholder)
        """
        user_id = context_payload.user_id
        
        # Get or create user profile
        if user_profile is None:
            user_profile = self.user_manager.get_or_create_default(user_id)
        
        # Retrieve relevant knowledge from RAG
        knowledge_snippets = self.knowledge_retriever.retrieve_knowledge(
            query=context_payload.user_feeling_input,
            n_results=3,
        )
        
        # Retrieve relevant memory
        memories = self.memory_manager.get_relevant_history(
            user_id=user_id,
            query=context_payload.user_feeling_input,
            n_results=3,
        )
        memory_summary = self._format_memory_for_prompt(memories)
        
        # Build prompt
        prompt = self.prompt_builder.build_prompt(
            context_payload=context_payload,
            user_profile=user_profile,
            memory_summary=memory_summary,
            knowledge_snippets=knowledge_snippets,
        )
        
        # Generate via LLM
        script = await self.llm_client.generate(prompt)
        
        # Generate session ID
        session_id = f"s_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:6]}"
        
        return {
            "session_id": session_id,
            "script": script,
            "user_id": user_id,
        }
    
    async def generate_meditation_stream(
        self,
        context_payload: ContextPayload,
        user_profile: Optional[UserProfile] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Generate meditation script with streaming.
        
        Args:
            context_payload: User's current context and feeling
            user_profile: Optional user profile
            
        Yields:
            Text chunks as they are generated
        """
        user_id = context_payload.user_id
        
        # Get or create user profile
        if user_profile is None:
            user_profile = self.user_manager.get_or_create_default(user_id)
        
        # Retrieve relevant knowledge from RAG
        knowledge_snippets = self.knowledge_retriever.retrieve_knowledge(
            query=context_payload.user_feeling_input,
            n_results=3,
        )
        
        # Retrieve relevant memory
        memories = self.memory_manager.get_relevant_history(
            user_id=user_id,
            query=context_payload.user_feeling_input,
            n_results=3,
        )
        memory_summary = self._format_memory_for_prompt(memories)
        
        # Build prompt
        prompt = self.prompt_builder.build_prompt(
            context_payload=context_payload,
            user_profile=user_profile,
            memory_summary=memory_summary,
            knowledge_snippets=knowledge_snippets,
        )
        
        # Generate via LLM with streaming
        async for chunk in self.llm_client.generate_stream(prompt):
            yield chunk
    
    def save_session_summary(
        self,
        user_id: str,
        session_id: str,
        summary: str,
        technique_used: str,
        user_feedback: Optional[str] = None,
    ) -> None:
        """
        Save a session summary to memory for future recall.
        
        This should be called after a meditation session completes.
        
        Args:
            user_id: The user who completed the session
            session_id: Unique session identifier
            summary: Summary of the session (user's state, context)
            technique_used: Meditation technique that was used
            user_feedback: Optional user feedback
        """
        session_memory = SessionMemory(
            session_id=session_id,
            date=datetime.now().strftime("%Y-%m-%d"),
            summary=summary,
            technique_used=technique_used,
            user_feedback=user_feedback,
        )
        
        self.memory_manager.add_session_summary_with_user(user_id, session_memory)
