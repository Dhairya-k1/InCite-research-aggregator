from dataclasses import dataclass
from statistics import mean

from rag.evaluation.metrics import evaluate_case


@dataclass(slots=True)
class EvaluationCase:
    query: str
    relevant_chunk_ids: set[str]


def evaluate_retriever(cases: list[EvaluationCase], retrieve, k_values=(1, 3, 5, 10)) -> dict:
    """Run a labeled benchmark without inventing scores or hiding failures."""
    rows = []
    for case in cases:
        results = retrieve(case.query)
        ids = [item.get("chunk_id") or item.get("payload", {}).get("chunk_id") for item in results]
        ids = [item_id for item_id in ids if item_id]
        rows.append({"query": case.query, "relevant": sorted(case.relevant_chunk_ids),
                     "retrieved": ids, "metrics": evaluate_case(ids, case.relevant_chunk_ids, k_values)})
    summary = {}
    for metric in (f"recall@{k}" for k in k_values):
        summary[metric] = round(mean(row["metrics"][metric] for row in rows), 4) if rows else 0.0
    for metric in (f"ndcg@{k}" for k in k_values):
        summary[metric] = round(mean(row["metrics"][metric] for row in rows), 4) if rows else 0.0
    return {"cases": len(rows), "summary": summary, "details": rows}
