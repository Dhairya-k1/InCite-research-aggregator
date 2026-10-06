from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db
from backend.services.search_service import search_service
from backend.api.schemas import SearchRequest, SearchResponse

router = APIRouter(tags=["Search"])


@router.post("/search", response_model=SearchResponse, status_code=status.HTTP_200_OK, summary="Search Research Papers")
async def search_papers(
    req: SearchRequest,
    db: AsyncSession = Depends(get_db)
):

    return await search_service.search(
        db=db,
        query_text=req.query,
        limit=req.limit,
        category=req.category
    )
