from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import DocumentChunk
from rag.models import Chunk


class IndexingService:
    async def index_paper(self, db: AsyncSession, paper_id: str) -> dict:
        # Qdrant/Gemini are intentionally initialized here, not at API import
        # time, so the metadata API remains usable without an API key.
        from rag.retrieval.qdrant_client import VectorDatabase
        vector_db = VectorDatabase()
        rows = (await db.execute(select(DocumentChunk).where(DocumentChunk.paper_id == paper_id))).scalars().all()
        chunks = [Chunk(chunk_id=row.chunk_id, paper_id=row.paper_id, text=row.text,
                        chunk_index=row.chunk_index, section=row.section, page=row.page,
                        strategy=row.strategy) for row in rows]
        if chunks:
            vector_db.ingest_chunks(chunks)
        return {"paper_id": paper_id, "chunks_indexed": len(chunks), "collection": vector_db.collection_name}

    def search(self, query: str, limit: int = 8) -> list[dict]:
        from rag.retrieval.qdrant_client import VectorDatabase
        return VectorDatabase().search(query, limit=limit)


indexing_service = IndexingService()
