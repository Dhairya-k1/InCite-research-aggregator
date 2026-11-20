from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db
from backend.services.evidence_service import evidence_service
from rag.evaluation.runner import EvaluationCase, evaluate_retriever

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


class EvaluationRequest(BaseModel):
    cases: list[dict] = Field(..., min_length=1)
    k_values: list[int] = Field(default_factory=lambda: [1, 3, 5, 10])


@router.post("/lexical")
async def run_lexical_evaluation(request: EvaluationRequest, db: AsyncSession = Depends(get_db)):
    try:
        cases = [EvaluationCase(query=item["query"], relevant_chunk_ids=set(item["relevant_chunk_ids"]))
                 for item in request.cases]
        async_results = []
        for case in cases:
            async_results.append(await evidence_service.search(db, case.query, limit=max(request.k_values)))
        by_query = {case.query: result for case, result in zip(cases, async_results)}
        return evaluate_retriever(cases, lambda query: by_query[query], tuple(request.k_values))
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid evaluation dataset: {exc}") from exc
