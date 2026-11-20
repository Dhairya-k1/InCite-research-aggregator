"""Small synchronous worker entry point; can later be moved behind Celery/RQ."""
import logging
from pathlib import Path
from rag.models import PaperMetadata
from rag.processing import process_pdf

logger = logging.getLogger("research_platform.processing")


def build_chunks(pdf_path: str | Path, paper_id: str, title: str, source: str, version: int = 1):
    metadata = PaperMetadata(paper_id=paper_id, title=title, authors=[], source=source, version=version)
    chunks = process_pdf(pdf_path, metadata)
    logger.info("Processed %s into %d chunks", paper_id, len(chunks))
    return chunks
