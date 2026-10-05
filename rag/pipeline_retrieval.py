from rag.models import PaperMetadata, Chunk
from rag.retrieval.qdrant_client import VectorDatabase
from rag.retrieval.keyword_search import KeywordSearchIndex
from rag.retrieval.hybrid import HybridRetriever
from rag.retrieval.reranker import Reranker

def test_retrieval_pipeline():
    # 1. Initialize Vector Database & Keyword Index
    vector_db = VectorDatabase()
    keyword_index = KeywordSearchIndex()
    
    # Mock Chunks for demonstration
    metadata = PaperMetadata(
        paper_id="arxiv-2401-99999", 
        title="Attention Mechanics in Vision", 
        authors=["Alice"], 
        source="arxiv", 
        version=1
    )
    
    sample_chunks = [
        Chunk(
            chunk_id="chunk_0",
            paper_id=metadata.paper_id,
            text="We introduce multi-head cross-attention for image segmentation.",
            chunk_index=0,
            section="Methodology",
            strategy="section-aware"
        ),
        Chunk(
            chunk_id="chunk_1",
            paper_id=metadata.paper_id,
            text="Our network achieves 89.4% mIoU on the Pascal VOC benchmark using AdamW optimizer.",
            chunk_index=1,
            section="Results",
            strategy="section-aware"
        )
    ]

    # Index into vector store and keyword index
    vector_db.ingest_chunks(sample_chunks)
    keyword_index.build_index(sample_chunks)

    # 2. Hybrid Retrieval
    hybrid_retriever = HybridRetriever(vector_db, keyword_index)
    query = "What mIoU score was achieved on Pascal VOC?"
    
    hybrid_candidates = hybrid_retriever.search(query, limit=10)
    print(f"Hybrid candidates retrieved: {len(hybrid_candidates)}")

    # 3. Reranking
    reranker = Reranker()
    final_top_chunks = reranker.rerank(query, hybrid_candidates, top_n=1)
    
    print("\n--- Top Reranked Chunk ---")
    print(f"Section: {final_top_chunks[0]['payload']['section']}")
    print(f"Text: {final_top_chunks[0]['payload']['text']}")
    print(f"Rerank Score: {final_top_chunks[0]['rerank_score']:.4f}")

if __name__ == "__main__":
    test_retrieval_pipeline()