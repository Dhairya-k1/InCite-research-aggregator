import hashlib
import logging
import time
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import IngestionJob, Paper, PaperVersion
from backend.services.paper_service import paper_service
from rag.ingestion.normalize import CanonicalPaper, normalize_title

logger = logging.getLogger("research_platform.ingestion")


class IngestionService:
    async def ingest(self, db: AsyncSession, records: list[CanonicalPaper]) -> dict:
        started = time.perf_counter()
        created = updated = duplicates = failed = 0
        for record in records:
            job_key = hashlib.sha256(f"{record.source}:{record.external_id}:v{record.version}".encode()).hexdigest()
            job = IngestionJob(job_id=str(uuid.uuid4()), source_name=record.source,
                               external_id=record.external_id, idempotency_key=job_key,
                               status="running", started_at=datetime.now(timezone.utc))
            db.add(job)
            try:
                existing = (await db.execute(select(Paper).where(Paper.paper_id == record.paper_id))).scalars().first()
                if existing:
                    updated += 1
                else:
                    # Cross-source conservative duplicate check: exact normalized title only.
                    title_matches = (await db.execute(select(Paper).where(Paper.title == record.title))).scalars().all()
                    if any(normalize_title(p.title) == normalize_title(record.title) for p in title_matches):
                        duplicates += 1
                        job.status = "duplicate"
                        job.completed_at = datetime.now(timezone.utc)
                        continue
                    created += 1
                await paper_service.upsert_paper(db, record.paper_id, record.title, record.abstract,
                    record.published_at, record.source, record.authors, record.version, record.doi, record.primary_category)
                job.status = "completed"
                job.completed_at = datetime.now(timezone.utc)
            except Exception as exc:
                failed += 1
                job.status = "failed"
                job.error_log = str(exc)
                job.completed_at = datetime.now(timezone.utc)
                logger.exception("Failed to ingest %s", record.external_id)
        await db.commit()
        return {"received": len(records), "created": created, "updated": updated,
                "duplicates": duplicates, "failed": failed,
                "duration_ms": round((time.perf_counter() - started) * 1000, 2)}


ingestion_service = IngestionService()
