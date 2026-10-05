import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from backend.database.connection import init_db, AsyncSessionLocal
from backend.services.paper_service import paper_service
from backend.api.routes import api_router
from backend.api.papers import router as papers_router
from backend.api.search import router as search_router
from backend.api.chat import router as chat_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("research_platform")


async def seed_initial_data():
    """Seeds sample research papers on initial run."""
    async with AsyncSessionLocal() as db:
        existing = await paper_service.list_papers(db, page=1, limit=1)
        if existing.total == 0:
            logger.info("Seeding initial research papers...")
            await paper_service.upsert_paper(
                db=db,
                paper_id="arxiv:1706.03762",
                title="Attention Is All You Need",
                abstract=(
                    "The dominant sequence transduction models are based on complex recurrent or "
                    "convolutional neural networks. We propose the Transformer, a model architecture "
                    "eschewing recurrence and relying entirely on an attention mechanism."
                ),
                published_at=datetime(2017, 6, 12, tzinfo=timezone.utc),
                source="arxiv",
                authors_data=[
                    {"name": "Ashish Vaswani", "affiliation": "Google Brain"},
                    {"name": "Noam Shazeer", "affiliation": "Google Brain"},
                    {"name": "Niki Parmar", "affiliation": "Google Research"},
                    {"name": "Jakob Uszkoreit", "affiliation": "Google Research"}
                ],
                version=7,
                primary_category="cs.CL",
                doi="10.48550/arXiv.1706.03762"
            )

            await paper_service.upsert_paper(
                db=db,
                paper_id="arxiv:2205.14135",
                title="FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness",
                abstract=(
                    "Transformers are slow and memory-hungry on long sequences. We propose FlashAttention, "
                    "an IO-aware exact attention algorithm that uses tiling to reduce the number of memory "
                    "reads/writes between GPU high bandwidth memory (HBM) and GPU on-chip SRAM."
                ),
                published_at=datetime(2022, 5, 27, tzinfo=timezone.utc),
                source="arxiv",
                authors_data=[
                    {"name": "Tri Dao", "affiliation": "Stanford University"},
                    {"name": "Daniel Y. Fu", "affiliation": "Stanford University"},
                    {"name": "Christopher Ré", "affiliation": "Stanford University"}
                ],
                version=2,
                primary_category="cs.LG",
                doi="10.48550/arXiv.2205.14135"
            )
            logger.info("Seed data loaded successfully.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Backend...")
    await init_db()
    await seed_initial_data()
    yield
    logger.info("Shutting down Backend...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FastAPI Backend for Research Platform (Kapil's Part)",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoints:
# GET  /papers
# GET  /papers/{id}
# GET  /papers/latest
# GET  /papers/{id}/news
# POST /chat
# POST /search
app.include_router(papers_router)
app.include_router(search_router)
app.include_router(chat_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
