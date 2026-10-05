from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Team Defined Contracts (Page 6 & 7)
# ---------------------------------------------------------

class PaperContract(BaseModel):
    """Canonical Paper object contract."""
    paper_id: str
    title: str
    authors: List[str] = Field(default_factory=list)
    abstract: Optional[str] = None
    published_at: datetime
    source: str = "arxiv"
    version: int = 1

    class Config:
        from_attributes = True


class SearchResultItem(BaseModel):
    paper_id: str
    title: str
    score: float


class SearchResponse(BaseModel):
    """Search response contract."""
    query: str
    results: List[SearchResultItem] = Field(default_factory=list)


class RAGSource(BaseModel):
    paper_id: str
    section: Optional[str] = None
    page: Optional[int] = None


class RAGResponse(BaseModel):
    """RAG chat response contract."""
    answer: str
    sources: List[RAGSource] = Field(default_factory=list)


# ---------------------------------------------------------
# Endpoint Request & Response Models
# ---------------------------------------------------------

class AuthorDetail(BaseModel):
    author_id: str
    name: str
    affiliation: Optional[str] = None
    orcid: Optional[str] = None

    class Config:
        from_attributes = True


class PaperVersionDetail(BaseModel):
    version_number: int
    title: str
    abstract: Optional[str] = None
    diff_summary: Optional[str] = None
    pdf_url: Optional[str] = None
    published_at: datetime

    class Config:
        from_attributes = True


class PaperNewsItem(BaseModel):
    headline: str
    summary: str
    significance_score: float = 0.0
    published_at: datetime


class PaperDetailResponse(PaperContract):
    doi: Optional[str] = None
    primary_category: Optional[str] = None
    citation_count: int = 0
    authors_detailed: List[AuthorDetail] = Field(default_factory=list)
    versions: List[PaperVersionDetail] = Field(default_factory=list)


class PaginatedPapersResponse(BaseModel):
    items: List[PaperContract]
    total: int
    page: int
    limit: int
    pages: int


class ChatRequest(BaseModel):
    query: str
    paper_id: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    limit: int = 10
    category: Optional[str] = None
