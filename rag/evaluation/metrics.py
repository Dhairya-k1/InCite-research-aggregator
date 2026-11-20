from math import log2


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    return len(set(retrieved[:k]) & relevant) / len(relevant)


def ndcg_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    dcg = sum(1 / log2(index + 2) for index, item in enumerate(retrieved[:k]) if item in relevant)
    ideal_count = min(len(relevant), k)
    idcg = sum(1 / log2(index + 2) for index in range(ideal_count))
    return dcg / idcg if idcg else 0.0


def evaluate_case(retrieved: list[str], relevant: set[str], k_values=(1, 3, 5, 10)) -> dict:
    return {f"recall@{k}": round(recall_at_k(retrieved, relevant, k), 4) for k in k_values} | {
        f"ndcg@{k}": round(ndcg_at_k(retrieved, relevant, k), 4) for k in k_values
    }
