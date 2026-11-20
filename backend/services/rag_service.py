from typing import Optional
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database.models import Paper
from backend.api.schemas import RAGResponse, RAGSource
from backend.services.evidence_service import evidence_service
from backend.services.retrieval_service import retrieval_service


class RAGService:
    """RAG Chat service providing grounded answers with citations."""

    async def chat(
        self,
        db: AsyncSession,
        query: str,
        paper_id: Optional[str] = None
    ) -> RAGResponse:
        retrieval = await retrieval_service.search(db, query, limit=6)
        evidence = retrieval["results"]
        if paper_id:
            evidence = [item for item in evidence if item.get("paper_id") == paper_id]
        if not evidence:
            return RAGResponse(
                answer="I could not find indexed evidence for this question. Ingest and process the relevant paper PDF first.",
                sources=[]
            )

        # Use Gemini when explicitly configured; otherwise provide a faithful
        # extractive answer so local development never fabricates citations.
        answer_text = self._extractive_answer(query, evidence)
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                from google import genai
                from google.genai import types
                client = genai.Client(api_key=api_key)
                context = "\n\n".join(
                    f"[{i + 1}] {item['text']} (paper={item['paper_id']}, section={item['section']}, page={item['page']})"
                    for i, item in enumerate(evidence)
                )
                prompt = (
                    "Answer the research question using only the evidence below. "
                    "If the evidence is insufficient, say so. Do not invent facts or citations.\n\n"
                    f"Question: {query}\n\nEvidence:\n{context}"
                )
                response = client.models.generate_content(
                    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"), contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.1)
                )
                if response.text:
                    answer_text = response.text.strip()
            except Exception:
                # Retrieval remains useful if an API quota/model is unavailable.
                pass

        sources = [RAGSource(paper_id=item["paper_id"], section=item["section"], page=item["page"])
                   for item in evidence]
        return RAGResponse(answer=answer_text, sources=sources)

    @staticmethod
    def _extractive_answer(query: str, evidence: list[dict]) -> str:
        snippets = []
        for item in evidence[:3]:
            text = item["text"].replace("\n", " ").strip()
            snippets.append(text[:500] + ("..." if len(text) > 500 else ""))
        return "Based on the indexed evidence: " + " ".join(snippets)


rag_service = RAGService()
