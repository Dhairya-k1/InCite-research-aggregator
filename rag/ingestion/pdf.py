"""PDF extraction that preserves page boundaries for citation-quality evidence."""
from dataclasses import dataclass
import re
from pathlib import Path

import fitz


@dataclass(slots=True)
class ExtractedPage:
    page: int
    text: str


def extract_pdf(path: str | Path) -> list[ExtractedPage]:
    document = fitz.open(str(path))
    pages: list[ExtractedPage] = []
    try:
        for number, page in enumerate(document, start=1):
            text = page.get_text("text")
            text = re.sub(r"[ \t]+", " ", text)
            text = re.sub(r"\n{3,}", "\n\n", text).strip()
            if text:
                pages.append(ExtractedPage(page=number, text=text))
    finally:
        document.close()
    return pages


def join_pages(pages: list[ExtractedPage]) -> str:
    return "\n\n".join(page.text for page in pages)
