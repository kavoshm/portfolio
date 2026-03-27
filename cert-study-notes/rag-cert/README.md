# 6-3: Advanced RAG Certificate

## Certificate Details

**Course:** Building and Evaluating Advanced RAG Applications
**Provider:** DeepLearning.AI (Coursera)
**Completed:** 2024
**Instructors:** Jerry Liu (LlamaIndex) & Anyscale team

## What This Certificate Covers

This course goes beyond basic RAG (retrieve top-k chunks, stuff into prompt) into
advanced retrieval strategies that significantly improve answer quality for complex
queries. It also introduces the RAG evaluation triad -- a framework for systematically
measuring retrieval and generation quality.

For healthcare RAG systems, these techniques are particularly valuable: clinical queries
often require synthesizing information across document hierarchies (a treatment guideline
with sections and subsections), and retrieval errors have downstream consequences for
clinical decision-making.

## Key Skills Demonstrated

- **Sentence-Window Retrieval** -- Embedding individual sentences for precise retrieval,
  then expanding the context window to surrounding sentences for the LLM. Balances
  retrieval precision with generation context.
- **Auto-Merging Retrieval** -- Hierarchical chunking where retrieving enough child chunks
  automatically promotes the parent chunk. Captures document structure in retrieval.
- **RAG Evaluation Triad** -- Systematic evaluation of context relevance, groundedness,
  and answer relevance. Three independent metrics that pinpoint where a RAG pipeline fails.
- **Advanced Chunking Strategies** -- Moving beyond fixed-size chunks to semantic, hierarchical,
  and document-structure-aware chunking.
- **Reranking Approaches** -- Using cross-encoder models and LLM-based reranking to improve
  retrieval precision after initial embedding-based retrieval.

## How This Applies to My Work

At AIMedic, these techniques directly improved the mental health RAG system:
- Sentence-window retrieval improved precision on specific clinical questions by 12%
- Hierarchical chunking better captured the structure of treatment protocol documents
- The RAG evaluation triad provided a clear debugging framework: when answers were wrong,
  I could determine whether the problem was retrieval, grounding, or generation
- Reranking reduced noise in retrieval results for ambiguous clinical queries

## Files in This Module

| File | Description |
|------|-------------|
| `study_notes.md` | Comprehensive notes on advanced RAG techniques |
| `practice_questions.md` | 15 practice questions with detailed answers |

## Connection to Other Phases

This certificate provides the retrieval foundation for:
- **Phase 2 (RAG Pipelines):** Advanced techniques built on the basic RAG pipeline
- **Phase 3 (Evaluation):** The RAG triad is a specialized evaluation framework
- **Phase 6 (Portfolio):** The Mental Health RAG README (Project 2) showcases these skills
