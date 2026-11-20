from typing import List, Dict, Any
from rag.retrieval.qdrant_client import VectorDatabase
from rag.retrieval.keyword_search import KeywordSearchIndex

class HybridRetriever:
    """
    Combines Qdrant Dense Vector Search and BM25 Lexical Search via RRF.
    """
    def __init__(self, vector_db: VectorDatabase, keyword_index: KeywordSearchIndex, rrf_k: int = 60):
        self.vector_db = vector_db
        self.keyword_index = keyword_index
        self.rrf_k = rrf_k

    def _reciprocal_rank_fusion(
        self, 
        vector_results: List[Dict[str, Any]], 
        keyword_results: List[Dict[str, Any]], 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Combines ranked lists using RRF scoring."""
        rrf_scores: Dict[str, float] = {}
        payload_map: Dict[str, Dict[str, Any]] = {}

        # Process Dense Vector Results
        for rank, res in enumerate(vector_results, start=1):
            chunk_id = res['payload']['chunk_id']
            payload_map[chunk_id] = res['payload']
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (1.0 / (self.rrf_k + rank))

        # Process Keyword Results
        for rank, res in enumerate(keyword_results, start=1):
            chunk_id = res['payload']['chunk_id']
            payload_map[chunk_id] = res['payload']
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (1.0 / (self.rrf_k + rank))

        # Sort chunk IDs by fused RRF score descending
        sorted_ids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)[:limit]

        return [
            {
                "rrf_score": rrf_scores[cid],
                "payload": payload_map[cid]
            }
            for cid in sorted_ids
        ]

    def search(self, query: str, limit: int = 10, strategy: str = None) -> List[Dict[str, Any]]: # type: ignore
        """
        Executes parallel vector + keyword search and merges candidates.
        """
        # Fetch candidate pools (larger pool size than final limit)
        candidate_limit = limit * 2
        vector_candidates = self.vector_db.search(query, limit=candidate_limit, strategy=strategy)
        keyword_candidates = self.keyword_index.search(query, limit=candidate_limit)

        # Merge via RRF
        return self._reciprocal_rank_fusion(vector_candidates, keyword_candidates, limit=limit)