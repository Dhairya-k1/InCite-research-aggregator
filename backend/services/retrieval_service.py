from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.evidence_service import evidence_service


class RetrievalService:
    @staticmethod
    def fuse(lexical: list[dict], semantic: list[dict], limit: int, rrf_k: int = 60) -> list[dict]:
        scores: dict[str, float] = {}
        payloads: dict[str, dict] = {}
        for rank, item in enumerate(lexical, 1):
            key = item.get("chunk_id") or item.get("payload", {}).get("chunk_id")
            if not key:
                continue
            scores[key] = scores.get(key, 0) + 1 / (rrf_k + rank)
            payloads[key] = item if "text" in item else item.get("payload", {})
        for rank, item in enumerate(semantic, 1):
            payload = item.get("payload", item)
            key = payload.get("chunk_id")
            if not key:
                continue
            scores[key] = scores.get(key, 0) + 1 / (rrf_k + rank)
            payloads[key] = payload
        return [dict(payloads[key], rrf_score=round(scores[key], 6))
                for key in sorted(scores, key=scores.get, reverse=True)[:limit]]

    async def search(self, db: AsyncSession, query: str, limit: int = 8) -> dict:
        lexical = await evidence_service.search(db, query, limit=limit * 2)
        semantic: list[dict] = []
        semantic_error = None
        try:
            from rag.retrieval.qdrant_client import VectorDatabase
            semantic = VectorDatabase().search(query, limit=limit * 2)
        except Exception as exc:
            semantic_error = str(exc)
        candidates = self.fuse(lexical, semantic, limit * 3)
        from rag.retrieval.reranker import Reranker
        reranked = Reranker().rerank(query, candidates, top_n=limit)
        results = sorted(reranked, key=lambda item: item.get("rerank_score", 0), reverse=True)
        return {"query": query, "mode": "hybrid-reranked" if semantic else "lexical-fallback-reranked",
                "results": results, "semantic_error": semantic_error}


retrieval_service = RetrievalService()
