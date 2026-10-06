from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db
from backend.services.paper_service import paper_service
from backend.api.schemas import (
    PaperContract, PaperDetailResponse, PaperNewsItem, PaginatedPapersResponse
)

router = APIRouter(prefix="/papers", tags=["Papers"])


@router.get("/latest", response_model=List[PaperContract], summary="Get Latest Research Papers")
async def get_latest_papers(
    limit: int = Query(10, ge=1, le=50, description="Max number of latest papers to return"),
    db: AsyncSession = Depends(get_db)
):

    return await paper_service.get_latest_papers(db=db, limit=limit)


@router.get("", response_model=PaginatedPapersResponse, summary="List Research Papers")
async def list_papers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    source: Optional[str] = Query(None, description="Filter by source (arxiv, openalex)"),
    category: Optional[str] = Query(None, description="Filter by primary category (e.g., cs.AI)"),
    search: Optional[str] = Query(None, description="Search term in title or abstract"),
    db: AsyncSession = Depends(get_db)
):
    """
    Paginated research papers with filtering and search support.
    """
    return await paper_service.list_papers(
        db=db,
        page=page,
        limit=limit,
        source=source,
        category=category,
        search=search
    )


@router.get("/{id}/news", response_model=List[PaperNewsItem], summary="Get Paper News Highlights")
async def get_paper_news(
    id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Returns AI-generated research news highlights and breakthroughs for a paper.
    Supports the 'Research News' tab on Vedant's Paper page.
    """
    news = await paper_service.get_paper_news(db=db, paper_id=id)
    return news


@router.get("/{id}", response_model=PaperDetailResponse, summary="Get Paper Details")
async def get_paper_by_id(
    id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetches comprehensive paper details, including author profiles, version history, and news.
    """
    paper = await paper_service.get_paper_by_id(db=db, paper_id=id)
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with ID '{id}' not found."
        )
    return paper
