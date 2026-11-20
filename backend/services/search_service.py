from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from backend.database.models import Paper
from backend.api.schemas import SearchResponse, SearchResultItem


class SearchService:
    """Search service executing text search and returning ranked results."""

    async def search(
        self,
        db: AsyncSession,
        query_text: str,
        limit: int = 10,
        category: Optional[str] = None
    ) -> SearchResponse:
        words = [w.strip() for w in query_text.split() if len(w.strip()) > 2]
        
        db_query = select(Paper)
        if category:
            db_query = db_query.where(Paper.primary_category == category)
        
        if words:
            clauses = []
            for w in words:
                clauses.append(Paper.title.ilike(f"%{w}%"))
                clauses.append(Paper.abstract.ilike(f"%{w}%"))
            db_query = db_query.where(or_(*clauses))
        
        db_query = db_query.limit(limit * 2)
        res = await db.execute(db_query)
        candidates = res.scalars().all()

        results: List[SearchResultItem] = []
        lower_query = query_text.lower()

        for p in candidates:
            title_lower = p.title.lower()
            abstract_lower = (p.abstract or "").lower()

            score = 0.50
            if lower_query in title_lower:
                score += 0.45
            elif any(w in title_lower for w in words):
                score += 0.30

            if abstract_lower and any(w in abstract_lower for w in words):
                score += 0.15

            results.append(SearchResultItem(
                paper_id=p.paper_id,
                title=p.title,
                score=min(round(score, 2), 0.99)
            ))

        results.sort(key=lambda x: x.score, reverse=True)
        return SearchResponse(query=query_text, results=results[:limit])


search_service = SearchService()
