# Advanced RAG Certificate -- Comprehensive Study Notes

## 1. Sentence-Window Retrieval

### The Problem with Standard Chunking

Standard RAG chunks documents into fixed-size segments (e.g., 500 tokens) and embeds each
chunk. The retrieval model finds the most similar chunks to the query and passes them to
the LLM. This creates a fundamental tension:

- **Small chunks** improve retrieval precision (the embedding is focused on a specific
  concept) but lose context (the LLM does not have enough surrounding information to
  generate a good answer).
- **Large chunks** provide better context for the LLM but hurt retrieval precision
  (the embedding is diluted across multiple concepts, and irrelevant content pollutes
  the similarity score).

### How Sentence-Window Retrieval Works

Sentence-window retrieval decouples the retrieval unit from the context unit:

1. **Index sentences individually.** Each sentence gets its own embedding. This gives maximum
   retrieval precision -- a query about "PHQ-9 referral threshold" matches the exact sentence
   that discusses this, not a 500-token chunk that mentions it somewhere in the middle.

2. **On retrieval, expand the window.** When a sentence is retrieved, replace it with a
   window of surrounding sentences (e.g., 3 sentences before and 3 after). This gives the
   LLM the context it needs to generate a complete answer.

```
Document:
    ... sentence N-3 ...
    ... sentence N-2 ...
    ... sentence N-1 ...
    >>> sentence N <<<     <-- This sentence matched the query (embedded individually)
    ... sentence N+1 ...
    ... sentence N+2 ...
    ... sentence N+3 ...

Retrieval returns sentence N.
Context sent to LLM: sentences N-3 through N+3 (the "window").
```

### Implementation Details

- **Sentence splitting:** Use a sentence tokenizer (spaCy or NLTK) rather than regex.
  Clinical text has abbreviations ("Pt.", "q.d.") that confuse regex-based splitters.
- **Window size:** Configurable. 3 sentences on each side is a good starting point. For
  clinical protocols where recommendations span multiple paragraphs, consider 5-7.
- **Overlap handling:** When two retrieved sentences are close together, their windows
  overlap. Merge overlapping windows to avoid sending duplicate context to the LLM.
- **Metadata propagation:** Each sentence inherits its parent document's metadata (source,
  section, date). The expanded window retains this metadata for citation.

### When to Use Sentence-Window Retrieval

- Queries that target specific facts (e.g., "What is the recommended dosage of sertraline
  for adolescents?")
- Documents with dense, factual content (clinical guidelines, drug references)
- When retrieval precision is more important than coverage

### When NOT to Use It

- Queries that require synthesizing broad themes (e.g., "What is the overall approach to
  treating treatment-resistant depression?")
- Very short documents where chunking is unnecessary
- When the document has no natural sentence structure (tables, structured data)

---

## 2. Auto-Merging Retrieval

### The Problem with Flat Chunking

Clinical documents often have hierarchical structure:

```
Treatment Guideline
├── Section 1: Assessment
│   ├── 1.1 Initial Screening
│   ├── 1.2 Diagnostic Criteria
│   └── 1.3 Severity Rating
├── Section 2: Treatment
│   ├── 2.1 First-Line Treatment
│   ├── 2.2 Augmentation Strategies
│   └── 2.3 Treatment-Resistant Cases
└── Section 3: Monitoring
    ├── 3.1 Follow-Up Schedule
    └── 3.2 Outcome Measures
```

Flat chunking loses this structure. A chunk from "2.1 First-Line Treatment" does not know
that it belongs to "Section 2: Treatment" or that "2.2 Augmentation Strategies" is the
next logical step if first-line treatment fails.

### How Auto-Merging Works

Auto-merging retrieval uses hierarchical chunking with automatic promotion:

1. **Create a chunk hierarchy.** Split the document at multiple levels:
   - Level 0 (leaf): Small chunks (~128 tokens) for precise retrieval
   - Level 1 (parent): Medium chunks (~512 tokens) containing multiple leaves
   - Level 2 (grandparent): Large chunks (~2048 tokens) containing multiple parents

2. **Embed and index the leaf nodes.** Retrieval operates on the smallest chunks for
   precision.

3. **Auto-merge on retrieval.** If enough leaf chunks from the same parent are retrieved,
   promote to the parent chunk instead. For example, if a query retrieves 3 out of 4 leaf
   chunks from the same parent, return the parent chunk (which includes the context that
   connects the leaves).

```
Parent chunk (512 tokens):
├── Leaf A (128 tokens)  <-- Retrieved
├── Leaf B (128 tokens)  <-- Retrieved
├── Leaf C (128 tokens)  <-- Retrieved
└── Leaf D (128 tokens)

3/4 leaves retrieved → auto-merge to parent chunk.
LLM receives the full parent (512 tokens) instead of 3 disconnected leaves.
```

### Configuration

- **Merge threshold:** What fraction of child chunks must be retrieved to trigger merge?
  Common values: 0.5 (half), 0.75 (three-quarters). Lower thresholds merge more
  aggressively, providing more context but potentially more noise.
- **Hierarchy depth:** 2-3 levels is typical. More levels add complexity without clear
  benefit for most documents.
- **Chunk sizes per level:** Leaf: 128-256 tokens, Parent: 512-1024 tokens,
  Grandparent: 2048+ tokens.

### When to Use Auto-Merging

- Documents with natural hierarchical structure (clinical guidelines, textbooks, protocols)
- Queries that need context from multiple related subsections
- When the relationship between chunks matters (e.g., first-line treatment and its
  contraindications are in adjacent subsections)

### Clinical Application

For a treatment guideline query like "How should treatment-resistant depression be managed?",
auto-merging might:
1. Retrieve leaf chunks from "2.3 Treatment-Resistant Cases" (direct match)
2. Also retrieve leaves from "2.1 First-Line Treatment" and "2.2 Augmentation Strategies"
   (related context)
3. Auto-merge 2.1, 2.2, and 2.3 into the full "Section 2: Treatment" parent
4. The LLM receives the complete treatment section, enabling a comprehensive answer that
   covers the full treatment progression

---

## 3. RAG Evaluation Triad

### The Three Metrics

The RAG evaluation triad provides three independent metrics that together diagnose where
a RAG pipeline fails:

```
     Query
      │
      ├──────────────────────────────────────┐
      │                                      │
      v                                      v
  Retrieved Context                      Generated Answer
      │                                      │
      │    (1) Context Relevance             │    (3) Answer Relevance
      │    Is the retrieved context          │    Does the answer address
      │    relevant to the query?            │    the query?
      │                                      │
      └──────────────┬──────────────────────┘
                     │
                     │    (2) Groundedness
                     │    Is the answer supported by
                     │    the retrieved context?
                     │    (No hallucination)
```

### Metric 1: Context Relevance

**Question:** Is the retrieved context relevant to the query?

**What it measures:** Retrieval quality. If the retrieved chunks are not relevant, the LLM
cannot generate a good answer regardless of its capabilities.

**How to measure:**
- LLM-as-judge: "Given the query [Q], rate the relevance of this context [C] on a 1-5 scale."
- Precision@k: What fraction of the top-k retrieved chunks are relevant?
- Sentence-level relevance: What fraction of sentences in the retrieved context are relevant?

**When this metric is low:**
The problem is in retrieval. Check:
- Embedding model quality (is it capturing clinical terminology?)
- Chunk size (too large? too small?)
- Retrieval strategy (similarity only? need MMR for diversity?)
- Query preprocessing (does the query need reformulation?)

### Metric 2: Groundedness

**Question:** Is the generated answer supported by the retrieved context?

**What it measures:** Hallucination. The LLM might generate text that sounds correct but is
not present in the retrieved context. In healthcare, this is the most dangerous failure mode.

**How to measure:**
- Claim extraction: Break the answer into individual claims. For each claim, check if the
  retrieved context supports it.
- LLM-as-judge: "Given this context [C], is this answer [A] fully supported by the context?"
- NLI (Natural Language Inference): For each answer sentence, classify as "entailed,"
  "contradicted," or "neutral" with respect to the context.

**When this metric is low:**
The problem is in generation. Check:
- Is the LLM ignoring the context and relying on training data?
- Is the prompt clearly instructing the LLM to only use provided context?
- Are there context conflicts (multiple chunks with contradictory information)?
- Is the context insufficient for the query (forcing the LLM to fill gaps)?

### Metric 3: Answer Relevance

**Question:** Does the generated answer address the query?

**What it measures:** Answer quality from the user's perspective. The answer might be
grounded and accurate but not actually answer the question asked.

**How to measure:**
- LLM-as-judge: "Does this answer [A] address the query [Q]? Rate on a 1-5 scale."
- Query-answer similarity: Embed both the query and the answer, measure cosine similarity.
- Hypothetical question generation: From the answer, generate questions it would answer.
  How similar are those questions to the original query?

**When this metric is low:**
The answer is tangential or off-topic. Check:
- Are the retrieved chunks relevant but not specific enough?
- Is the LLM generating a general answer instead of a specific one?
- Is the prompt directing the LLM to synthesize a focused answer?

### Debugging with the Triad

The power of the triad is diagnostic:

| Context Relevance | Groundedness | Answer Relevance | Diagnosis |
|-------------------|-------------|------------------|-----------|
| High | High | High | Pipeline is working well |
| Low | Any | Any | Retrieval problem: fix embeddings, chunking, or query |
| High | Low | Any | Hallucination: fix generation prompt or add guardrails |
| High | High | Low | Answer is grounded but off-topic: fix prompt or retrieval filtering |
| Low | High | High | Lucky coincidence: model used training data, not context |

---

## 4. Advanced Chunking Strategies

### Fixed-Size Chunking (Baseline)

Split text into fixed-size segments (e.g., 500 tokens) with overlap (e.g., 100 tokens).
Simple and universal but ignores document structure.

**Best for:** Unstructured text with no clear section boundaries (free-text clinical notes,
therapy transcripts).

### Semantic Chunking

Group text by semantic similarity rather than fixed size. Adjacent sentences that are
semantically similar stay together; a shift in topic triggers a new chunk.

**Method:**
1. Embed each sentence
2. Compute cosine similarity between adjacent sentences
3. Split where similarity drops below a threshold

**Best for:** Documents where topics change without explicit section headers. Clinical notes
that jump between complaints, history, and assessment without clear formatting.

**Advantage:** Chunks are semantically coherent -- each chunk discusses one topic.
**Disadvantage:** Chunk sizes vary widely. Some chunks may be very short (2 sentences) or
very long (20 sentences). This affects retrieval performance.

### Document-Structure-Aware Chunking

Use the document's own structure (headings, sections, subsections) as chunk boundaries.

**Method:**
1. Parse document structure (Markdown headings, PDF outlines, HTML tags)
2. Split at section boundaries
3. If a section exceeds the target size, apply recursive splitting within it

**Best for:** Structured documents with clear section hierarchy (clinical guidelines,
treatment protocols, formularies).

**Advantage:** Chunks respect document structure. A "Drug Interactions" section stays as one
chunk rather than being split arbitrarily.
**Disadvantage:** Requires documents with parseable structure. Raw clinical notes often
have inconsistent formatting.

### Proposition-Based Chunking

Break text into atomic propositions (individual facts or claims), then group related
propositions into chunks.

**Method:**
1. Use an LLM to extract atomic propositions from the text
2. Group related propositions by topic
3. Each group becomes a chunk

**Best for:** Dense factual content where individual facts need to be retrievable
(drug reference databases, diagnostic criteria lists).

**Advantage:** Maximum retrieval precision -- each proposition is an independent, retrievable
fact.
**Disadvantage:** Expensive (requires LLM call for proposition extraction). Loses narrative
context between propositions.

### Choosing a Chunking Strategy for Clinical Documents

| Document Type | Recommended Strategy | Why |
|--------------|---------------------|-----|
| Treatment guidelines | Document-structure + auto-merging | Hierarchical structure maps to retrieval hierarchy |
| Clinical notes | Semantic chunking | No consistent structure; semantic boundaries are the best available |
| Drug references | Proposition-based | Dense factual content; individual drug-fact retrieval |
| Therapy transcripts | Fixed-size with overlap | Long, conversational text with gradual topic shifts |
| Discharge summaries | Document-structure (SOAP sections) | Standard structure (Subjective, Objective, Assessment, Plan) |

---

## 5. Reranking Approaches

### Why Reranking Matters

Embedding-based retrieval (bi-encoder) is fast but imprecise. It embeds the query and
documents independently, then computes similarity. This misses nuances: "depression
treatment in elderly patients" matches documents about "depression" and about "elderly
patients" but may not prioritize documents specifically about treating depression in the
elderly.

Reranking adds a second, more precise pass after initial retrieval.

### Cross-Encoder Reranking

A cross-encoder takes the query and a document as a pair and outputs a relevance score.
Unlike bi-encoders (which embed query and document independently), cross-encoders attend to
both simultaneously, capturing fine-grained relevance.

**Pipeline:**
1. Bi-encoder retrieval: top-50 candidates (fast, approximate)
2. Cross-encoder reranking: re-score top-50, return top-5 (slow, precise)

**Models:** `cross-encoder/ms-marco-MiniLM-L-6-v2` is a common choice. For clinical text,
models fine-tuned on biomedical text (e.g., PubMedBERT-based cross-encoders) perform better.

**Advantage:** Significantly improves precision. In my testing, cross-encoder reranking
improved Precision@5 by 10-15% on clinical queries.
**Disadvantage:** Slower (~100ms for 50 candidates). Cost is compute, not API calls.

### LLM-Based Reranking

Use an LLM to score or rank retrieved documents.

**Method 1 -- Pointwise scoring:**
"On a scale of 1-10, how relevant is this document to the query [Q]?"

**Method 2 -- Listwise ranking:**
"Given query [Q], rank these documents from most to least relevant: [D1, D2, D3, ...]"

**Method 3 -- Pairwise comparison:**
"Given query [Q], which document is more relevant: [D1] or [D2]?"

**Advantage:** Most precise reranking. The LLM understands the query semantics deeply.
**Disadvantage:** Expensive (LLM API call per reranking). Too slow for real-time applications
with many candidates.

### Cohere Rerank API

Cohere offers a dedicated reranking API that is faster and cheaper than LLM-based reranking
while being more precise than cross-encoders.

**Pipeline:**
1. Bi-encoder retrieval: top-50 candidates
2. Cohere Rerank: re-score top-50, return top-5
3. LLM generation with top-5 reranked results

**Advantage:** Good balance of precision, speed, and cost.
**Disadvantage:** External API dependency. May not be trained on clinical text.

### Reranking Strategy Selection

| Approach | Precision | Latency | Cost | Best For |
|----------|-----------|---------|------|----------|
| No reranking | Baseline | Fastest | Free | Simple queries, small document sets |
| Cross-encoder | +10-15% | +100ms | Compute only | Real-time applications, moderate precision needs |
| Cohere Rerank | +15-20% | +200ms | $0.001/query | Production applications with cost constraints |
| LLM reranking | +20-25% | +2-5s | $0.01-0.05/query | Offline or batch processing, highest precision |

For clinical RAG systems, cross-encoder reranking is the sweet spot: meaningful precision
improvement without significant latency or cost overhead. Reserve LLM reranking for batch
evaluation or offline analysis.

---

## Key Takeaways

1. **Standard RAG is a starting point, not an end state.** Sentence-window retrieval,
   auto-merging, and reranking each provide 10-15% improvement in retrieval quality.
   Combined, they transform a mediocre RAG system into a reliable one.

2. **The RAG evaluation triad is the debugging framework.** When a RAG system gives wrong
   answers, the triad tells you whether the problem is retrieval, grounding, or generation.
   Without this framework, you are guessing.

3. **Chunking strategy should match document structure.** There is no universal best chunking
   strategy. The right choice depends on the document type, query patterns, and retrieval
   requirements.

4. **Reranking is the highest-ROI retrieval improvement.** Adding a cross-encoder reranking
   step takes minimal engineering effort and consistently improves precision. It should be
   the first optimization after baseline RAG is working.

5. **Clinical RAG has higher stakes than general RAG.** A wrong answer from a general-purpose
   chatbot is annoying. A wrong answer from a clinical RAG system could inform a treatment
   decision. Every retrieval improvement directly impacts patient safety.
