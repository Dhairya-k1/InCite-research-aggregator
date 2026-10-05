import re
from typing import List
from rag.models import Chunk, PaperMetadata

class BaseChunker:
    def chunk(self, text: str, metadata: PaperMetadata) -> List[Chunk]:
        raise NotImplementedError

class FixedSizeChunker(BaseChunker):
    """
    Baseline fixed-size chunking strategy.
    Splits text by character count with a defined overlap.
    """
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str, metadata: PaperMetadata) -> List[Chunk]:
        chunks = []
        start = 0
        text_length = len(text)
        index = 0

        while start < text_length:
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            chunks.append(
                Chunk(
                    chunk_id=f"{metadata.paper_id}_fixed_{index}",
                    paper_id=metadata.paper_id,
                    text=chunk_text.strip(),
                    chunk_index=index,
                    strategy="fixed-size"
                )
            )
            start += (self.chunk_size - self.overlap)
            index += 1

        return chunks