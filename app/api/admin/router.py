
"""
Admin API Router
"""

from fastapi import APIRouter
from app.api.admin import documents, vectordb

router = APIRouter()

router.include_router(documents.router, prefix="/documents", tags=["Admin Documents"])
router.include_router(vectordb.router, prefix="/vectordb", tags=["Admin VectorDB"])
