# Advanced RAG Certificate -- Practice Questions

15 practice questions covering advanced RAG concepts with detailed answers.

---

## Question 1: Sentence-Window Retrieval

**Q: Explain the fundamental tradeoff in RAG chunk size and how sentence-window retrieval
addresses it.**

**A:** The tradeoff is between retrieval precision and generation context. Small chunks
(100-200 tokens) produce focused embeddings that match specific queries well, giving high
retrieval precision. But small chunks lack surrounding context, so the LLM may not have
enough information to generate a complete answer. Large chunks (800-1000 tokens) provide
rich context for generation but produce diluted embeddings that match queries less precisely,
because irrelevant content in the chunk distorts the similarity score.

Sentence-window retrieval decouples these two concerns. It embeds individual sentences
(maximum precision) but when a sentence is retrieved, it expands the context to a window
of surrounding sentences (e.g., 3-5 sentences on each side) before sending to the LLM.
The retrieval step operates on small, focused units for precision. The generation step
receives expanded context for completeness. This eliminates the tradeoff rather than
compromising between the two sides.

---

## Question 2: Auto-Merging Retrieval

**Q: A clinical treatment guideline has 3 levels of hierarchy: chapters, sections, and
paragraphs. You retrieve 4 out of 5 paragraphs from Section 2.3 "Dosing Guidelines."
Explain what auto-merging does and why it produces a better result than returning the
4 individual paragraphs.**

**A:** Auto-merging detects that 4 out of 5 child paragraphs from the same parent section
were retrieved and promotes the retrieval result to the full parent section (Section 2.3
"Dosing Guidelines"). Instead of returning 4 disconnected paragraphs, it returns the
complete section.

This produces a better result for three reasons. First, the 5th paragraph that was not
individually retrieved likely contains related information (perhaps dosing for a specific
population or contraindications) that completes the picture -- the LLM gets information it
would have missed. Second, the paragraph order and transitions are preserved. Dosing
guidelines often build sequentially (standard dose, then adjustments, then
contraindications), and disconnected paragraphs lose this logical flow. Third, the context
is contiguous, which reduces the chance that the LLM misinterprets a paragraph taken out
of context. A paragraph saying "reduce dose by 50%" makes sense only when preceded by
the paragraph explaining which patient population this applies to.

---

## Question 3: RAG Evaluation Triad

**Q: Your RAG system produces an answer that is factually correct but not supported by the
retrieved context. Which metric in the RAG triad would flag this, and what does it indicate?**

**A:** The Groundedness metric would flag this. Groundedness measures whether the generated
answer is supported by the retrieved context -- whether every claim in the answer can be
traced back to the provided documents.

A factually correct but ungrounded answer means the LLM is drawing on its training data
rather than the retrieved context. This is a serious problem in clinical RAG for two reasons.
First, the LLM's training data may be outdated -- clinical guidelines change, and a
treatment recommendation from the model's training data may no longer be current. Second,
the entire point of RAG is to provide authoritative, citable answers grounded in specific
documents. An ungrounded answer cannot be cited, audited, or verified.

To fix this: strengthen the system prompt to explicitly instruct the model to only use
provided context and to say "I don't have this information in the provided documents"
when context is insufficient. Also check whether the retrieved context actually contains
the information needed to answer the query (Context Relevance metric) -- if it does not,
the LLM has no choice but to use training data or refuse.

---

## Question 4: Chunking Strategy Selection

**Q: You need to build a RAG system over three types of clinical documents: (1) structured
treatment guidelines with sections and subsections, (2) free-text therapy session notes,
and (3) a drug interaction database. Recommend a chunking strategy for each and explain
your reasoning.**

**A:** For structured treatment guidelines: document-structure-aware chunking combined with
auto-merging retrieval. Parse the section hierarchy (chapters, sections, subsections) and
use it as the chunk hierarchy. Leaf nodes are subsections, parents are sections, grandparents
are chapters. This preserves the document's logical structure and enables auto-merging when
queries span multiple subsections.

For free-text therapy session notes: semantic chunking. These notes lack consistent
formatting -- a therapist may jump from the patient's reported symptoms to family history
to treatment response without section headers. Semantic chunking detects topic shifts by
measuring embedding similarity between adjacent sentences and splits where the topic
changes. This produces semantically coherent chunks even without structural markers.

For the drug interaction database: proposition-based chunking. Each drug-drug interaction
is an independent fact ("Sertraline + MAOIs: contraindicated due to serotonin syndrome
risk"). These facts need to be individually retrievable. Use an LLM to extract atomic
propositions, then embed each proposition independently. This gives maximum retrieval
precision for specific drug interaction queries.

---

## Question 5: Reranking

**Q: You add a cross-encoder reranking step to your clinical RAG pipeline and observe that
Precision@5 improves from 0.72 to 0.84, but end-to-end latency increases from 300ms to
450ms. Is this tradeoff acceptable for a clinical application? How would you decide?**

**A:** For most clinical applications, this tradeoff is clearly acceptable. A 12-point
precision improvement means that out of 5 retrieved chunks, on average 4.2 are now relevant
versus 3.6 before. That additional relevant chunk can mean the difference between a
complete and incomplete clinical answer. The 150ms latency increase (300ms to 450ms) is
imperceptible to the user, especially since the full end-to-end latency including LLM
generation is typically 2-5 seconds.

The decision framework depends on two factors: the clinical consequence of retrieval errors
and the latency budget. If retrieval errors could lead to incorrect treatment information,
the precision improvement is essentially a safety improvement, making 150ms of latency
trivially worth it. If the application has a strict latency budget (e.g., real-time triage
during an emergency consultation), the calculus changes, but even then, 450ms is well
within any reasonable clinical workflow latency requirement.

The only scenario where I would not add reranking is if the initial retrieval precision
is already very high (>0.95) or if the document collection is so small that the bi-encoder
already retrieves mostly relevant content.

---

## Question 6: Context Relevance

**Q: Your RAG system retrieves 5 chunks for a query about "SSRI dosing in elderly patients."
Three chunks discuss SSRIs in general adults, one discusses elderly patient care in general,
and one discusses SSRI dosing specifically for elderly patients. What is the Context Relevance
score, and how would you improve it?**

**A:** Context Relevance is approximately 0.20 (1 out of 5 chunks is directly relevant to
the specific query). The three general SSRI chunks are partially relevant but not specific
to elderly patients. The general elderly care chunk is partially relevant but not specific
to SSRIs. Only one chunk addresses the specific intersection.

To improve this: First, try reranking. A cross-encoder reranker would likely score the
elderly-specific SSRI chunk much higher than the general chunks, pushing it to the top of
results. Second, consider query decomposition: split "SSRI dosing in elderly patients"
into sub-queries ("SSRI dosing guidelines" AND "elderly patient medication adjustments")
and require retrieved chunks to match multiple sub-queries. Third, use metadata filtering:
if documents are tagged with patient population metadata, filter retrieval to
elderly-relevant documents before similarity search. Fourth, improve the embedding model:
a clinical embedding model would better distinguish "SSRIs in general" from "SSRIs in
elderly" because it understands that dosing differs by population.

---

## Question 7: Groundedness Failures

**Q: A clinician asks the RAG system "What is the maximum daily dose of sertraline?" The
system retrieves a chunk that says "Sertraline is typically started at 50mg daily" and
generates the answer "The maximum daily dose of sertraline is 200mg." This is factually
correct but not in the retrieved context. How do you diagnose and fix this?**

**A:** Diagnosis: The Groundedness metric would be low because the answer (200mg maximum dose)
is not supported by the retrieved context (which only mentions the starting dose). The
Context Relevance metric might also be low if the chunk about starting dose is the best
available but does not contain maximum dose information.

Two possible root causes: (1) The document collection does not contain information about
maximum doses, so no relevant chunk exists to retrieve. (2) The information exists but the
retrieval failed to find it.

To fix: First, check the document collection. Search for "sertraline" and "maximum dose"
to verify the information exists. If it does not exist, the fix is to add relevant
documents (drug reference materials, prescribing information). If the information does
exist but was not retrieved, investigate why: is the chunk too large (relevant sentence
buried in a large chunk)? Is the embedding model failing to match "maximum daily dose"
with the relevant passage?

Additionally, strengthen the system prompt to prevent the LLM from supplementing retrieved
context with training data. Add an explicit instruction: "If the provided context does not
contain the information needed to answer the question, state that the information is not
available in the current documents. Do not use information from outside the provided context."

---

## Question 8: Hybrid Retrieval

**Q: Explain how hybrid retrieval (combining sparse and dense retrieval) can improve
performance for clinical text with specialized terminology.**

**A:** Dense retrieval (embedding-based) captures semantic meaning but can struggle with
exact clinical terminology. If a clinician queries "SNRI augmentation for MDD with comorbid
GAD," dense retrieval matches the semantic meaning but might not prioritize documents that
use these exact acronyms. Sparse retrieval (BM25/keyword-based) excels at exact term
matching but misses semantic relationships ("depression treatment" should match "MDD
management" even though the terms differ).

Hybrid retrieval combines both: run a dense retrieval and a sparse retrieval in parallel,
then merge and deduplicate the results. The merging strategy matters: Reciprocal Rank
Fusion (RRF) is the most common approach -- it combines the rankings from both methods,
giving credit to documents that appear in both result sets.

For clinical text, hybrid retrieval is particularly valuable because clinical queries mix
exact terminology (ICD-10 codes, drug names, abbreviations) with semantic intent. A query
like "F32.1 treatment options" has both an exact component (the ICD-10 code) that sparse
retrieval handles well and a semantic component ("treatment options") that dense retrieval
handles well. Neither approach alone captures both.

---

## Question 9: Embedding Model Selection

**Q: You are choosing between a general-purpose embedding model (text-embedding-3-small)
and a biomedical embedding model (PubMedBERT-based) for a clinical RAG system. How would
you evaluate which is better for your use case?**

**A:** Create an evaluation dataset of 30-50 clinical queries with expert-annotated relevant
documents. For each query, a clinician identifies which documents in the collection are
relevant. Then run both embedding models on the same queries and measure retrieval quality
using Precision@5, Recall@5, MRR (Mean Reciprocal Rank), and NDCG@5.

Beyond aggregate metrics, analyze failure modes. Are there specific query types where one
model outperforms the other? The biomedical model likely handles clinical abbreviations
(SOB = shortness of breath, not emotional state), drug names, and diagnosis terminology
better. The general-purpose model may handle conversational queries and broader medical
questions better.

Also consider practical factors: the biomedical model may require local hosting (higher
infrastructure cost, lower latency) while the general-purpose model has a simple API.
Embedding dimension affects storage and retrieval speed. And critically: test with your
actual document types, not generic benchmarks. A model that performs well on PubMed
abstracts may not perform well on clinical session notes.

In my experience, the biomedical model improved retrieval precision by 8% on clinical
queries involving specific diagnoses and medications, but performed similarly to the
general-purpose model on broader queries.

---

## Question 10: Multi-Document Synthesis

**Q: A clinician asks "What are the contraindications for combining lithium with NSAIDs
in a patient with renal impairment?" This requires information from multiple documents.
How does your RAG system handle this?**

**A:** This query requires synthesizing three pieces of information: lithium
contraindications, NSAID interactions, and renal impairment considerations. A standard
RAG pipeline may retrieve chunks about each topic but fail to synthesize them into a
coherent answer.

Three approaches to improve multi-document synthesis: First, increase top-k retrieval (e.g.,
top-10 instead of top-5) and use MMR (Maximal Marginal Relevance) to ensure diversity
across the retrieved chunks. This increases the chance of retrieving relevant chunks from
all three document areas. Second, use query decomposition: break the complex query into
sub-queries ("lithium contraindications," "lithium-NSAID interaction," "NSAID use in
renal impairment") and retrieve for each sub-query independently, then merge and deduplicate
results. Third, add an explicit synthesis instruction to the generation prompt: "The
retrieved context comes from multiple documents. Synthesize information across all sources
to provide a comprehensive answer. Note when sources agree, conflict, or provide
complementary information."

For this specific clinical query, the answer should cover: NSAIDs reduce renal lithium
clearance (increasing lithium levels), renal impairment further reduces clearance (double
risk), and the combination is generally contraindicated with specific monitoring requirements
if unavoidable. Only by synthesizing across document types does the full clinical picture
emerge.

---

## Question 11: Chunk Overlap

**Q: Why is chunk overlap important in clinical RAG, and how do you determine the right
overlap size?**

**A:** Chunk overlap prevents information loss at chunk boundaries. In clinical text, a
critical finding often spans a boundary: "The patient's potassium was" at the end of
chunk N and "5.8 mEq/L, which is critically elevated given their renal history" at the
start of chunk N+1. Without overlap, neither chunk contains the complete finding. With
overlap, both chunks contain the full statement.

For clinical text, overlap is especially important because: clinical findings are often
expressed as compound sentences (lab value + interpretation + clinical significance),
medication instructions span multiple sentences (drug + dose + frequency +
contraindications), and assessment sections build progressively (findings + reasoning +
diagnosis).

To determine overlap size: start with 20% of chunk size (e.g., 100-token overlap for
500-token chunks). Run retrieval evaluation on a test set with different overlap values
(0%, 10%, 20%, 30%). Measure both retrieval precision (does overlap improve it?) and
storage cost (overlap increases total chunks by ~20-30%). In my experience, 20% overlap
provides the best tradeoff: it catches most boundary-spanning information without
excessive duplication.

Too much overlap (>30%) creates near-duplicate chunks that waste storage and can bias
retrieval toward information that appears in many overlapping chunks.

---

## Question 12: Query Transformation

**Q: A clinician types "why isn't the sertraline working?" into the RAG system. This
conversational query will likely retrieve poorly. How would you transform it for better
retrieval?**

**A:** The original query is conversational and lacks clinical specificity. The RAG system
needs to retrieve from clinical protocol documents, which use formal terminology.

Three query transformation approaches: First, query rewriting using an LLM. Prompt the
LLM: "Rewrite this clinical question in formal medical terminology: 'why isn't the
sertraline working?'" The LLM might produce: "Sertraline treatment non-response:
differential causes, inadequate SSRI response evaluation, and next steps for
treatment-resistant depression." This formal query matches clinical document language
much better.

Second, HyDE (Hypothetical Document Embeddings). Instead of embedding the query, ask an
LLM to generate a hypothetical answer, then embed that answer and use it for retrieval.
The hypothetical answer will contain clinical terminology ("treatment-resistant depression,"
"dose optimization," "augmentation strategies") that matches document embeddings better
than the conversational query.

Third, query expansion. Generate multiple related queries and retrieve for each: "SSRI
treatment non-response," "sertraline dose adjustment criteria," "switching from sertraline
to another antidepressant," "treatment-resistant depression management." Merge results
from all expanded queries.

For a clinical RAG system, I recommend query rewriting as the default approach because it
is fast (single LLM call), produces consistent results, and handles the
conversational-to-clinical terminology gap directly.

---

## Question 13: Evaluation Dataset Construction

**Q: How would you build an evaluation dataset for a RAG system that answers questions
about mental health treatment protocols?**

**A:** An evaluation dataset for RAG needs three components per test case: a query, the
set of relevant documents (for retrieval evaluation), and the correct answer (for
generation evaluation).

Step 1: Generate diverse queries. Work with clinicians to create 50+ questions spanning
different query types: factual ("What is the PHQ-9 threshold for referral?"),
comparative ("How does CBT compare to medication for moderate depression?"),
procedural ("What is the intake assessment protocol for new patients?"), and complex
multi-document queries. Include queries at different specificity levels: broad ("How is
depression treated?") and narrow ("What is the recommended sertraline starting dose for
adolescents with comorbid anxiety?").

Step 2: Annotate relevant documents. For each query, have a clinician identify which
documents (or specific sections) in the collection contain the information needed to
answer the query. This enables measuring retrieval precision and recall.

Step 3: Write reference answers. Have clinicians write gold-standard answers for each
query. These serve as evaluation references for answer quality (though G-Eval with rubrics
may be more appropriate than ROUGE for evaluating free-text clinical answers).

Step 4: Include adversarial cases. Add queries where the answer is not in the document
collection (the system should say "not found" rather than hallucinate), queries with
ambiguous or outdated information, and queries that require synthesizing conflicting
guidance from multiple documents.

Step 5: Version and maintain. The evaluation dataset is a living artifact. When new
failure modes are discovered in production, add them to the test set.

---

## Question 14: Metadata Filtering in Clinical RAG

**Q: Explain why metadata filtering is critical for clinical RAG and describe the key
metadata fields for clinical documents.**

**A:** Metadata filtering is critical because not all documents in a clinical knowledge
base are equally relevant for every query, and relevance depends on factors that
embedding similarity alone cannot capture.

Key metadata fields:

1. **Document type** (guideline, protocol, assessment tool, drug reference). A query about
   treatment options should prioritize treatment guidelines over assessment tools.

2. **Publication/effective date.** Clinical guidelines are updated regularly. Retrieving
   an outdated guideline is dangerous. Filter to the most recent version unless
   specifically querying historical guidance.

3. **Patient population** (adult, adolescent, elderly, pregnant). Dosing guidelines differ
   by population. A query about pediatric dosing should filter out adult-only guidelines.

4. **Clinical domain** (depression, anxiety, substance use, psychosis). In a broad mental
   health knowledge base, domain filtering reduces noise significantly.

5. **Evidence level/authority** (national guideline, institutional protocol, expert opinion).
   Prioritize higher-evidence sources.

6. **Status** (active, superseded, draft). Never retrieve superseded guidelines for
   clinical queries.

Implementation: Store metadata alongside each chunk in the vector store. At query time,
apply metadata filters before or alongside similarity search. For example:
`retrieve(query, filters={"document_type": "guideline", "status": "active", "date": ">2022-01-01"})`.

Without metadata filtering, a clinical RAG system might answer a question about current
treatment recommendations by citing a 2018 guideline that has been superseded, which is
worse than not answering at all.

---

## Question 15: Production RAG Monitoring

**Q: Your clinical RAG system has been running in production for 3 months. Describe the
monitoring strategy you would implement to detect quality degradation over time.**

**A:** Production RAG monitoring operates at three levels: retrieval quality, generation
quality, and system health.

Retrieval monitoring: Sample 5% of production queries. For each sampled query, log the
retrieved chunks, their relevance scores, and their metadata. Track: average relevance
score over time (drift indicates embedding degradation or document collection changes),
percentage of queries with zero relevant chunks above threshold (indicates coverage gaps),
and metadata distribution of retrieved chunks (are certain document types over-represented?).

Generation monitoring: For sampled queries, run the RAG evaluation triad (Context Relevance,
Groundedness, Answer Relevance) using LLM-as-judge. Track rolling averages for each metric.
Alert when any metric drops below threshold. Also track: answer length distribution
(sudden changes indicate prompt or model behavior shifts), refusal rate ("I don't have
this information" -- increasing rate may indicate coverage gaps), and clinician correction
rate if available.

System health monitoring: Track latency (retrieval latency, generation latency, end-to-end),
error rates (API failures, embedding failures, parsing failures), token usage and cost,
and vector store performance (query time, index size, memory usage).

Proactive checks: Weekly automated evaluation run on a fixed test set to detect gradual
drift that production sampling might miss. Monthly review of the most-corrected or
lowest-scoring production queries to identify systematic failure patterns. Quarterly
review of the document collection to ensure documents are current and complete.

The key principle: RAG quality degrades silently. Without active monitoring, you discover
quality problems only when a clinician complains. By then, the problem may have existed
for weeks or months.
