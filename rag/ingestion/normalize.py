from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
from typing import Any, Optional


def normalize_title(title: str) -> str:
    """Create a conservative title key for cross-source duplicate detection."""
    value = re.sub(r"[^a-z0-9 ]+", " ", (title or "").lower())
    return re.sub(r"\s+", " ", value).strip()


def normalize_arxiv_id(value: str) -> tuple[str, int]:
    """Return canonical arXiv id and revision number (arXiv ids may include vN)."""
    raw = (value or "").strip().rstrip("/")
    raw = raw.rsplit("/", 1)[-1]
    match = re.match(r"^(?P<base>[^v]+?)(?:v(?P<version>\d+))?$", raw, re.I)
    if not match:
        return raw, 1
    return match.group("base"), int(match.group("version") or 1)


@dataclass(slots=True)
class CanonicalPaper:
    paper_id: str
    title: str
    abstract: Optional[str]
    published_at: datetime
    source: str
    external_id: str
    authors: list[dict[str, Any]] = field(default_factory=list)
    doi: Optional[str] = None
    primary_category: Optional[str] = None
    version: int = 1
    pdf_url: Optional[str] = None
    landing_url: Optional[str] = None
    citation_count: int = 0

    def __post_init__(self) -> None:
        if self.published_at.tzinfo is None:
            self.published_at = self.published_at.replace(tzinfo=timezone.utc)
        self.title = re.sub(r"\s+", " ", self.title or "").strip()
        self.abstract = re.sub(r"\s+", " ", self.abstract or "").strip() or None
