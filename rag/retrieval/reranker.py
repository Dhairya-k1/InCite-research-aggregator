from typing import List, Dict, Any
from sentence_transformers import CrossEncoder

class Reranker:
    """
    Rescores candidate chunks using a lightweight Cross-Encoder model.
    """
    def __init__(self, model_name: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2'):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Scores candidate query-passage pairs and sorts by score descending.
        """
        if not candidates:
            return []

        pairs = [[query, item['payload']['text']] for item in candidates]
        scores = self.model.predict(pairs)

        for idx, score in enumerate(scores):
            candidates[idx]['rerank_score'] = float(score)

        sorted_candidates = sorted(
            candidates, 
            key=lambda x: x['rerank_score'], 
            reverse=True
        )[:top_n]

        return sorted_candidates