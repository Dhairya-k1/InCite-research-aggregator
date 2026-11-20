import json
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from rag.ingestion.normalize import CanonicalPaper


def _abstract(inverted: dict | None) -> str | None:
    if not inverted:
        return None
    words: list[str] = []
    for word, positions in inverted.items():
        for position in positions:
            if position >= len(words):
                words.extend([""] * (position - len(words) + 1))
            words[position] = word
    return " ".join(words).strip() or None


def fetch_openalex(query: str, per_page: int = 10, timeout: int = 30) -> list[CanonicalPaper]:
    params = urlencode({"search": query, "per-page": per_page, "mailto": "incite@example.com"})
    request = Request(f"https://api.openalex.org/works?{params}", headers={"User-Agent": "InCite/1.0"})
    with urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read())
    return [parse_openalex_work(work) for work in data.get("results", [])]


def parse_openalex_work(work: dict) -> CanonicalPaper:
    external_id = work.get("id", "").rsplit("/", 1)[-1]
    date = work.get("publication_date") or "1970-01-01"
    authors = [{"name": (a.get("author") or {}).get("display_name", ""),
                "author_id": (a.get("author") or {}).get("id", "").rsplit("/", 1)[-1]}
               for a in work.get("authorships", [])]
    return CanonicalPaper(
        paper_id=f"openalex:{external_id}", external_id=external_id,
        title=work.get("title") or "Untitled", abstract=_abstract(work.get("abstract_inverted_index")),
        published_at=datetime.fromisoformat(date).replace(tzinfo=timezone.utc), source="openalex",
        authors=authors, doi=work.get("doi"), citation_count=work.get("cited_by_count", 0),
        primary_category=((work.get("primary_topic") or {}).get("field") or {}).get("display_name"),
        landing_url=work.get("doi") or work.get("id"),
    )
