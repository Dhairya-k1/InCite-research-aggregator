import os
from typing import List
from google import genai
from google.genai import types

class GeminiEmbedder:
    """
    Handles vector generation using Google's Gemini API.
    Required environment variable: GEMINI_API_KEY
    """
    # Replaced deprecated text-embedding-004 with gemini-embedding-001
    EMBEDDING_DIMENSION = 768

    def __init__(self, model_name: str = 'gemini-embedding-001'):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")
        
        # Initialize the new SDK client
        self.client = genai.Client(api_key=api_key)
        
        self.model_name = model_name.replace("models/", "")

    def embed_document(self, text: str) -> List[float]:
        """Embeds text for storing in the vector database."""
        result = self.client.models.embed_content(
            model=self.model_name,
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                title="Research Paper Chunk",
                output_dimensionality=self.EMBEDDING_DIMENSION
            )
        )
        return result.embeddings[0].values

    def embed_query(self, query: str) -> List[float]:
        """Embeds the user's search query."""
        result = self.client.models.embed_content(
            model=self.model_name,
            contents=query,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
                output_dimensionality=self.EMBEDDING_DIMENSION
            )
        )
        return result.embeddings[0].values
    
    @property
    def dimension(self) -> int:
        return self.EMBEDDING_DIMENSION