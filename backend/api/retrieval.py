from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db
from backend.services.retrieval_service import retrieval_service

router = APIRouter(prefix="/retrieve", tags=["Retrieval"])


@router.get("/search")
async def retrieve(query: str = Query(..., min_length=2), limit: int = Query(8, ge=1, le=50),
                   db: AsyncSession = Depends(get_db)):
    return await retrieval_service.search(db, query, limit)
