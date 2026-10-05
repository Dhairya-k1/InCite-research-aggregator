from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db
from backend.services.rag_service import rag_service
from backend.api.schemas import ChatRequest, RAGResponse

router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=RAGResponse, status_code=status.HTTP_200_OK, summary="Grounded Research RAG Chatbot")
async def chat_with_paper(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    RAG chat endpoint answering user research questions with grounded citations.
    Adheres strictly to team RAG Contract:
    {
       "answer": "...",
       "sources": [{"paper_id": "...", "section": "Methodology", "page": 5}]
    }
    """
    return await rag_service.chat(
        db=db,
        query=req.query,
        paper_id=req.paper_id
    )
