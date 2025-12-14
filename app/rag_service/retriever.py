"""
Knowledge Retriever Module

Retrieves relevant knowledge from vector store based on user input.
"""

from typing import List, Optional

from app.rag_service.vector_store import VectorStore


class KnowledgeRetriever:
    """
    Retrieves relevant meditation knowledge based on queries.
    """
    
    def __init__(self):
        """Initialize retriever with vector store."""
        self.vector_store = VectorStore()
    
    def retrieve_knowledge(
        self,
        query: str,
        n_results: int = 3,
        category: Optional[str] = None,
    ) -> str:
        """
        Retrieve relevant knowledge snippets for a query.
        
        Args:
            query: User's feeling/input query
            n_results: Number of results to retrieve (default: 3)
            category: Optional filter by category (techniques, scripts, metaphors)
            
        Returns:
            Formatted string containing retrieved knowledge snippets
        """
        # Build metadata filter if category specified
        where = {"category": category} if category else None
        
        # Query vector store
        results = self.vector_store.query(
            query_text=query,
            n_results=n_results,
            where=where,
        )
        
        # Format results
        if not results['documents'] or not results['documents'][0]:
            return "No relevant knowledge found."
        
        formatted_snippets = []
        
        for idx, (doc, metadata) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0]
        )):
            snippet = f"""
--- Knowledge Snippet {idx + 1} ---
Category: {metadata.get('category', 'unknown')}
Source: {metadata.get('filename', 'unknown')}

{doc.strip()}
"""
            formatted_snippets.append(snippet)
        
        return "\n".join(formatted_snippets)
    
    def retrieve_by_category(
        self,
        query: str,
        category: str,
        n_results: int = 2,
    ) -> str:
        """
        Retrieve knowledge from a specific category.
        
        Args:
            query: User query
            category: Category to retrieve from (techniques, scripts, metaphors)
            n_results: Number of results
            
        Returns:
            Formatted knowledge snippets
        """
        return self.retrieve_knowledge(
            query=query,
            n_results=n_results,
            category=category,
        )
    
    def get_mixed_knowledge(
        self,
        query: str,
    ) -> str:
        """
        Retrieve a mix of knowledge from different categories.
        
        Retrieves 1 technique, 1 script, and 1 metaphor for comprehensive guidance.
        
        Args:
            query: User query
            
        Returns:
            Formatted knowledge from multiple categories
        """
        snippets = []
        
        # Retrieve from each category
        for category in ['techniques', 'scripts', 'metaphors']:
            snippet = self.retrieve_by_category(
                query=query,
                category=category,
                n_results=1,
            )
            if snippet != "No relevant knowledge found.":
                snippets.append(snippet)
        
        return "\n\n".join(snippets) if snippets else "No relevant knowledge found."
