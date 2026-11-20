from fastapi import APIRouter
from backend.observability import metrics

router = APIRouter(tags=["Operations"])


@router.get("/health")
async def health():
    return {"status": "ok", "service": "incite-api"}


@router.get("/metrics")
async def application_metrics():
    return metrics.snapshot()
