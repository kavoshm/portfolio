# Mental Health RAG System

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991?logo=openai&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.1+-green?logo=chainlink&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

A Retrieval-Augmented Generation system that enables clinical staff to query mental health
treatment protocols, therapy guidelines, and case management documentation using natural
language. Built on a RAG pipeline with domain-optimized chunking, metadata-rich retrieval,
and a FastAPI service layer -- designed for a clinical environment where wrong answers
are not just unhelpful, they are potentially harmful.

The system ingests clinical protocol documents (CBT manuals, DSM-5 criteria, treatment
guidelines, intake assessment rubrics) and provides grounded, citation-backed answers
to clinical queries, replacing the "search through a folder of PDFs" workflow that most
mental health practices still rely on.

---

## Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                    Mental Health RAG System                        │
│                                                                   │
│  INGESTION PIPELINE                                               │
│  ┌──────────┐   ┌──────────────┐   ┌────────────┐   ┌─────────┐ │
│  │ Clinical  │   │  Document    │   │  Semantic   │   │ ChromaDB│ │
│  │ Documents │──>│  Loader +    │──>│  Chunker    │──>│ Vector  │ │
│  │ (PDF,TXT) │   │  Metadata    │   │  (500 tok,  │   │ Store   │ │
│  └──────────┘   │  Extractor   │   │  100 overlap)│   └────┬────┘ │
│                  └──────────────┘   └────────────┘        │      │
│                                                            │      │
│  QUERY PIPELINE                                            │      │
│  ┌──────────┐   ┌──────────────┐   ┌────────────┐        │      │
│  │ Clinical  │   │  Query       │   │  Retriever  │<───────┘      │
│  │ Question  │──>│  Embedding   │──>│  (top-k=5,  │               │
│  └──────────┘   └──────────────┘   │  MMR)       │               │
│                                     └──────┬─────┘               │
│                                            │                      │
│                                            v                      │
│                  ┌──────────────────────────────────────────┐     │
│                  │  Generation (GPT-4)                       │     │
│                  │  - System prompt: clinical assistant role  │     │
│                  │  - Retrieved context with source metadata  │     │
│                  │  - Instruction: cite sources, flag gaps    │     │
│                  └──────────────┬───────────────────────────┘     │
│                                 │                                  │
│                                 v                                  │
│                  ┌──────────────────────────────────────────┐     │
│                  │  Response                                 │     │
│                  │  - Answer with inline citations            │     │
│                  │  - Source documents listed                 │     │
│                  │  - Confidence indicator                    │     │
│                  │  - "Not found in documents" when unknown   │     │
│                  └──────────────────────────────────────────┘     │
│                                                                   │
│  API LAYER (FastAPI)                                              │
│  ┌──────────┐   ┌──────────────┐   ┌────────────────────┐       │
│  │ POST     │   │ POST         │   │ GET                 │       │
│  │ /query   │   │ /ingest      │   │ /sources            │       │
│  └──────────┘   └──────────────┘   └────────────────────┘       │
└───────────────────────────────────────────────────────────────────┘
```

---

## Key Features

- **Domain-optimized chunking** -- 500-token chunks with 100-token overlap, tuned for clinical protocol documents where a single recommendation often spans multiple paragraphs
- **Metadata-rich retrieval** -- Every chunk carries source document, section heading, document type (guideline/protocol/assessment), and publication date for filtering and citation
- **MMR diversity** -- Maximal Marginal Relevance retrieval ensures returned chunks cover different aspects of a query rather than repeating the same information
- **Explicit uncertainty** -- When retrieved context does not contain the answer, the system says so rather than hallucinating. This is non-negotiable in clinical use.
- **Source citations** -- Every claim in the response links back to a specific document and section
- **FastAPI service layer** -- REST endpoints for query, document ingestion, and source browsing

---

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key

### Installation

```bash
git clone https://github.com/kavoshmonfared/mental-health-rag.git
cd mental-health-rag
pip install -r requirements.txt
cp .env.example .env  # Add your OPENAI_API_KEY
```

### Ingest Documents

```bash
# Ingest a directory of clinical protocol PDFs
python ingest.py --source data/protocols/ --collection mental_health_protocols
```

### Start the API Server

```bash
uvicorn api:app --reload --port 8000
```

### Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the first-line treatment recommendations for moderate depression in adults?"}'
```

---

## API Endpoints

### POST /query

Query the knowledge base with a clinical question.

**Request:**
```json
{
  "question": "What is the recommended PHQ-9 threshold for referral to psychiatry?",
  "filters": {
    "document_type": "guideline",
    "max_age_years": 3
  },
  "top_k": 5
}
```

**Response:**
```json
{
  "answer": "According to the APA Practice Guidelines (2022), a PHQ-9 score of 20 or above (severe depression) warrants referral to psychiatry for medication evaluation. Scores between 15-19 (moderately severe) should trigger a referral if the patient has not responded to first-line interventions within 6-8 weeks. [Source: APA Practice Guidelines, Section 4.2]",
  "sources": [
    {
      "document": "APA Practice Guidelines - Depression (2022)",
      "section": "4.2 Referral Criteria",
      "relevance_score": 0.94,
      "chunk_preview": "Patients scoring 20 or above on the PHQ-9 should be..."
    },
    {
      "document": "Clinic Intake Protocol v3.1",
      "section": "Severity-Based Routing",
      "relevance_score": 0.87,
      "chunk_preview": "Moderate-to-severe cases (PHQ-9 >= 15) that do not..."
    }
  ],
  "confidence": "high",
  "retrieval_metadata": {
    "chunks_retrieved": 5,
    "chunks_used": 2,
    "avg_relevance": 0.88
  }
}
```

### POST /ingest

Ingest new documents into the knowledge base.

**Request:**
```json
{
  "file_path": "/data/new_protocol.pdf",
  "metadata": {
    "document_type": "protocol",
    "author": "Clinical Team",
    "effective_date": "2024-01-15"
  }
}
```

**Response:**
```json
{
  "status": "ingested",
  "chunks_created": 47,
  "document_id": "doc_abc123"
}
```

### GET /sources

List all documents in the knowledge base.

**Response:**
```json
{
  "documents": [
    {
      "id": "doc_001",
      "title": "APA Practice Guidelines - Depression (2022)",
      "type": "guideline",
      "chunks": 83,
      "ingested_at": "2024-06-01T10:30:00Z"
    }
  ],
  "total_chunks": 412
}
```

---

## Project Structure

```
mental-health-rag/
├── src/
│   ├── __init__.py
│   ├── api.py                   # FastAPI application and endpoints
│   ├── ingest.py                # Document ingestion pipeline
│   ├── retriever.py             # Retrieval logic with MMR and filtering
│   ├── generator.py             # LLM generation with citation formatting
│   ├── chunker.py               # Clinical document chunking strategies
│   └── metadata_extractor.py    # Extract document metadata from PDFs
├── config/
│   ├── system_prompt.txt        # Clinical assistant system prompt
│   ├── chunking_config.yaml     # Chunk size, overlap, splitter settings
│   └── retrieval_config.yaml    # top-k, MMR lambda, score threshold
├── tests/
│   ├── test_retrieval.py        # Retrieval accuracy tests
│   ├── test_generation.py       # Generation quality tests
│   ├── test_api.py              # API endpoint tests
│   └── fixtures/
│       ├── sample_protocols/    # Synthetic clinical protocols
│       └── test_queries.json    # Query-answer pairs for evaluation
├── eval/
│   ├── retrieval_eval.py        # Retrieval quality metrics
│   ├── generation_eval.py       # Answer quality metrics
│   └── eval_results.json        # Latest evaluation results
├── data/
│   └── sample_protocols/        # Sample documents (no PHI)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Design Decisions

### Why ChromaDB Over Pinecone
**Context:** Needed a vector store for moderate-scale clinical document retrieval (~500 documents, ~10k chunks).
**Decision:** ChromaDB with local persistence.
**Rationale:** For a clinic-scale deployment, ChromaDB handles the volume easily without external service dependencies. Clinical data stays on-premises, which simplifies compliance. Pinecone would add cost and data-residency complexity for no performance benefit at this scale.
**Tradeoff:** Would need to migrate to a managed solution if scaling beyond ~100k chunks.

### Why 500-Token Chunks with 100-Token Overlap
**Context:** Clinical protocol documents have a specific structure -- recommendations often span 2-3 paragraphs with context building across sentences.
**Decision:** 500-token chunks (larger than the typical 200-300 default) with 100-token overlap.
**Rationale:** Tested chunk sizes of 200, 300, 500, and 800 tokens. At 200 tokens, clinical recommendations were frequently split across chunks, losing context. At 800, retrieval became noisy with too much irrelevant content per chunk. 500 tokens preserved most complete clinical recommendations while keeping retrieval focused. The 100-token overlap handles cases where a recommendation straddles a boundary.
**Tradeoff:** Fewer chunks mean slightly less granular retrieval. Acceptable given the document types.

### Why MMR Over Pure Similarity
**Context:** Clinical queries often touch multiple aspects of a topic ("What should I consider when treating depression in elderly patients?").
**Decision:** Maximal Marginal Relevance with lambda=0.7 for retrieval.
**Rationale:** Pure cosine similarity retrieval returned 5 chunks that often said the same thing. MMR with lambda=0.7 returns the most relevant chunk first, then balances relevance with diversity for remaining chunks. This consistently produced answers that covered medication considerations, contraindications, and monitoring -- rather than 5 variations of "SSRIs are first-line."
**Tradeoff:** Occasionally the 4th or 5th chunk is less relevant than it would be with pure similarity. Worth it for answer completeness.

---

## Evaluation Results

### Retrieval Quality

Evaluated on 30 clinical questions with expert-annotated relevant documents.

| Metric | Score | Notes |
|--------|-------|-------|
| Precision@5 | 0.78 | 78% of retrieved chunks were relevant |
| Recall@5 | 0.83 | 83% of relevant chunks appeared in top 5 |
| MRR | 0.91 | Most relevant chunk is usually ranked first |
| NDCG@5 | 0.85 | Ranking quality is strong |

### Answer Quality

Evaluated using LLM-as-judge (GPT-4) with clinical rubrics on 30 test queries.

| Metric | Score | Method |
|--------|-------|--------|
| Factual accuracy | 4.3/5.0 | Are claims supported by source documents? |
| Completeness | 3.9/5.0 | Does the answer cover all relevant aspects? |
| Citation accuracy | 4.5/5.0 | Do citations point to correct source material? |
| Safety | 4.8/5.0 | No harmful or misleading clinical information? |
| Appropriate uncertainty | 4.1/5.0 | Does it say "unknown" when context is insufficient? |

### Known Failure Modes

| Failure Mode | Frequency | Mitigation |
|-------------|-----------|------------|
| Incomplete answer when information spans >5 chunks | 4/30 queries | Increase top-k for complex queries |
| Outdated protocol cited when newer exists | 2/30 queries | Add date-based relevance boosting |
| Over-confident answer from partially relevant chunks | 2/30 queries | Tighten relevance score threshold |

### Latency and Cost

| Metric | Value |
|--------|-------|
| Retrieval latency (p50) | 45ms |
| End-to-end latency (p50) | 2.8s |
| End-to-end latency (p95) | 5.2s |
| Avg cost per query | ~$0.05 |

---

## Challenges & Solutions

### Challenge 1: Clinical Abbreviations Broke Chunking
**Problem:** Clinical documents use abbreviations heavily ("Pt should be assessed w/ PHQ-9 q2w for tx response"). Sentence-level splitters broke on periods in abbreviations like "Pt." and "q2w."
**Root Cause:** RecursiveCharacterTextSplitter treats periods as sentence boundaries.
**Solution:** Pre-processing step that normalizes common clinical abbreviations before chunking. Maintained an abbreviation dictionary of ~200 common clinical abbreviations.

### Challenge 2: Cross-Document Synthesis
**Problem:** Some questions required synthesizing information from multiple documents (e.g., a treatment guideline AND a clinic-specific protocol). The model would sometimes answer from only one source.
**Root Cause:** The generation prompt did not explicitly instruct synthesis across sources.
**Solution:** Modified the system prompt to include: "When retrieved context comes from multiple documents, synthesize information across all relevant sources. Note when sources agree or conflict." Improved completeness score from 3.4 to 3.9.

### Challenge 3: "Not Found" Calibration
**Problem:** The system was too aggressive in saying "information not found in documents" -- it would sometimes refuse to answer when relevant context was present but phrased differently from the query.
**Root Cause:** Relevance score threshold was set too high (0.85). Semantically relevant but differently-worded chunks fell below threshold.
**Solution:** Lowered threshold to 0.75 and added a secondary check: if any chunk scores >0.75, proceed with generation but note confidence level. Below 0.75 for all chunks triggers "not found."

---

## What I Learned

- **Retrieval quality is the ceiling for generation quality.** I spent weeks tuning prompts before realizing that the real problem was retrieval. When I switched focus to chunk size optimization and MMR tuning, answer quality improved more in two days than it had in two weeks of prompt engineering.
- **Metadata is not optional in clinical RAG.** Without document type and date metadata, the system could not distinguish between a current treatment guideline and an outdated protocol. In clinical use, citing an obsolete guideline is worse than saying "I don't know."
- **"I don't know" is a feature, not a failure.** In healthcare RAG, the system must refuse to answer when it does not have supporting evidence. Calibrating the threshold for "not found" was one of the hardest parts of the project -- too aggressive and the system is useless, too permissive and it halluccinates.
- **Embedding models matter more than I expected.** Switching from `text-embedding-ada-002` to a model better suited for clinical text improved retrieval precision by 8% on our test set. The general-purpose embedding model treated "depression" (clinical) and "depression" (economic) as highly similar.

---

## Future Improvements

- [ ] Implement sentence-window retrieval for more precise context
- [ ] Add auto-merging retrieval for documents with hierarchical structure
- [ ] Build a clinician feedback loop to improve retrieval based on usage
- [ ] Add document versioning to track when guidelines are updated
- [ ] Explore hybrid retrieval (sparse + dense) for handling clinical terminology

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Author

**Kavosh Monfared** -- Senior Software Engineer, AI Automation & Healthcare Systems
- GitHub: [@kavoshmonfared](https://github.com/kavoshmonfared)
- LinkedIn: [kavoshmonfared](https://linkedin.com/in/kavoshmonfared)
