"""
Admin Documents API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from typing import List, Optional

router = APIRouter()

KNOWLEDGE_BASE_DIR = "knowledge_base"

class Document(BaseModel):
    id: str  # relative path
    name: str
    category: str
    content: Optional[str] = None
    size: int
    last_modified: float

class CreateDocument(BaseModel):
    category: str
    filename: str
    content: str

class UpdateDocument(BaseModel):
    content: str


@router.get("/", response_model=List[Document])
async def list_documents(category: Optional[str] = None):
    """List all documents in knowledge base"""
    docs = []
    
    # Categories to scan
    categories = ["techniques", "scripts", "metaphors"]
    if category and category in categories:
        categories = [category]
    
    for cat in categories:
        dir_path = os.path.join(KNOWLEDGE_BASE_DIR, cat)
        if not os.path.exists(dir_path):
            continue
            
        for filename in os.listdir(dir_path):
            if not filename.endswith(".md") or filename == "README.md":
                continue
                
            file_path = os.path.join(dir_path, filename)
            stats = os.stat(file_path)
            
            docs.append(Document(
                id=f"{cat}/{filename}",
                name=filename,
                category=cat,
                size=stats.st_size,
                last_modified=stats.st_mtime
            ))
            
    return docs

@router.get("/{category}/{filename}")
async def get_document(category: str, filename: str):
    """Get document content"""
    file_path = os.path.join(KNOWLEDGE_BASE_DIR, category, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Document not found")
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    return {"content": content}

@router.post("/")
async def create_document(doc: CreateDocument):
    """Create new document"""
    dir_path = os.path.join(KNOWLEDGE_BASE_DIR, doc.category)
    os.makedirs(dir_path, exist_ok=True)
    
    file_path = os.path.join(dir_path, doc.filename)
    if os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="File already exists")
        
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(doc.content)
        
    return {"status": "success", "path": file_path}

@router.put("/{category}/{filename}")
async def update_document(category: str, filename: str, doc: UpdateDocument):
    """Update existing document"""
    file_path = os.path.join(KNOWLEDGE_BASE_DIR, category, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Document not found")
        
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(doc.content)
        
    return {"status": "success"}

@router.delete("/{category}/{filename}")
async def delete_document(category: str, filename: str):
    """Delete document"""
    file_path = os.path.join(KNOWLEDGE_BASE_DIR, category, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Document not found")
        
    os.remove(file_path)
    return {"status": "success"}
