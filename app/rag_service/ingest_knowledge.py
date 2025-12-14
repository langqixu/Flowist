"""
Knowledge Base Ingestion Script

Reads markdown files from knowledge_base/ directory,
chunks them, and ingests into ChromaDB vector store.
"""

import os
from pathlib import Path
from typing import List, Tuple

from app.rag_service.vector_store import VectorStore


class KnowledgeIngester:
    """
    Handles ingestion of knowledge base documents into vector store.
    """
    
    def __init__(self, knowledge_base_dir: str = "knowledge_base"):
        """
        Initialize ingester.
        
        Args:
            knowledge_base_dir: Path to knowledge base directory
        """
        self.knowledge_base_dir = Path(knowledge_base_dir)
        self.vector_store = VectorStore()
    
    def read_markdown_file(self, filepath: Path) -> str:
        """
        Read content from a markdown file.
        
        Args:
            filepath: Path to markdown file
            
        Returns:
            File content as string
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    def chunk_document(
        self,
        content: str,
        chunk_size: int = 1000,
        overlap: int = 200,
    ) -> List[str]:
        """
        Split document into overlapping chunks.
        
        Args:
            content: Document content
            chunk_size: Maximum chunk size in characters
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + chunk_size
            chunk = content[start:end]
            chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    def collect_documents(self) -> List[Tuple[str, dict, str]]:
        """
        Collect all documents from knowledge base directory.
        
        Returns:
            List of tuples (content, metadata, filepath)
        """
        documents = []
        
        # Iterate through all markdown files
        for filepath in self.knowledge_base_dir.rglob("*.md"):
            # Skip README files
            if filepath.name == "README.md":
                continue
            
            content = self.read_markdown_file(filepath)
            
            # Determine category from parent directory
            category = filepath.parent.name
            
            metadata = {
                "source": str(filepath),
                "category": category,
                "filename": filepath.name,
            }
            
            documents.append((content, metadata, str(filepath)))
        
        return documents
    
    def ingest(self, chunk_documents: bool = True) -> int:
        """
        Ingest all knowledge base documents into vector store.
        
        Args:
            chunk_documents: Whether to chunk documents before ingestion
            
        Returns:
            Number of documents/chunks ingested
        """
        documents = self.collect_documents()
        
        all_texts = []
        all_metadatas = []
        all_ids = []
        
        doc_id_counter = 0
        
        for content, metadata, filepath in documents:
            if chunk_documents:
                chunks = self.chunk_document(content)
                
                for idx, chunk in enumerate(chunks):
                    all_texts.append(chunk)
                    chunk_metadata = metadata.copy()
                    chunk_metadata["chunk_index"] = idx
                    all_metadatas.append(chunk_metadata)
                    all_ids.append(f"doc_{doc_id_counter}_chunk_{idx}")
                
                doc_id_counter += 1
            else:
                all_texts.append(content)
                all_metadatas.append(metadata)
                all_ids.append(f"doc_{doc_id_counter}")
                doc_id_counter += 1
        
        # Add to vector store
        if all_texts:
            self.vector_store.add_documents(
                documents=all_texts,
                metadatas=all_metadatas,
                ids=all_ids,
            )
        
        return len(all_texts)


def main():
    """Main ingestion script."""
    print("🚀 Starting knowledge base ingestion...")
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    knowledge_base_path = project_root / "knowledge_base"
    
    if not knowledge_base_path.exists():
        print(f"❌ Knowledge base directory not found: {knowledge_base_path}")
        return
    
    ingester = KnowledgeIngester(str(knowledge_base_path))
    
    # Reset collection (optional - comment out to append instead)
    print("🗑️  Resetting collection...")
    ingester.vector_store.reset_collection()
    
    # Ingest documents
    num_ingested = ingester.ingest(chunk_documents=True)
    
    print(f"✅ Successfully ingested {num_ingested} document chunks")
    print(f"📊 Total documents in collection: {ingester.vector_store.get_collection_count()}")


if __name__ == "__main__":
    main()
