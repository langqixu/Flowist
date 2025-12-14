
"""
Admin VectorDB API
"""
from fastapi import APIRouter
from app.rag_service.vector_store import VectorStore
import subprocess
import asyncio

router = APIRouter()

@router.get("/stats")
async def get_vectordb_stats():
    """Get vector database statistics"""
    from app.config import get_settings
    settings = get_settings()
    
    store = VectorStore()
    count = store.get_collection_count()
    
    return {
        "document_count": count,
        "collection_name": store.collection_name,
        "persist_directory": settings.chroma_persist_directory
    }

@router.post("/reimport")
async def reimport_knowledge_base():
    """Trigger knowledge base re-import"""
    # Run ingestion script as subprocess
    try:
        process = await asyncio.create_subprocess_exec(
            "python3", "-m", "app.rag_service.ingest_knowledge",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            return {
                "status": "success",
                "message": "Knowledge base re-imported successfully",
                "logs": stdout.decode()
            }
        else:
            return {
                "status": "error", 
                "message": "Import failed",
                "error": stderr.decode()
            }
            
    except Exception as e:
        return {"status": "error", "message": str(e)}
