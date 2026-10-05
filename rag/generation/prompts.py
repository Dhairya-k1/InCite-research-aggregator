def build_rag_prompt(query: str, retrieved_chunks: list) -> str:
    """
    Constructs the prompt combining the user query and the retrieved context chunks.
    """
    context_text = ""
    for idx, chunk in enumerate(retrieved_chunks):
        payload = chunk.get('payload', {})
        paper_id = payload.get('paper_id', 'Unknown')
        section = payload.get('section', 'Unknown')
        text = payload.get('text', '')
        
        context_text += f"--- Context Chunk {idx + 1} ---\n"
        context_text += f"Paper ID: {paper_id}\n"
        context_text += f"Section: {section}\n"
        context_text += f"Text: {text}\n\n"

    prompt = f"""You are an expert AI research assistant. 
Answer the user's question based strictly on the provided Context Chunks.

INSTRUCTIONS:
1. Synthesize the context to provide a clear, accurate answer.
2. If the context does not contain the answer, state that you do not have enough information based on the current literature. Do NOT guess.
3. You must extract the `paper_id` and `section` for any chunk that directly supports your answer and include them in the `sources` array.

USER QUESTION: {query}

CONTEXT CHUNKS:
{context_text}
"""
    return prompt