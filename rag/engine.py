import os
import json
from typing import Dict, Any

from google import genai
from google.genai import types

from rag.retrieval.hybrid import HybridRetriever
from rag.retrieval.reranker import Reranker
from rag.generation.prompts import build_rag_prompt
from rag.models import RAGResponse

class RAGEngine:
    """
    The main RAG orchestration engine.
    Combines hybrid retrieval, cross-encoder reranking, and Gemini structured generation.
    """
    def __init__(self, hybrid_retriever: HybridRetriever, reranker: Reranker):
        self.retriever = hybrid_retriever
        self.reranker = reranker
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")
        
        # Initialize the new SDK client
        self.client = genai.Client(api_key=api_key)
        
        # No 'models/' prefix for the new SDK
        self.model_name = 'gemini-3.8-flash'

    def answer_query(self, query: str, top_k_retrieval: int = 10, top_k_rerank: int = 4) -> Dict[str, Any]:
        """
        Executes the full RAG pipeline and returns a structured response.
        """
        retrieved_candidates = self.retriever.search(query, limit=top_k_retrieval)
        final_context = self.reranker.rerank(query, retrieved_candidates, top_n=top_k_rerank)
        prompt = build_rag_prompt(query, final_context)

        # Generate using the new types.GenerateContentConfig
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RAGResponse,
                temperature=0.2
            )
        )
        
        try:
            # Parse the strict JSON output returned by Gemini
            structured_output = json.loads(response.text)
            return structured_output
        except json.JSONDecodeError:
            return {
                "answer": "Failed to generate a properly formatted response.",
                "sources": []
            }