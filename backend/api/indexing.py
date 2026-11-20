from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db
from backend.services.indexing_service import indexing_service

router = APIRouter(prefix="/index", tags=["Vector Index"])


@router.post("/{paper_id}")
async def index_paper(paper_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await indexing_service.index_paper(db, paper_id)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Vector indexing unavailable: {exc}") from exc


@router.get("/search")
async def vector_search(query: str = Query(..., min_length=2), limit: int = Query(8, ge=1, le=50)):
    try:
        return {"query": query, "results": indexing_service.search(query, limit)}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Vector search unavailable: {exc}") from exc
