import uuid
import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import AsyncSessionLocal, get_db
from backend.database.models import ProcessingJob
from sqlalchemy import select
from backend.services.processing_service import processing_service

router = APIRouter(prefix="/jobs", tags=["Background Jobs"])
_jobs: dict[str, dict] = {}


async def _run_processing(job_id: str, paper_id: str):
    _jobs[job_id]["status"] = "running"
    _jobs[job_id]["started_at"] = datetime.now(timezone.utc).isoformat()
    try:
        async with AsyncSessionLocal() as db:
            job = (await db.execute(select(ProcessingJob).where(ProcessingJob.job_id == job_id))).scalars().first()
            if job:
                job.status = "running"
                job.started_at = datetime.now(timezone.utc)
                await db.commit()
            _jobs[job_id]["result"] = await processing_service.process_paper(db, paper_id)
            if job:
                job.status = "completed"
                job.result = _jobs[job_id]["result"]
                job.completed_at = datetime.now(timezone.utc)
                await db.commit()
        _jobs[job_id]["status"] = "completed"
    except Exception as exc:
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["error"] = str(exc)
        async with AsyncSessionLocal() as db:
            job = (await db.execute(select(ProcessingJob).where(ProcessingJob.job_id == job_id))).scalars().first()
            if job:
                job.status = "failed"
                job.error_log = str(exc)
                job.completed_at = datetime.now(timezone.utc)
                await db.commit()
    _jobs[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat()


@router.post("/process/{paper_id}", status_code=202)
async def queue_processing(paper_id: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    job_id = str(uuid.uuid4())
    idempotency_key = hashlib.sha256(f"pdf_processing:{paper_id}".encode()).hexdigest()
    existing = (await db.execute(select(ProcessingJob).where(ProcessingJob.idempotency_key == idempotency_key))).scalars().first()
    if existing and existing.status in {"queued", "running", "completed"}:
        return {"job_id": existing.job_id, "paper_id": paper_id, "status": existing.status,
                "result": existing.result}
    db.add(ProcessingJob(job_id=job_id, paper_id=paper_id, job_type="pdf_processing",
                         status="queued", idempotency_key=idempotency_key))
    await db.commit()
    _jobs[job_id] = {"job_id": job_id, "paper_id": paper_id, "status": "queued"}
    background_tasks.add_task(_run_processing, job_id, paper_id)
    return _jobs[job_id]


@router.get("/{job_id}")
async def get_job(job_id: str):
    async with AsyncSessionLocal() as db:
        job = (await db.execute(select(ProcessingJob).where(ProcessingJob.job_id == job_id))).scalars().first()
        if job:
            return {"job_id": job.job_id, "paper_id": job.paper_id, "status": job.status,
                    "result": job.result, "error": job.error_log,
                    "started_at": job.started_at, "completed_at": job.completed_at}
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return _jobs[job_id]
