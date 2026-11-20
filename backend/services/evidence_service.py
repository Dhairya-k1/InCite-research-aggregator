from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import DocumentChunk


class EvidenceService:
    async def search(self, db: AsyncSession, query: str, limit: int = 8, paper_id: str | None = None):
        terms = [term.strip() for term in query.lower().split() if len(term.strip()) > 2]
        statement = select(DocumentChunk)
        if paper_id:
            statement = statement.where(DocumentChunk.paper_id == paper_id)
        if terms:
            statement = statement.where(or_(*[DocumentChunk.text.ilike(f"%{term}%") for term in terms]))
        rows = (await db.execute(statement.limit(limit * 3))).scalars().all()
        query_terms = set(terms)
        ranked = sorted(rows, key=lambda row: sum(term in row.text.lower() for term in query_terms), reverse=True)
        return [{"chunk_id": row.chunk_id, "paper_id": row.paper_id, "text": row.text,
                 "section": row.section, "page": row.page, "score": round(sum(term in row.text.lower() for term in query_terms) / max(len(query_terms), 1), 3)}
                for row in ranked[:limit]]


evidence_service = EvidenceService()
