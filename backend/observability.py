import time
from collections import deque
from dataclasses import dataclass
from fastapi import Request


@dataclass
class RequestSample:
    path: str
    status: int
    duration_ms: float


class Metrics:
    def __init__(self, capacity: int = 1000):
        self.samples = deque(maxlen=capacity)

    def record(self, path: str, status: int, duration_ms: float):
        self.samples.append(RequestSample(path, status, duration_ms))

    def snapshot(self) -> dict:
        values = [sample.duration_ms for sample in self.samples]
        errors = sum(sample.status >= 500 for sample in self.samples)
        if not values:
            return {"requests": 0, "errors": 0, "p50_ms": 0, "p95_ms": 0}
        values.sort()
        percentile = lambda p: round(values[min(len(values) - 1, int(len(values) * p))], 2)
        return {"requests": len(values), "errors": errors, "p50_ms": percentile(0.50), "p95_ms": percentile(0.95)}


metrics = Metrics()


async def observe_request(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    metrics.record(request.url.path, response.status_code, (time.perf_counter() - started) * 1000)
    return response
