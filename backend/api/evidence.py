from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.connection import get_db
from backend.services.evidence_service import evidence_service

router = APIRouter(prefix="/evidence", tags=["Evidence"])


@router.get("/search")
async def search_evidence(query: str = Query(..., min_length=2), limit: int = Query(8, ge=1, le=50),
                          paper_id: str | None = None, db: AsyncSession = Depends(get_db)):
    return {"query": query, "results": await evidence_service.search(db, query, limit, paper_id)}
