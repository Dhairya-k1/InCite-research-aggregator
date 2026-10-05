from typing import List, Dict
import re
from rag.models import Chunk, PaperMetadata
from rag.chunking.base import BaseChunker

class SectionAwareChunker(BaseChunker):
    """
    Splits research papers based on common academic headers.
    Assumes text has been somewhat normalized from PDF extraction.
    """
    def __init__(self, max_chunk_size: int = 1500, overlap: int = 200):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
        # Regex to catch common academic sections (e.g., "1. Introduction", "Abstract", "IV. Methodology")
        self.section_pattern = re.compile(
            r'^(?:[0-9]+\.?|[I|V|X]+\.?\s*)?(Abstract|Introduction|Related Work|Background|Methodology|Methods|Experiments|Results|Discussion|Conclusion|References)\b', 
            re.IGNORECASE | re.MULTILINE
        )

    def _split_long_section(self, section_text: str, section_name: str, base_index: int, metadata: PaperMetadata) -> List[Chunk]:
        """Falls back to overlapping chunks if a section is too large."""
        chunks = []
        words = section_text.split()
        
        # Approximating tokens/chars to avoid massive arrays; simple word batching for speed
        words_per_chunk = self.max_chunk_size // 5 # approx 5 chars per word
        word_overlap = self.overlap // 5
        
        start = 0
        sub_index = 0
        while start < len(words):
            end = start + words_per_chunk
            chunk_text = " ".join(words[start:end])
            
            chunks.append(Chunk(
                chunk_id=f"{metadata.paper_id}_sec_{base_index}_{sub_index}",
                paper_id=metadata.paper_id,
                text=chunk_text,
                chunk_index=base_index + sub_index,
                section=section_name,
                strategy="section-aware"
            ))
            start += (words_per_chunk - word_overlap)
            sub_index += 1
            
        return chunks

    def chunk(self, text: str, metadata: PaperMetadata) -> List[Chunk]:
        chunks = []
        # Find all section headers
        matches = list(self.section_pattern.finditer(text))
        
        if not matches:
            # Fallback if no sections found
            from rag.chunking.base import FixedSizeChunker
            return FixedSizeChunker(self.max_chunk_size, self.overlap).chunk(text, metadata)

        # Process sections
        for i, match in enumerate(matches):
            section_name = match.group(1).strip()
            start_idx = match.end()
            end_idx = matches[i+1].start() if i + 1 < len(matches) else len(text)
            
            section_text = text[start_idx:end_idx].strip()
            if not section_text:
                continue
                
            if len(section_text) > self.max_chunk_size:
                sub_chunks = self._split_long_section(section_text, section_name, i * 100, metadata)
                chunks.extend(sub_chunks)
            else:
                chunks.append(Chunk(
                    chunk_id=f"{metadata.paper_id}_sec_{i}",
                    paper_id=metadata.paper_id,
                    text=section_text,
                    chunk_index=i,
                    section=section_name,
                    strategy="section-aware"
                ))
                
        return chunks