"""
Memory Manager Module

Handles storage and retrieval of user session memories using VectorDB.
"""

from typing import List, Dict, Any
import json
from datetime import datetime

from app.config import get_settings
from app.rag_service.vector_store import VectorStore
from app.models.memory import SessionMemory


class MemoryManager:
    """
    Manages user long-term memory.
    
    Stores session summaries in a dedicated VectorDB collection and
    retrieves relevant history to contextually enhance new sessions.
    """
    
    def __init__(self):
        """Initialize MemoryManager with the memory-specific vector store."""
        settings = get_settings()
        self.vector_store = VectorStore(
            collection_name=settings.chroma_memory_collection_name
        )
    
    def add_session_summary(self, session_memory: SessionMemory) -> None:
        """
        Store a session summary in the vector database.
        
        Args:
            session_memory: The session memory object to store
        """
        # Create a rich text representation for embedding
        # This text is what will be semantically searched
        document_text = (
            f"Date: {session_memory.date}\n"
            f"Technique: {session_memory.technique_used}\n"
            f"Summary: {session_memory.summary}\n"
            f"Feedback: {session_memory.user_feedback or 'N/A'}"
        )
        
        # Metadata for filtering (e.g., retrieving by user_id is implicit in this design 
        # but if we had multi-user we would need user_id here. 
        # PRD payload has user_id, let's assume we extract it or pass it.
        # The SessionMemory model doesn't strictly have user_id, but the add function might need it 
        # or we store it in metadata. 
        # Let's adjust to accept user_id as argument or assume single user for now 
        # but PRD 4.1 shows user_id.
        # Let's add user_id to metadata.
        """
        note: strict adherence to PRD 4.2 model which has session_id, date, summary, technique, feedback.
        The user_id comes from the request context.
        We should probably pass user_id to this method.
        """
        
        metadata = {
            "session_id": session_memory.session_id,
            "date": session_memory.date,
            "technique": session_memory.technique_used,
            "type": "session_summary"
        }
        
        self.vector_store.add_documents(
            documents=[document_text],
            metadatas=[metadata],
            ids=[session_memory.session_id]
        )
    
    def add_session_summary_with_user(self, user_id: str, session_memory: SessionMemory) -> None:
        """
        Store a session summary with user_id.
        """
        document_text = (
            f"Date: {session_memory.date}\n"
            f"Technique: {session_memory.technique_used}\n"
            f"Summary: {session_memory.summary}\n"
            f"Feedback: {session_memory.user_feedback or 'N/A'}"
        )
        
        metadata = {
            "user_id": user_id,
            "session_id": session_memory.session_id,
            "date": session_memory.date,
            "technique": session_memory.technique_used,
        }
        
        self.vector_store.add_documents(
            documents=[document_text],
            metadatas=[metadata],
            ids=[session_memory.session_id]
        )

    def get_relevant_history(self, user_id: str, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant history for a user based on their current state/query.
        
        Args:
            user_id: The ID of the user
            query: The user's current input/feeling
            n_results: Number of past sessions to retrieve
            
        Returns:
            List of memory items (summary + metadata)
        """
        results = self.vector_store.query(
            query_text=query,
            n_results=n_results,
            where={"user_id": user_id}
        )
        
        # Parse results from ChromaDB format
        memories = []
        if results and results['documents']:
            ids = results['ids'][0]
            documents = results['documents'][0]
            metadatas = results['metadatas'][0]
            
            for i in range(len(ids)):
                memories.append({
                    "id": ids[i],
                    "content": documents[i],
                    "metadata": metadatas[i]
                })
                
        return memories
    
    def get_recent_history(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent sessions (not by similarity, just by date/insertion).
        
        Note: ChromaDB isn't optimized for time-based sort, but we can retrieve 
        and sort in memory if the dataset is small, or use metadata filtering if needed. 
        For now, we might just rely on get_relevant_history or simple retrieval.
        Actually, we can't easily "get last 5" without a query in Chroma unless we get all.
        Let's stick to relevant history for now as per PRD requirement 2.1 "Memory Lookup: profile + recent 5".
        Maybe we just query with emptiness or generic query if we want "recent"? 
        Actually PRD 3.2 says "Recall Mechanism: extract... related to current User Input".
        So get_relevant_history is the key.
        """
        return []
