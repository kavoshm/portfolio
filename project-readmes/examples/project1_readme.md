# Clinical Note Classifier

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991?logo=openai&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.1+-green?logo=chainlink&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

An LLM-powered classification system that categorizes unstructured clinical notes into
structured urgency levels, department routings, and ICD-10 code suggestions. Built with
prompt engineering techniques -- few-shot learning, chain-of-thought reasoning, and
structured output formatting -- to achieve reliable, explainable classification suitable
for clinical triage workflows.

This project demonstrates that careful prompt engineering, without any model fine-tuning,
can produce classification accuracy competitive with supervised ML approaches on clinical
text, while providing human-readable reasoning for every decision.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                 Clinical Note Classifier                      │
│                                                              │
│  ┌──────────┐    ┌───────────────┐    ┌──────────────────┐  │
│  │ Clinical  │    │  Prompt       │    │  OpenAI GPT-4    │  │
│  │ Note      │───>│  Assembly     │───>│  API             │  │
│  │ (raw text)│    │               │    │  (temp=0)        │  │
│  └──────────┘    │ - System      │    └────────┬─────────┘  │
│                  │   prompt       │             │             │
│                  │ - Few-shot     │             v             │
│                  │   examples     │    ┌──────────────────┐  │
│                  │ - CoT          │    │  JSON Parser +   │  │
│                  │   instruction  │    │  Schema          │  │
│                  │ - Output       │    │  Validation      │  │
│                  │   schema       │    └────────┬─────────┘  │
│                  └───────────────┘             │             │
│                                                v             │
│                                    ┌──────────────────────┐  │
│                                    │ Structured Output    │  │
│                                    │ - urgency_level      │  │
│                                    │ - department         │  │
│                                    │ - icd10_codes[]      │  │
│                                    │ - reasoning          │  │
│                                    │ - risk_flags[]       │  │
│                                    └──────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## Key Features

- **Multi-dimensional classification** -- Simultaneously classifies urgency (1-5 scale), target department, and suggested ICD-10 codes in a single pass
- **Chain-of-thought reasoning** -- Every classification includes step-by-step reasoning, making outputs auditable and debuggable
- **Few-shot calibration** -- 3-5 curated clinical examples in the prompt anchor the model's behavior to domain-appropriate classifications
- **Structured JSON output** -- Schema-validated output integrates directly with downstream EHR systems via FHIR-compatible fields
- **Risk flag detection** -- Identifies high-risk patterns (suicidal ideation, medication interactions, critical lab values) and elevates urgency automatically

---

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key with GPT-4 access

### Installation

```bash
git clone https://github.com/kavoshm/clinical-note-classifier.git
cd clinical-note-classifier
pip install -r requirements.txt
cp .env.example .env  # Add your OPENAI_API_KEY
```

### Run

```bash
# Classify a single note
python classify.py --input "Patient presents with chest pain radiating to left arm, diaphoresis, onset 30 minutes ago."

# Classify a batch from file
python classify.py --batch data/sample_notes.jsonl --output results/
```

---

## Usage Examples

### Single Note Classification

```python
from clinical_classifier import ClinicalNoteClassifier

classifier = ClinicalNoteClassifier(
    model="gpt-4",
    temperature=0,
    few_shot_examples="config/few_shot_examples.json"
)

result = classifier.classify(
    note="48yo M presents with 3-day history of productive cough, fever 101.2F, "
         "decreased breath sounds RLL. CXR shows RLL infiltrate. No known drug allergies. "
         "Started on amoxicillin-clavulanate 875mg BID."
)

print(result)
```

**Output:**
```json
{
  "urgency_level": 3,
  "urgency_label": "Urgent - Same Day",
  "department": "Internal Medicine",
  "icd10_codes": [
    {"code": "J18.1", "description": "Lobar pneumonia, unspecified organism"},
    {"code": "R50.9", "description": "Fever, unspecified"}
  ],
  "risk_flags": [],
  "reasoning": "Step 1: Chief complaint is productive cough with fever, suggesting infectious etiology. Step 2: Physical exam finding of decreased breath sounds RLL correlates with CXR finding of RLL infiltrate, consistent with community-acquired pneumonia. Step 3: Vital signs show low-grade fever but no signs of sepsis or respiratory distress. Step 4: Treatment already initiated with appropriate first-line antibiotic. Step 5: Urgency level 3 - requires same-day evaluation but not emergent given stable presentation and initiated treatment.",
  "confidence": 0.91
}
```

### High-Risk Detection

```python
result = classifier.classify(
    note="22yo F brought in by roommate. Patient reports feeling hopeless for 2 weeks, "
         "not eating, states 'I don't want to be here anymore.' Denies specific plan "
         "but acknowledges passive suicidal ideation. PHQ-9 score: 22."
)
```

**Output:**
```json
{
  "urgency_level": 1,
  "urgency_label": "Emergency - Immediate",
  "department": "Psychiatry / Emergency",
  "icd10_codes": [
    {"code": "R45.851", "description": "Suicidal ideations"},
    {"code": "F32.2", "description": "Major depressive disorder, single episode, severe"}
  ],
  "risk_flags": ["suicidal_ideation", "phq9_severe"],
  "reasoning": "Step 1: Patient expresses passive suicidal ideation ('don't want to be here anymore'). Step 2: PHQ-9 score of 22 indicates severe depression. Step 3: Functional impairment present (not eating). Step 4: Risk flag triggered: suicidal ideation requires immediate psychiatric evaluation regardless of denied specific plan. Step 5: Urgency level 1 - emergency classification due to suicide risk.",
  "confidence": 0.97
}
```

---

## Project Structure

```
clinical-note-classifier/
├── src/
│   ├── __init__.py
│   ├── classify.py              # CLI entry point
│   ├── classifier.py            # Core ClinicalNoteClassifier class
│   ├── prompt_builder.py        # Assembles system prompt + few-shot + CoT
│   ├── schema_validator.py      # Validates JSON output against schema
│   └── risk_detector.py         # Post-classification risk flag checks
├── config/
│   ├── system_prompt.txt        # Base system prompt
│   ├── few_shot_examples.json   # Curated few-shot examples
│   ├── icd10_subset.json        # Valid ICD-10 codes for validation
│   └── risk_patterns.json       # Risk flag trigger patterns
├── tests/
│   ├── test_classifier.py       # Classification accuracy tests
│   ├── test_risk_flags.py       # Risk detection tests
│   ├── test_schema.py           # Output schema validation tests
│   └── fixtures/
│       └── sample_notes.json    # Test clinical notes (synthetic)
├── data/
│   └── sample_notes.jsonl       # Sample input data (no PHI)
├── eval/
│   ├── eval_runner.py           # Evaluation harness
│   ├── eval_results.json        # Latest evaluation results
│   └── rubrics.json             # Evaluation rubrics
├── requirements.txt
├── .env.example
└── README.md
```

---

## Design Decisions

### Why Prompt Engineering Over Fine-Tuning
**Context:** Needed reliable clinical text classification without access to large labeled datasets.
**Decision:** Used few-shot prompting with GPT-4 rather than fine-tuning a smaller model.
**Rationale:** Fine-tuning requires hundreds to thousands of labeled clinical notes, which we did not have. Few-shot with GPT-4 achieved comparable accuracy with 3-5 examples. Additionally, prompt-based approaches are easier to update when classification criteria change (e.g., new department added, urgency scale revised).
**Tradeoff:** Higher per-request cost ($0.03-0.06 per classification vs. ~$0.001 for a fine-tuned model). Acceptable for the volume we handle.

### Why Chain-of-Thought Reasoning Is Required
**Context:** Clinical classification needs to be auditable -- a clinician reviewing the output needs to understand *why* a note was classified a certain way.
**Decision:** CoT reasoning is mandatory in every classification response.
**Rationale:** Without reasoning, a classification of "Urgency 1" is a black box. With CoT, a clinician can verify the logic ("the model flagged suicidal ideation and elevated PHQ-9, which triggered emergency classification"). This also makes debugging systematic: when classification is wrong, the reasoning shows exactly where the logic failed.
**Tradeoff:** Increases output tokens by ~40%, adding ~$0.01 per request. Worth it for auditability.

### Why Temperature = 0
**Context:** Clinical classifications must be deterministic -- the same note should produce the same classification every time.
**Decision:** Temperature set to 0 for all classification calls.
**Rationale:** Any randomness in clinical classification is unacceptable. A note classified as Urgency 3 on Monday should not become Urgency 2 on Tuesday from the same model with the same prompt.
**Tradeoff:** Loses some diversity that might catch edge cases. Mitigated by comprehensive few-shot examples.

---

## Evaluation Results

### Classification Accuracy

Evaluated on 50 synthetic clinical notes across 5 urgency levels and 8 departments.

| Metric | Score | Method |
|--------|-------|--------|
| Urgency accuracy | 88% (44/50) | Exact match with clinician labels |
| Department accuracy | 92% (46/50) | Exact match |
| ICD-10 relevance | 4.1/5.0 | LLM-as-judge (GPT-4) |
| Reasoning quality | 4.3/5.0 | LLM-as-judge with clinical rubric |
| Risk flag recall | 100% (12/12) | All high-risk notes correctly flagged |
| Risk flag precision | 85.7% (12/14) | 2 false positives on ambiguous notes |

### Error Analysis

| Error Type | Count | Pattern |
|------------|-------|---------|
| Urgency off by 1 | 4 | Borderline cases (e.g., 2 vs. 3) where clinical judgment varies |
| Urgency off by 2+ | 2 | Both involved complex multi-system presentations |
| Wrong department | 4 | Cross-specialty cases (e.g., cardiology vs. internal medicine) |
| Missing ICD-10 | 3 | Secondary diagnoses omitted when note was long |

### Latency and Cost

| Metric | Value |
|--------|-------|
| Latency (p50) | 2.1s |
| Latency (p95) | 4.8s |
| Avg input tokens | 320 |
| Avg output tokens | 450 (with CoT) |
| Cost per classification | ~$0.04 |

---

## Challenges & Solutions

### Challenge 1: ICD-10 Code Hallucination
**Problem:** Without constraints, GPT-4 would generate plausible-looking but invalid ICD-10 codes (e.g., "J18.7" which does not exist).
**Root Cause:** The model has seen ICD-10 codes in training data but does not have a validated code list.
**Solution:** Added a post-processing validation step that checks generated codes against a curated subset of valid ICD-10 codes. Invalid codes are flagged rather than silently passed through.

### Challenge 2: Urgency Calibration Across Note Styles
**Problem:** Urgency classification accuracy dropped from 92% to 78% when tested on notes written in a terse, abbreviation-heavy style (e.g., "48M CP rad L arm, diaphor, 30min onset") vs. verbose narrative style.
**Root Cause:** Few-shot examples were all in narrative style. The model had no calibration for abbreviated clinical shorthand.
**Solution:** Added 2 abbreviated-style examples to the few-shot set. Accuracy on terse notes improved to 86%.

### Challenge 3: Multi-System Presentations
**Problem:** Notes describing patients with multiple concurrent issues (e.g., chest pain + psychiatric crisis + diabetic complications) produced confused classifications that tried to merge everything into a single urgency level.
**Root Cause:** The prompt asked for a single classification per note, but some notes describe multiple clinical problems.
**Solution:** Modified the prompt to instruct the model to classify based on the highest-acuity problem and list secondary concerns separately. Improved multi-system classification accuracy from 70% to 85%.

---

## What I Learned

- **Few-shot example selection is the highest-leverage intervention.** Spending an hour curating 5 high-quality few-shot examples improved accuracy more than 10 hours of prompt wording iteration. The examples anchor the model's behavior far more than instructions do.
- **Chain-of-thought is not just for the user -- it is a debugging tool.** When a classification was wrong, the CoT reasoning immediately revealed whether the failure was in entity extraction, clinical reasoning, or urgency calibration. Without CoT, I would have been guessing.
- **Clinical text is adversarial for NLP.** Abbreviations, negations ("denies chest pain" vs. "has chest pain"), and context-dependent terminology ("positive" means different things in different clinical contexts) require explicit handling in the prompt.
- **Temperature = 0 does not mean perfectly deterministic.** Across API calls on different days, I observed ~3% variance in outputs for identical inputs. Likely due to model serving infrastructure. For clinical use, you need idempotency checks beyond temperature settings.

---

## Future Improvements

- [ ] Implement confidence-based routing: low-confidence classifications go to human review
- [ ] Add support for multi-language clinical notes (Farsi clinical text)
- [ ] Build a feedback loop where clinician corrections update the few-shot example set
- [ ] Benchmark against fine-tuned models when labeled data becomes available
- [ ] Add FHIR R4 output format for direct EHR integration

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Author

**Kavosh Monfared** -- Senior Software Engineer, AI Automation & Healthcare Systems
- GitHub: [@kavoshm](https://github.com/kavoshm)
- LinkedIn: [Kavosh Monfared](https://www.linkedin.com/in/kavosh-m-5479063ba/)
