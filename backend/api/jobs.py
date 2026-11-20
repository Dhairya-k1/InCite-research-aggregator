import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import AsyncSessionLocal, get_db
from backend.services.processing_service import processing_service

router = APIRouter(prefix="/jobs", tags=["Background Jobs"])
_jobs: dict[str, dict] = {}


async def _run_processing(job_id: str, paper_id: str):
    _jobs[job_id]["status"] = "running"
    _jobs[job_id]["started_at"] = datetime.now(timezone.utc).isoformat()
    try:
        async with AsyncSessionLocal() as db:
            _jobs[job_id]["result"] = await processing_service.process_paper(db, paper_id)
        _jobs[job_id]["status"] = "completed"
    except Exception as exc:
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["error"] = str(exc)
    _jobs[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat()


@router.post("/process/{paper_id}", status_code=202)
async def queue_processing(paper_id: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"job_id": job_id, "paper_id": paper_id, "status": "queued"}
    background_tasks.add_task(_run_processing, job_id, paper_id)
    return _jobs[job_id]


@router.get("/{job_id}")
async def get_job(job_id: str):
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return _jobs[job_id]
