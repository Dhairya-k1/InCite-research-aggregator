from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db
from rag.ingestion.arxiv import fetch_arxiv
from rag.ingestion.openalex import fetch_openalex
from rag.ingestion.service import ingestion_service

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])


@router.post("/{source}")
async def ingest_source(source: str, query: str = Query(..., min_length=2), limit: int = Query(10, ge=1, le=50),
                        db: AsyncSession = Depends(get_db)):
    try:
        records = fetch_arxiv(query, limit) if source.lower() == "arxiv" else fetch_openalex(query, limit) if source.lower() == "openalex" else None
        if records is None:
            raise HTTPException(status_code=400, detail="Supported sources are arxiv and openalex")
        return await ingestion_service.ingest(db, records)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"{source} ingestion failed: {exc}") from exc
