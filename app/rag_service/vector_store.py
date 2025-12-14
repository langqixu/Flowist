"""
Vector Store Module

Manages ChromaDB vector database for knowledge base storage and retrieval.
"""

from typing import List, Optional
import chromadb
from chromadb.config import Settings

from app.config import get_settings


class VectorStore:
    """
    ChromaDB vector store wrapper.
    
    Handles initialization, document storage, and similarity search
    for the meditation knowledge base.
    """
    
    def __init__(self, collection_name: Optional[str] = None):
        """
        Initialize ChromaDB client and collection.
        
        Args:
            collection_name: Optional name of the collection to use.
                           Defaults to the knowledge base collection from config.
        """
        settings = get_settings()
        
        # Initialize ChromaDB client with persistent storage
        self.client = chromadb.Client(
            Settings(
                persist_directory=settings.chroma_persist_directory,
                anonymized_telemetry=False,
            )
        )
        
        # Get or create collection
        self.collection_name = collection_name or settings.chroma_collection_name
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Flowist meditation data"}
        )
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[dict],
        ids: List[str],
    ) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of text documents to add
            metadatas: List of metadata dicts for each document
            ids: List of unique IDs for each document
        """
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )
    
    def query(
        self,
        query_text: str,
        n_results: int = 3,
        where: Optional[dict] = None,
    ) -> dict:
        """
        Query the vector store for similar documents.
        
        Args:
            query_text: Query string
            n_results: Number of results to return (default: 3)
            where: Optional metadata filter
            
        Returns:
            Query results containing documents, metadatas, and distances
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where,
        )
        return results
    
    def get_collection_count(self) -> int:
        """
        Get the number of documents in the collection.
        
        Returns:
            Number of documents
        """
        return self.collection.count()
    
    def reset_collection(self) -> None:
        """
        Delete and recreate the collection.
        
        Warning: This will delete all stored documents.
        """
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Flowist meditation knowledge base"}
        )
