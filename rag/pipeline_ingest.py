from rag.models import PaperMetadata
from rag.chunking.section_aware import SectionAwareChunker
from rag.retrieval.qdrant_client import VectorDatabase

def run_ingestion_test():
    # 1. Mock metadata (Kapil's schema equivalent)
    metadata = PaperMetadata(
        paper_id="arxiv-2401-12345",
        title="Efficient Transformer Inference",
        authors=["John Doe"],
        source="arxiv",
        version=1
    )
    
    # 2. Mock extracted text (simulate PDF extraction output)
    sample_text = """
    Abstract. We present a novel method for transformer inference.
    1. Introduction. Transformers are computationally expensive.
    IV. Methodology. We quantize the attention weights using an 8-bit schema.
    """
    
    # 3. Process into chunks (Part 1)
    chunker = SectionAwareChunker()
    chunks = chunker.chunk(sample_text, metadata)
    
    print(f"Generated {len(chunks)} chunks.")
    
    # 4. Ingest into Qdrant (Part 2)
    vector_db = VectorDatabase()
    vector_db.ingest_chunks(chunks)
    print("Ingestion complete.")

if __name__ == "__main__":
    run_ingestion_test()