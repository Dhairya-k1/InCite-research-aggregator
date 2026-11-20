from rag.retrieval.qdrant_client import VectorDatabase
from rag.retrieval.keyword_search import KeywordSearchIndex
from rag.retrieval.hybrid import HybridRetriever
from rag.retrieval.reranker import Reranker
from rag.engine import RAGEngine

def test_full_rag():
    # Initialize the retrieval stack (from Parts 2 & 3)
    vector_db = VectorDatabase()
    keyword_index = KeywordSearchIndex() 
    # (Assume chunks were previously ingested into these indexes)
    
    hybrid = HybridRetriever(vector_db, keyword_index)
    reranker = Reranker()
    
    # Initialize the RAG Orchestrator
    rag = RAGEngine(hybrid_retriever=hybrid, reranker=reranker)
    
    # Execute User Query
    user_query = "Why does the proposed method outperform the baseline?"
    result = rag.answer_query(user_query)
    
    # The output is directly consumable by the frontend
    print("--- RAG JSON API RESPONSE ---")
    import json
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_full_rag()