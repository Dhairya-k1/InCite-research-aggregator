from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db
from backend.services.processing_service import processing_service

router = APIRouter(prefix="/processing", tags=["Processing"])


@router.post("/{paper_id}")
async def process_paper(paper_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await processing_service.process_paper(db, paper_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Paper processing failed: {exc}") from exc
