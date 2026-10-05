from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
import re
from rag.models import Chunk

class KeywordSearchIndex:
    """
    BM25-based keyword retrieval index for exact term matching.
    """
    def __init__(self):
        self.bm25: BM25Okapi = None # type: ignore
        self.chunks: List[Chunk] = []

    def _tokenize(self, text: str) -> List[str]:
        """Simple lowercase word tokenization."""
        return re.findall(r'\w+', text.lower())

    def build_index(self, chunks: List[Chunk]):
        """Builds or rebuilds the BM25 index from a list of chunks."""
        self.chunks = chunks
        tokenized_corpus = [self._tokenize(chunk.text) for chunk in chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Performs lexical search and returns ranked chunk results."""
        if not self.bm25 or not self.chunks:
            return []

        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)

        # Get top-k indices sorted by score descending
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:limit]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Ignore zero-match chunks
                results.append({
                    "score": float(scores[idx]),
                    "payload": self.chunks[idx].model_dump()
                })
        return results