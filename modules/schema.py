from pydantic import BaseModel
from typing import List

class RAGRequest(BaseModel):
    query: str

class RAGResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: float