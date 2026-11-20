from fastapi import APIRouter
from backend.api.papers import router as papers_router
from backend.api.search import router as search_router
from backend.api.chat import router as chat_router

api_router = APIRouter()

api_router.include_router(papers_router)
api_router.include_router(search_router)
api_router.include_router(chat_router)
