# InCite-research-aggregator

This module implements the **Retrieval-Augmented Generation (RAG)** and **retrieval evaluation pipeline** for the Research Discovery Platform.

The goal is not simply to build a chatbot. The system is designed to experimentally evaluate how different document processing and retrieval strategies affect **retrieval quality, answer grounding, and latency**.

---

## 1. Objectives

The RAG module will:

* Extract text from research-paper PDFs.
* Preserve paper, page, and section metadata.
* Implement multiple chunking strategies.
* Generate vector embeddings.
* Store and retrieve chunks using a vector database.
* Implement semantic retrieval.
* Implement hybrid retrieval.
* Add reranking.
* Generate grounded answers using an LLM.
* Provide evidence/citations for generated answers.
* Evaluate retrieval quality using labeled questions.
* Measure `Recall@K` and `nDCG@K`.
* Compare different retrieval strategies.
* Analyze retrieval failures.
* Measure retrieval latency.

---

## 2. RAG Pipeline

```text
                    Research Paper PDF
                           │
                           ▼
                  ┌─────────────────┐
                  │   PDF Parser    │
                  │    PyMuPDF      │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Text Cleaning   │
                  │ & Normalization │
                  └────────┬────────┘
                           │
                           ▼
             ┌────────────────────────────┐
             │        Chunking            │
             │                            │
             │ Fixed-size                 │
             │ Section-aware              │
             └─────────────┬──────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   Embeddings    │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │     Qdrant      │
                  │   Vector DB     │
                  └────────┬────────┘
                           │
                           ▼
                     User Query
                           │
                           ▼
             ┌────────────────────────────┐
             │      Retrieval             │
             │                            │
             │ Semantic + Keyword         │
             │        ↓                   │
             │ Hybrid Fusion              │
             │        ↓                   │
             │ Reranking                  │
             └─────────────┬──────────────┘
                           │
                           ▼
                   Relevant Chunks
                           │
                           ▼
                  ┌─────────────────┐
                  │      LLM        │
                  │     Gemini      │
                  └────────┬────────┘
                           │
                           ▼
                  Grounded Answer
                           │
                           ▼
                    Evidence/Citations
```

---

# 3. Project Structure

```text
rag/
│
├── data/
│   ├── papers/
│   └── evaluation/
│
├── ingestion/
│   └── pdf_parser.py
│
├── chunking/
│   ├── fixed_size.py
│   └── section_aware.py
│
├── embeddings/
│   └── embedder.py
│
├── retrieval/
│   ├── qdrant_store.py
│   ├── semantic.py
│   ├── hybrid.py
│   └── reranker.py
│
├── generation/
│   └── rag.py
│
├── evaluation/
│   ├── dataset.py
│   ├── metrics.py
│   └── evaluate.py
│
├── experiments/
│
├── config.py
├── requirements.txt
└── README.md
```

---

# 4. Technology Stack

| Component         | Technology                                |
| ----------------- | ----------------------------------------- |
| Language          | Python                                    |
| PDF processing    | PyMuPDF                                   |
| Embeddings        | Sentence Transformers / Gemini embeddings |
| Vector database   | Qdrant                                    |
| Keyword retrieval | MySQL Full-Text Search / BM25             |
| Reranking         | Cross-encoder / compatible reranker       |
| LLM               | Google Gemini API                         |
| Evaluation        | Python                                    |
| API integration   | FastAPI                                   |
| Containerization  | Docker                                    |

---

# 5. Development Strategy

The RAG system will be developed incrementally.

We will **not** immediately build the complete RAG pipeline.

Each stage must work before moving to the next stage.

```text
Stage 1
PDF → Text

Stage 2
Text → Fixed-size Chunks

Stage 3
Text → Section-aware Chunks

Stage 4
Chunks → Embeddings

Stage 5
Embeddings → Qdrant

Stage 6
Query → Semantic Retrieval

Stage 7
Semantic + Keyword → Hybrid Retrieval

Stage 8
Hybrid Retrieval → Reranking

Stage 9
Retrieved Context → Gemini → Answer

Stage 10
Evaluation Dataset → Retrieval Metrics

Stage 11
Compare Retrieval Strategies

Stage 12
Failure Analysis + Latency Measurement
```

---

# 6. Stage 1 — PDF Parsing

The first component extracts text while preserving page information.

File:

```text
ingestion/pdf_parser.py
```

Example:

```python
import fitz


def extract_text(pdf_path):
    """
    Extract text from a PDF while preserving page-level information.
    """

    doc = fitz.open(pdf_path)

    pages = []

    for page_number, page in enumerate(doc, start=1):

        text = page.get_text("text")

        if text.strip():
            pages.append({
                "page": page_number,
                "text": text.strip()
            })

    doc.close()

    return pages
```

Example output:

```python
[
    {
        "page": 1,
        "text": "Abstract ..."
    },
    {
        "page": 2,
        "text": "1 Introduction ..."
    }
]
```

Page metadata is retained because it will later be used for:

* citations
* evidence tracing
* debugging
* retrieval analysis

---

# 7. Chunking

Two primary chunking strategies will be evaluated.

## 7.1 Fixed-size Chunking

This will act as the baseline.

Example:

```text
Chunk size: 500 tokens
Overlap: 100 tokens
```

Pipeline:

```text
Document
   ↓
500-token chunk
   ↓
100-token overlap
   ↓
500-token chunk
   ↓
...
```

Purpose:

Establish a simple baseline against which more advanced strategies can be compared.

---

## 7.2 Section-aware Chunking

Research papers contain meaningful sections such as:

```text
Abstract
Introduction
Related Work
Methodology
Experiments
Results
Conclusion
```

Instead of blindly splitting the document, section-aware chunking attempts to preserve these boundaries.

Example chunk:

```json
{
    "text": "...",
    "paper_id": "paper_001",
    "section": "Methodology",
    "page": 5,
    "chunk_strategy": "section_aware"
}
```

This allows us to test whether preserving document structure improves retrieval.

---

# 8. Chunk Metadata

Every chunk should retain enough metadata to trace it back to the original paper.

Example:

```json
{
    "chunk_id": "paper001_chunk_017",
    "paper_id": "paper001",
    "text": "...",
    "page": 5,
    "section": "Methodology",
    "chunk_strategy": "section_aware"
}
```

Potential additional metadata:

```text
paper title
authors
arXiv ID
DOI
publication date
```

---

# 9. Embedding Pipeline

Chunks are converted into vector representations.

```text
Chunk
  ↓
Embedding Model
  ↓
Vector
  ↓
Qdrant
```

Each vector will be associated with its original chunk metadata.

Example:

```text
Vector
 ├── paper_id
 ├── chunk_id
 ├── page
 ├── section
 └── text
```

---

# 10. Vector Database

Qdrant will be used for vector search.

The database will contain:

```text
Embedding Vector
      +
Chunk Metadata
```

A query will be embedded using the same embedding model.

```text
User Question
      ↓
Query Embedding
      ↓
Qdrant
      ↓
Top-K Similar Chunks
```

---

# 11. Retrieval Pipeline

The retrieval system will progressively become more sophisticated.

### Experiment 1 — Semantic Retrieval

```text
Query
 ↓
Embedding
 ↓
Vector Search
 ↓
Top-K
```

### Experiment 2 — Hybrid Retrieval

```text
                  Query
                    │
          ┌─────────┴─────────┐
          ↓                   ↓
    Vector Search       Keyword Search
          │                   │
          └─────────┬─────────┘
                    ↓
               Score Fusion
                    ↓
                Top-K
```

### Experiment 3 — Hybrid + Reranking

```text
Query
 ↓
Hybrid Retrieval
 ↓
Top 20 candidates
 ↓
Reranker
 ↓
Top 5
```

This allows us to determine whether each additional component actually improves retrieval quality.

---

# 12. RAG Generation

The final generation pipeline will be:

```text
User Question
      ↓
Retriever
      ↓
Relevant Chunks
      ↓
Context Construction
      ↓
Gemini
      ↓
Grounded Answer
      ↓
Evidence / Citations
```

The model will be instructed to use only retrieved evidence.

Basic principle:

```text
If the answer is not supported by retrieved context,
the model should not invent an answer.
```

The answer should retain enough information to identify its supporting paper/section/page.

---

# 13. Evaluation Dataset

A labeled retrieval evaluation dataset will be created.

Example:

```json
{
    "question": "What dataset was used for evaluation?",
    "relevant_chunks": [
        "paper001_chunk_034",
        "paper001_chunk_035"
    ]
}
```

The dataset will contain questions whose relevant chunks are manually labeled.

Possible question types:

```text
Methodology
Dataset
Results
Architecture
Limitations
Contributions
Experimental setup
Metrics
```

---

# 14. Retrieval Metrics

## Recall@K

Measures whether relevant chunks were retrieved within the top K results.

```text
Recall@K =
relevant chunks retrieved
-------------------------
total relevant chunks
```

Example:

```text
Relevant chunks:
A, B

Retrieved Top-5:
A, C, D, E, F

Recall@5 = 1 / 2 = 0.5
```

---

# 15. nDCG@K

nDCG evaluates the ranking quality of retrieved results.

It rewards systems that place highly relevant chunks near the top of the ranking.

This is especially useful when comparing:

```text
Semantic retrieval
        vs
Hybrid retrieval
        vs
Hybrid + reranking
```

---

# 16. Planned Evaluation Experiments

The main experiment will compare:

| System       | Retrieval                          |
| ------------ | ---------------------------------- |
| Baseline     | Fixed-size + semantic              |
| Experiment 1 | Section-aware + semantic           |
| Experiment 2 | Section-aware + hybrid             |
| Experiment 3 | Section-aware + hybrid + reranking |

For every experiment we will measure:

```text
Recall@5
Recall@10
nDCG@5
nDCG@10
P50 latency
P95 latency
```

The actual values will be obtained from experiments and will not be manually assumed.

---

# 17. Retrieval Failure Analysis

When retrieval fails, the failure will be categorized.

Possible categories:

```text
1. PDF extraction failure
2. Missing information
3. Poor chunk boundary
4. Semantic retrieval failure
5. Keyword retrieval failure
6. Hybrid fusion failure
7. Reranker failure
8. Incorrect ground-truth label
```

Example:

```text
Question:
"What dataset was used?"

Expected chunk:
paper001_chunk_034

Retrieved:
paper001_chunk_012
paper001_chunk_018
paper001_chunk_022

Failure:
Semantic retrieval failure
```

This helps identify where the system actually needs improvement.

---

# 18. Latency Measurement

The system should measure latency at important stages.

```text
PDF fetching
PDF parsing
Chunking
Embedding
Indexing
Query embedding
Retrieval
Reranking
LLM generation
```

For retrieval requests, record:

```text
P50 latency
P95 latency
```

This will allow us to make engineering trade-offs instead of optimizing only for accuracy.

---

# 19. Final Evaluation Table

Yet to be made.

---

# 20. Current Progress

### Completed

* [x] RAG module architecture
* [x] Project directory structure
* [x] PDF parser design
* [x] Page-level metadata design
* [x] Fixed-size chunking
* [x] Section-aware chunking
* [x] Embeddings
* [x] Qdrant integration
* [x] Semantic retrieval
* [x] Hybrid retrieval
* [x] Reranking
* [x] RAG generation

### In Progress

* [ ] Evaluation dataset
* [ ] Recall@K
* [ ] nDCG@K
* [ ] Failure analysis
* [ ] Latency measurement

---

# 21. Engineering Principles

This project follows several principles:

### 1. Measure before optimizing

Do not claim that a technique is better without evaluating it.

### 2. Separate retrieval from generation

Retrieval quality must be measurable independently from LLM answer quality.

### 3. Preserve traceability

Every generated answer should be traceable back to:

```text
Answer
 ↓
Retrieved chunk
 ↓
Section
 ↓
Page
 ↓
Paper
```

### 4. Build baselines

Every advanced technique should have a simpler baseline for comparison.

### 5. Keep experiments reproducible

Record:

```text
model
chunk size
overlap
top-K
retrieval strategy
reranker
dataset version
evaluation results
latency
```

---

# 22. Immediate Next Steps

Build in this exact order:

```text
1. PDF parser
       ↓
2. Fixed-size chunker
       ↓
3. Section-aware chunker
       ↓
4. Embedding model
       ↓
5. Qdrant
       ↓
6. Semantic retrieval
       ↓
7. Evaluation dataset
       ↓
8. Recall@K + nDCG@K
       ↓
9. Hybrid retrieval
       ↓
10. Reranking
       ↓
11. Gemini RAG generation
       ↓
12. Final experiments
       ↓
13. Failure analysis
       ↓
14. Latency/cost analysis
```

The goal is to finish each stage with a working test before moving to the next one.
