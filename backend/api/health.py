from fastapi import APIRouter
from backend.observability import metrics
from backend.costs import cost_tracker

router = APIRouter(tags=["Operations"])


@router.get("/health")
async def health():
    return {"status": "ok", "service": "incite-api"}


@router.get("/metrics")
async def application_metrics():
    return {**metrics.snapshot(), "usage": cost_tracker.snapshot()}


@router.get("/costs")
async def application_costs():
    return cost_tracker.snapshot()
