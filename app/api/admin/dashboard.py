"""
Admin Dashboard API
"""
from fastapi import APIRouter
from app.rag_service.vector_store import VectorStore
import os

router = APIRouter()

KNOWLEDGE_BASE_DIR = "knowledge_base"

@router.get("/stats")
async def get_dashboard_stats():
    """
    Get aggregated dashboard statistics.
    Returns:
        - document_count: Total files in knowledge base
        - chunk_count: Total vector embeddings
    """
    # 1. Get Document Count
    doc_count = 0
    categories = ["techniques", "scripts", "metaphors"]
    for cat in categories:
        dir_path = os.path.join(KNOWLEDGE_BASE_DIR, cat)
        if os.path.exists(dir_path):
            # Count only .md files, exclude README
            files = [f for f in os.listdir(dir_path) if f.endswith(".md") and f != "README.md"]
            doc_count += len(files)
            
    # 2. Get Chunk Count (from VectorStore)
    store_info = {}
    try:
        from app.config import get_settings
        settings = get_settings()
        store = VectorStore()
        chunk_count = store.get_collection_count()
        store_info = {
            "collection_name": store.collection_name,
            "persist_directory": settings.chroma_persist_directory
        }
    except Exception as e:
        # For debugging: return string error if possible, or print to log
        print(f"Error getting chunk count: {e}")
        chunk_count = -1 # Indicator of error
        
    return {
        "document_count": doc_count,
        "chunk_count": chunk_count,
        **store_info
    }
