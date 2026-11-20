from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db
from backend.services.evidence_service import evidence_service
from rag.evaluation.runner import EvaluationCase, evaluate_retriever

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


class ComparisonRequest(BaseModel):
    cases: list[dict] = Field(..., min_length=1)
    k: int = Field(5, ge=1, le=50)


@router.post("/compare-chunking")
async def compare_chunking(request: ComparisonRequest, db: AsyncSession = Depends(get_db)):
    try:
        cases = [EvaluationCase(item["query"], set(item["relevant_chunk_ids"])) for item in request.cases]
        outputs = {}
        for strategy in ("fixed-size", "section-aware"):
            retrieved = {}
            for case in cases:
                retrieved[case.query] = await evidence_service.search(db, case.query, request.k, strategy=strategy)
            report = evaluate_retriever(cases, lambda query, values=retrieved: values[query], (request.k,))
            failures = []
            for detail in report["details"]:
                if not set(detail["retrieved"]) & set(detail["relevant"]):
                    failures.append({"query": detail["query"], "category": "no_relevant_chunk_retrieved"})
                elif set(detail["retrieved"]) != set(detail["relevant"]) & set(detail["retrieved"]):
                    failures.append({"query": detail["query"], "category": "partial_recall"})
            report["failures"] = failures
            outputs[strategy] = report
        return {"experiment": "fixed-size-vs-section-aware", "results": outputs}
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid evaluation dataset: {exc}") from exc
