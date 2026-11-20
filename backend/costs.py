from dataclasses import dataclass
from threading import Lock


@dataclass
class UsageEvent:
    provider: str
    operation: str
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float = 0.0


class CostTracker:
    def __init__(self):
        self._events: list[UsageEvent] = []
        self._lock = Lock()

    def record(self, event: UsageEvent):
        with self._lock:
            self._events.append(event)

    def snapshot(self):
        with self._lock:
            events = list(self._events)
        return {
            "events": len(events),
            "input_tokens": sum(e.input_tokens for e in events),
            "output_tokens": sum(e.output_tokens for e in events),
            "estimated_cost_usd": round(sum(e.estimated_cost_usd for e in events), 8),
            "by_operation": {
                operation: sum(e.estimated_cost_usd for e in events if e.operation == operation)
                for operation in sorted({e.operation for e in events})
            },
        }


cost_tracker = CostTracker()
