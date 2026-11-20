import hashlib
from pathlib import Path
from urllib.parse import quote

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import Paper, PaperVersion
from rag.ingestion.download import download_pdf
from rag.models import PaperMetadata
from rag.processing import persist_chunks, process_pdf


class ProcessingService:
    async def process_paper(self, db: AsyncSession, paper_id: str) -> dict:
        paper = (await db.execute(select(Paper).where(Paper.paper_id == paper_id))).scalars().first()
        if not paper:
            raise ValueError(f"Paper '{paper_id}' was not found")

        version = (await db.execute(select(PaperVersion).where(PaperVersion.paper_id == paper.id)
                                    .order_by(PaperVersion.version_number.desc()))).scalars().first()
        pdf_url = version.pdf_url if version and version.pdf_url else self._default_pdf_url(paper)
        safe_id = hashlib.sha256(paper.paper_id.encode()).hexdigest()[:20]
        path = Path("data/papers") / f"{safe_id}-v{paper.version}.pdf"
        if not path.exists():
            download_pdf(pdf_url, path)

        metadata = PaperMetadata(paper_id=paper.paper_id, title=paper.title, authors=[],
                                 source=paper.source, version=paper.version)
        chunks = process_pdf(path, metadata)
        saved = await persist_chunks(db, chunks)
        paper.storage_path = str(path)
        if version:
            version.storage_path = str(path)
        await db.commit()
        return {"paper_id": paper.paper_id, "pdf_url": pdf_url, "path": str(path),
                "chunks": len(chunks), "new_chunks": saved}

    @staticmethod
    def _default_pdf_url(paper: Paper) -> str:
        if paper.source.lower() == "arxiv":
            arxiv_id = paper.paper_id.split(":", 1)[-1]
            return f"https://arxiv.org/pdf/{quote(arxiv_id)}.pdf"
        raise ValueError("No PDF URL is available for this source")


processing_service = ProcessingService()
