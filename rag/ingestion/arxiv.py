import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Iterable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from rag.ingestion.normalize import CanonicalPaper, normalize_arxiv_id

NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


def fetch_arxiv(query: str, max_results: int = 10, timeout: int = 30) -> list[CanonicalPaper]:
    params = urlencode({"search_query": f"all:{query}", "start": 0, "max_results": max_results,
                        "sortBy": "submittedDate", "sortOrder": "descending"})
    request = Request(f"https://export.arxiv.org/api/query?{params}", headers={"User-Agent": "InCite/1.0"})
    with urlopen(request, timeout=timeout) as response:
        return parse_arxiv_feed(response.read())


def parse_arxiv_feed(payload: bytes | str) -> list[CanonicalPaper]:
    root = ET.fromstring(payload)
    papers: list[CanonicalPaper] = []
    for entry in root.findall("a:entry", NS):
        raw_id = entry.findtext("a:id", "", NS)
        base_id, version = normalize_arxiv_id(raw_id)
        authors = [{"name": a.findtext("a:name", "", NS).strip()} for a in entry.findall("a:author", NS)]
        categories = entry.findall("a:category", NS)
        pdf_url = next((l.attrib.get("href") for l in entry.findall("a:link", NS)
                        if l.attrib.get("title") == "pdf"), None)
        published = datetime.fromisoformat(entry.findtext("a:published", "", NS).replace("Z", "+00:00"))
        papers.append(CanonicalPaper(
            paper_id=f"arxiv:{base_id}", external_id=base_id, version=version,
            title=entry.findtext("a:title", "", NS), abstract=entry.findtext("a:summary", "", NS),
            published_at=published, source="arxiv", authors=authors,
            primary_category=categories[0].attrib.get("term") if categories else None,
            pdf_url=pdf_url, landing_url=raw_id,
        ))
    return papers
