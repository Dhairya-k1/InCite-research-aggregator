"""Document processing orchestration used by workers and local experiments."""
from pathlib import Path
from rag.chunking.section_aware import SectionAwareChunker
from rag.ingestion.pdf import extract_pdf
from rag.models import Chunk, PaperMetadata


def process_pdf(path: str | Path, metadata: PaperMetadata, chunk_size: int = 1500) -> list[Chunk]:
    pages = extract_pdf(path)
    chunker = SectionAwareChunker(max_chunk_size=chunk_size)
    chunks = chunker.chunk("\n\n".join(page.text for page in pages), metadata)
    # Keep page citations deterministic by assigning the page containing the
    # first matching text. Section-aware chunks remain the primary metadata.
    for chunk in chunks:
        chunk.page = next((p.page for p in pages if chunk.text[:80].strip() in p.text), None)
    return chunks
