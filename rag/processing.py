"""Document processing orchestration used by workers and local experiments."""
from pathlib import Path
from rag.chunking.section_aware import SectionAwareChunker
from rag.ingestion.pdf import extract_pdf
from rag.models import Chunk, PaperMetadata
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import DocumentChunk


def process_pdf(path: str | Path, metadata: PaperMetadata, chunk_size: int = 1500) -> list[Chunk]:
    pages = extract_pdf(path)
    chunker = SectionAwareChunker(max_chunk_size=chunk_size)
    chunks = chunker.chunk("\n\n".join(page.text for page in pages), metadata)
    # Keep page citations deterministic by assigning the page containing the
    # first matching text. Section-aware chunks remain the primary metadata.
    for chunk in chunks:
        chunk.page = next((p.page for p in pages if chunk.text[:80].strip() in p.text), None)
    return chunks


async def persist_chunks(db: AsyncSession, chunks: list[Chunk]) -> int:
    """Idempotently persist chunks so citations survive process restarts."""
    saved = 0
    for chunk in chunks:
        existing = (await db.execute(select(DocumentChunk).where(DocumentChunk.chunk_id == chunk.chunk_id))).scalars().first()
        values = dict(chunk_id=chunk.chunk_id, paper_id=chunk.paper_id, text=chunk.text,
                      chunk_index=chunk.chunk_index, section=chunk.section, page=chunk.page,
                      strategy=chunk.strategy)
        if existing:
            for key, value in values.items():
                setattr(existing, key, value)
        else:
            db.add(DocumentChunk(**values))
            saved += 1
    await db.commit()
    return saved
