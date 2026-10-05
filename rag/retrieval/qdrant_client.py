from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from typing import List, Dict, Any
from uuid import uuid5, NAMESPACE_URL
from rag.models import Chunk
from rag.embeddings.gemini import GeminiEmbedder

class VectorDatabase:
    """
    Manages the Qdrant vector store. 
    Configured for local storage during development.
    """
    def __init__(self, collection_name: str = "research_papers"):
        # Uses local storage path for development
        self.client = QdrantClient(path="./local_qdrant_storage")
        self.collection_name = collection_name
        self.embedder = GeminiEmbedder()
        self._ensure_collection()

    def _ensure_collection(self):
        """Creates the collection if it does not already exist."""
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection_name for c in collections):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedder.dimension, 
                    distance=Distance.COSINE
                )
            )
            # Note: Removed self.client.create_payload_index(...) to silence local UserWarnings.

    def ingest_chunks(self, chunks: List[Chunk]):
        """Embeds and uploads document chunks to Qdrant."""
        points = []
        
        # In a production worker, batching and async processing should be applied here.
        for chunk in chunks:
            vector = self.embedder.embed_document(chunk.text)
            
            # Convert Pydantic model to dict for the payload
            payload = chunk.model_dump()
            
            points.append(
                PointStruct(
                    # Qdrant accepts UUIDs or integers as point IDs. Keep the
                    # application chunk ID in the payload for result mapping.
                    id=str(uuid5(NAMESPACE_URL, f"{chunk.paper_id}:{chunk.chunk_id}")),
                    vector=vector,
                    payload=payload
                )
            )
            
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, query: str, limit: int = 5, strategy: str = None) -> List[Dict[str, Any]]: # type: ignore
        """
        Basic dense vector search. 
        Allows filtering by strategy (e.g., 'section-aware') for A/B testing.
        """
        query_vector = self.embedder.embed_query(query)
        
        query_filter = None
        if strategy:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="strategy",
                        match=MatchValue(value=strategy)
                    )
                ]
            )

        results = self.client.query_points( # type: ignore
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True
        ).points
        
        return [
            {"score": res.score, "payload": res.payload} 
            for res in results
        ]