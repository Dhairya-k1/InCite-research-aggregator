from typing import List, Dict, Any
import re
import os

class Reranker:
    """
    Rescores candidate chunks using a lightweight Cross-Encoder model.
    """
    def __init__(self, model_name: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2'):
        self.model = None
        self.model_name = model_name
        try:
            if os.getenv("INCITE_ENABLE_CROSS_ENCODER", "0") != "1":
                return
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(model_name)
        except Exception:
            # A deterministic lexical scorer keeps local/offline development usable.
            self.model = None

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Scores candidate query-passage pairs and sorts by score descending.
        """
        if not candidates:
            return []

        if self.model is not None:
            pairs = [[query, item.get('text', item.get('payload', {}).get('text', ''))] for item in candidates]
            scores = self.model.predict(pairs)
        else:
            query_terms = set(re.findall(r"\w+", query.lower()))
            scores = [sum(term in item.get('text', item.get('payload', {}).get('text', '')).lower()
                          for term in query_terms) / max(len(query_terms), 1) for item in candidates]

        for idx, score in enumerate(scores):
            candidates[idx]['rerank_score'] = float(score)

        sorted_candidates = sorted(
            candidates, 
            key=lambda x: x['rerank_score'], 
            reverse=True
        )[:top_n]

        return sorted_candidates
