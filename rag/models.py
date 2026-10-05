from pydantic import BaseModel, Field
from typing import List, Optional

class PaperMetadata(BaseModel):
    paper_id: str
    title: str
    authors: List[str]
    source: str
    version: int

class Chunk(BaseModel):
    chunk_id: str
    paper_id: str
    text: str
    chunk_index: int
    section: Optional[str] = None
    page: Optional[int] = None
    
    # Metadata for evaluation and hybrid search
    strategy: str = Field(description="e.g., 'fixed-size' or 'section-aware'")

class SourceEvidence(BaseModel):
    paper_id: str = Field(description="The unique identifier of the paper")
    section: Optional[str] = Field(None, description="The specific section where the evidence was found (e.g., 'Methodology')")
    page: Optional[int] = Field(None, description="The page number, if available")

class RAGResponse(BaseModel):
    answer: str = Field(description="The detailed, grounded answer to the user's question.")
    sources: List[SourceEvidence] = Field(description="List of sources directly referenced to formulate the answer.")