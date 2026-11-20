"""Paper-source adapters and canonical ingestion workflows."""

from rag.ingestion.normalize import CanonicalPaper, normalize_arxiv_id, normalize_title

__all__ = ["CanonicalPaper", "normalize_arxiv_id", "normalize_title"]
