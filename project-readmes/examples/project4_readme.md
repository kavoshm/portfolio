# Agentic Clinical Intake Pipeline

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-0.1+-purple)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991?logo=openai&logoColor=white)
![FHIR R4](https://img.shields.io/badge/FHIR-R4-red)
![LangChain](https://img.shields.io/badge/LangChain-0.1+-green?logo=chainlink&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

A multi-step agentic pipeline that ingests unstructured clinical notes, extracts structured
data (diagnoses, medications, allergies, risk flags) through a chain of specialized LLM
agents, validates results against clinical schemas, and writes FHIR R4-compliant resources
back to the EHR. Built with LangGraph for stateful orchestration and human-in-the-loop
checkpoints at safety-critical decision points.

In pilot deployment, this pipeline reduced manual data entry time for intake workflows
substantially, while maintaining data quality through multi-stage validation and clinician
review gates.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                  Agentic Clinical Intake Pipeline                     │
│                                                                      │
│  ┌──────────┐                                                        │
│  │ Raw      │   Unstructured clinical note (free text, PDF, fax)     │
│  │ Clinical │                                                        │
│  │ Note     │                                                        │
│  └────┬─────┘                                                        │
│       │                                                              │
│       v                                                              │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  STAGE 1: Entity Extraction                                     │ │
│  │  ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐│ │
│  │  │ Demographics│ │ Diagnoses│ │Medications│ │ Allergies +     ││ │
│  │  │ Agent       │ │ Agent    │ │ Agent     │ │ Risk Flags Agent││ │
│  │  └────────────┘ └──────────┘ └──────────┘ └──────────────────┘│ │
│  │  (Parallel extraction using function calling)                   │ │
│  └──────────────────────────┬──────────────────────────────────────┘ │
│                              │                                       │
│                              v                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  STAGE 2: Clinical Validation                                   │ │
│  │  ┌──────────────────┐  ┌──────────────────┐                    │ │
│  │  │ ICD-10 Code      │  │ Drug Interaction  │                    │ │
│  │  │ Validator        │  │ Checker           │                    │ │
│  │  └──────────────────┘  └──────────────────┘                    │ │
│  │  ┌──────────────────┐  ┌──────────────────┐                    │ │
│  │  │ FHIR Schema      │  │ Allergy Cross-   │                    │ │
│  │  │ Validator        │  │ Reference        │                    │ │
│  │  └──────────────────┘  └──────────────────┘                    │ │
│  └──────────────────────────┬──────────────────────────────────────┘ │
│                              │                                       │
│                              v                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  STAGE 3: Human-in-the-Loop Review          [CHECKPOINT]       │ │
│  │                                                                 │ │
│  │  ┌─────────────────────────────────────────────────────────┐   │ │
│  │  │  Clinician Review Dashboard                              │   │ │
│  │  │  - Extracted entities highlighted in original note       │   │ │
│  │  │  - Validation warnings displayed                         │   │ │
│  │  │  - Approve / Edit / Reject for each entity               │   │ │
│  │  │  - Risk flags require explicit acknowledgment            │   │ │
│  │  └─────────────────────────────────────────────────────────┘   │ │
│  │                                                                 │ │
│  │  Auto-approve path: if confidence > 0.95 AND no risk flags     │ │
│  │  AND no validation warnings → skip human review                 │ │
│  └──────────────────────────┬──────────────────────────────────────┘ │
│                              │                                       │
│                              v                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  STAGE 4: FHIR Resource Generation                              │ │
│  │  ┌────────────┐ ┌────────────────┐ ┌────────────────────────┐  │ │
│  │  │ Patient    │ │ Condition      │ │ MedicationStatement    │  │ │
│  │  │ Resource   │ │ Resources      │ │ Resources              │  │ │
│  │  └────────────┘ └────────────────┘ └────────────────────────┘  │ │
│  │  ┌────────────┐ ┌────────────────┐                             │ │
│  │  │ Allergy    │ │ RiskAssessment │                             │ │
│  │  │ Intolerance│ │ Resource       │                             │ │
│  │  └────────────┘ └────────────────┘                             │ │
│  └──────────────────────────┬──────────────────────────────────────┘ │
│                              │                                       │
│                              v                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  STAGE 5: EHR Integration                                      │ │
│  │  POST /fhir/Patient, /fhir/Condition, etc.                     │ │
│  │  + Audit log entry                                              │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Key Features

- **Multi-agent extraction** -- Parallel specialized agents for demographics, diagnoses, medications, and allergies/risk flags, each with domain-specific function calling schemas
- **LangGraph state management** -- Stateful pipeline with explicit state transitions, retry logic, and checkpoint persistence for human-in-the-loop review
- **Clinical validation tools** -- ICD-10 code validation, drug interaction checking, allergy cross-reference, and FHIR schema validation as LangChain tools
- **Human-in-the-loop checkpoints** -- Clinician review gates at safety-critical stages with approve/edit/reject workflow
- **FHIR R4 output** -- Generates valid FHIR R4 resources (Patient, Condition, MedicationStatement, AllergyIntolerance, RiskAssessment)
- **Confidence-based routing** -- High-confidence, low-risk extractions can auto-approve; uncertain or flagged extractions require human review
- **Full audit trail** -- Every extraction, validation, review decision, and FHIR write is logged for compliance

---

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- FHIR R4 server (or mock server for development)

### Installation

```bash
git clone https://github.com/kavoshmonfared/agentic-intake-pipeline.git
cd agentic-intake-pipeline
pip install -r requirements.txt
cp .env.example .env  # Add OPENAI_API_KEY and FHIR_SERVER_URL
```

### Run the Pipeline

```bash
# Process a single clinical note
python pipeline.py --input data/sample_notes/intake_note_001.txt

# Process a batch
python pipeline.py --batch data/sample_notes/ --output results/

# Run with human-in-the-loop review (opens review UI)
python pipeline.py --input data/sample_notes/intake_note_001.txt --review
```

---

## Usage Examples

### End-to-End Pipeline Execution

```python
from intake_pipeline import IntakePipeline

pipeline = IntakePipeline(
    model="gpt-4",
    fhir_server="http://localhost:8080/fhir",
    human_review=True  # Enable human-in-the-loop
)

result = pipeline.process(
    note="""
    Maria Santos, DOB 03/15/1978, Female
    MRN: 2024-1847

    Presenting complaint: Patient reports persistent low mood, insomnia, and
    loss of appetite for the past 6 weeks. Previously diagnosed with GAD
    (F41.1) in 2019. Currently on sertraline 100mg daily and lorazepam
    0.5mg PRN for anxiety. Reports alcohol use 3-4 drinks/week, denies
    illicit drug use. Allergic to penicillin (rash).

    PHQ-9 score: 16 (moderately severe depression)
    GAD-7 score: 12 (moderate anxiety)

    Assessment: Major depressive episode superimposed on generalized anxiety
    disorder. Consider SSRI dose adjustment. Monitor closely given
    benzodiazepine use and alcohol consumption.
    """
)
```

### Extracted Entities (Stage 1 Output)

```json
{
  "demographics": {
    "name": "Maria Santos",
    "date_of_birth": "1978-03-15",
    "sex": "female",
    "mrn": "2024-1847",
    "confidence": 0.98
  },
  "diagnoses": [
    {
      "description": "Major depressive episode",
      "icd10": "F32.1",
      "status": "active",
      "onset": "6 weeks ago",
      "confidence": 0.92
    },
    {
      "description": "Generalized anxiety disorder",
      "icd10": "F41.1",
      "status": "active",
      "onset": "2019",
      "confidence": 0.97
    }
  ],
  "medications": [
    {
      "name": "sertraline",
      "dose": "100mg",
      "frequency": "daily",
      "route": "oral",
      "status": "active",
      "confidence": 0.96
    },
    {
      "name": "lorazepam",
      "dose": "0.5mg",
      "frequency": "PRN",
      "route": "oral",
      "status": "active",
      "confidence": 0.95
    }
  ],
  "allergies": [
    {
      "substance": "penicillin",
      "reaction": "rash",
      "severity": "moderate",
      "confidence": 0.97
    }
  ],
  "risk_flags": [
    {
      "flag": "benzodiazepine_alcohol_interaction",
      "severity": "moderate",
      "detail": "Patient on lorazepam with reported alcohol use (3-4 drinks/week). Risk of CNS depression.",
      "confidence": 0.88
    },
    {
      "flag": "phq9_moderately_severe",
      "severity": "moderate",
      "detail": "PHQ-9 score 16 indicates moderately severe depression. Close monitoring recommended.",
      "confidence": 0.99
    }
  ]
}
```

### FHIR R4 Output (Stage 4)

```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Patient",
        "identifier": [{"system": "urn:mrn", "value": "2024-1847"}],
        "name": [{"family": "Santos", "given": ["Maria"]}],
        "gender": "female",
        "birthDate": "1978-03-15"
      },
      "request": {"method": "PUT", "url": "Patient?identifier=2024-1847"}
    },
    {
      "resource": {
        "resourceType": "Condition",
        "code": {
          "coding": [{"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": "F32.1", "display": "Major depressive disorder, single episode, moderate"}]
        },
        "clinicalStatus": {"coding": [{"code": "active"}]},
        "subject": {"reference": "Patient?identifier=2024-1847"}
      },
      "request": {"method": "POST", "url": "Condition"}
    },
    {
      "resource": {
        "resourceType": "MedicationStatement",
        "medicationCodeableConcept": {
          "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "display": "sertraline 100mg oral tablet"}]
        },
        "dosage": [{"text": "100mg daily", "route": {"text": "oral"}}],
        "status": "active",
        "subject": {"reference": "Patient?identifier=2024-1847"}
      },
      "request": {"method": "POST", "url": "MedicationStatement"}
    },
    {
      "resource": {
        "resourceType": "AllergyIntolerance",
        "code": {"text": "penicillin"},
        "reaction": [{"manifestation": [{"text": "rash"}], "severity": "moderate"}],
        "patient": {"reference": "Patient?identifier=2024-1847"}
      },
      "request": {"method": "POST", "url": "AllergyIntolerance"}
    }
  ]
}
```

---

## Human-in-the-Loop Workflow

The pipeline implements a checkpoint-based review workflow:

```
  Extraction complete
        │
        v
  ┌─────────────────────────┐
  │ Confidence check:        │
  │ All entities > 0.95?     │──── YES ──> ┌─────────────────┐
  │ No risk flags?           │             │ Auto-approve     │
  │ No validation warnings?  │             │ (logged as auto) │
  └────────┬────────────────┘             └────────┬────────┘
           │ NO                                     │
           v                                        │
  ┌─────────────────────────┐                       │
  │ Human Review Queue       │                       │
  │                         │                       │
  │ Clinician sees:          │                       │
  │ - Original note          │                       │
  │ - Extracted entities     │                       │
  │ - Confidence scores      │                       │
  │ - Validation warnings    │                       │
  │ - Risk flags             │                       │
  │                         │                       │
  │ Actions:                 │                       │
  │ [Approve] [Edit] [Reject]│                       │
  └────────┬────────────────┘                       │
           │                                        │
           v                                        v
  ┌─────────────────────────────────────────────────────┐
  │ FHIR Resource Generation + EHR Write                │
  └─────────────────────────────────────────────────────┘
```

**Auto-approve criteria:**
- All entity confidence scores > 0.95
- No risk flags of severity "high" or "critical"
- No validation warnings (ICD-10 valid, no drug interactions, FHIR schema passes)
- In pilot: ~35% of notes met auto-approve criteria

---

## Project Structure

```
agentic-intake-pipeline/
├── src/
│   ├── __init__.py
│   ├── pipeline.py              # Main pipeline orchestration (LangGraph)
│   ├── graph.py                 # LangGraph state graph definition
│   ├── state.py                 # Pipeline state schema
│   ├── agents/
│   │   ├── demographics.py      # Demographics extraction agent
│   │   ├── diagnoses.py         # Diagnosis extraction agent
│   │   ├── medications.py       # Medication extraction agent
│   │   └── allergies_risks.py   # Allergy and risk flag agent
│   ├── tools/
│   │   ├── icd10_validator.py   # ICD-10 code validation tool
│   │   ├── drug_interaction.py  # Drug interaction checker tool
│   │   ├── fhir_validator.py    # FHIR R4 schema validator tool
│   │   └── allergy_xref.py     # Allergy cross-reference tool
│   ├── fhir/
│   │   ├── resource_builder.py  # FHIR resource construction
│   │   ├── bundle_builder.py    # Transaction bundle assembly
│   │   └── client.py            # FHIR server client
│   ├── review/
│   │   ├── checkpoint.py        # Human-in-the-loop checkpoint logic
│   │   └── dashboard.py         # Review dashboard (Streamlit)
│   └── utils/
│       ├── audit_log.py         # Audit trail logging
│       └── cost_tracker.py      # Token and cost tracking
├── config/
│   ├── agent_prompts/           # Prompt templates for each agent
│   ├── tool_configs/            # Tool configuration files
│   ├── fhir_profiles/           # FHIR R4 profile definitions
│   └── pipeline_config.yaml     # Pipeline settings
├── tests/
│   ├── test_extraction.py       # Entity extraction tests
│   ├── test_validation.py       # Validation tool tests
│   ├── test_fhir_output.py      # FHIR resource tests
│   ├── test_pipeline_e2e.py     # End-to-end pipeline tests
│   └── fixtures/
│       ├── sample_notes/        # Synthetic clinical notes
│       └── expected_fhir/       # Expected FHIR output
├── data/
│   └── sample_notes/            # Sample input data (no PHI)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Design Decisions

### Why LangGraph Over a Simple LangChain Sequential Chain
**Context:** The pipeline has branching logic (parallel extraction agents), conditional routing (auto-approve vs. human review), and stateful checkpoints.
**Decision:** LangGraph for pipeline orchestration.
**Rationale:** A sequential chain cannot handle: (1) parallel agent execution for Stage 1, (2) conditional branching based on confidence scores and risk flags, (3) state persistence for human-in-the-loop review (the pipeline must pause, save state, and resume after clinician input). LangGraph's graph-based execution model handles all three natively.
**Tradeoff:** More complex to debug than a linear chain. Mitigated by comprehensive logging at each state transition.

### Why Parallel Extraction Agents
**Context:** A single agent extracting all entities (demographics + diagnoses + medications + allergies) from a clinical note produced inconsistent results -- it would sometimes focus on medications and miss allergy details.
**Decision:** Four specialized extraction agents running in parallel, each with a focused prompt and output schema.
**Rationale:** Specialization improves extraction quality. Each agent has a prompt tailored to its entity type, with domain-specific few-shot examples. A demographics agent does not need to know about drug interactions; a medication agent does not need to parse names and dates. Parallel execution means Stage 1 takes as long as the slowest agent (~3s) rather than 4x sequential (~12s).
**Tradeoff:** 4x the API calls and cost for extraction. Worth it for quality.

### Why Confidence-Based Auto-Approve
**Context:** Requiring human review for every note defeats the purpose of automation.
**Decision:** Auto-approve pipeline results when confidence is high, risk is low, and validation passes.
**Rationale:** Clinical notes that are clearly structured, contain standard terminology, and produce high-confidence extractions do not benefit from human review. The auto-approve criteria are conservative (>0.95 confidence, no risk flags, clean validation). In pilot, ~35% of notes auto-approved, saving significant clinician time on routine cases while keeping humans in the loop for complex or ambiguous notes.
**Tradeoff:** Non-zero risk of auto-approved errors. Mitigated by periodic random audit of auto-approved notes (10% sample).

---

## Evaluation Results

Evaluated on 40 synthetic clinical notes spanning intake assessments, follow-up notes, and referral letters.

### Entity Extraction Accuracy

| Entity Type | Precision | Recall | F1 | Notes |
|-------------|-----------|--------|-----|-------|
| Demographics | 0.98 | 0.97 | 0.975 | Near-perfect on structured fields |
| Diagnoses | 0.91 | 0.87 | 0.89 | Misses implicit diagnoses |
| Medications | 0.94 | 0.92 | 0.93 | Occasionally misses PRN details |
| Allergies | 0.96 | 0.90 | 0.93 | Misses allergies mentioned in passing |
| Risk Flags | 0.85 | 0.92 | 0.88 | High recall (good); some false positives |

### FHIR Validation

| Check | Pass Rate |
|-------|-----------|
| FHIR R4 schema valid | 97.5% (39/40) |
| ICD-10 codes valid | 94% (based on extracted diagnosis count) |
| All required fields present | 100% |

### Pipeline Performance

| Metric | Value |
|--------|-------|
| End-to-end latency (auto-approve path) | 8.2s (p50) |
| End-to-end latency (with human review) | varies |
| Cost per note | ~$0.12 |
| Auto-approve rate | 35% |

---

## Challenges & Solutions

### Challenge 1: Implicit Diagnoses
**Problem:** Clinical notes often imply diagnoses without stating them explicitly. "Patient's blood sugar has been running 250-300, not compliant with insulin" implies uncontrolled diabetes, but the note may not say "diabetes."
**Root Cause:** The diagnosis extraction agent was trained to extract explicitly stated diagnoses.
**Solution:** Added a secondary "inference pass" where the agent reviews extracted medications and lab values to suggest implied diagnoses. These are flagged as "inferred" with lower confidence and always route to human review.

### Challenge 2: Agent Coordination on Overlapping Information
**Problem:** "Allergic to penicillin" could be extracted by both the allergy agent and the medication agent (as a contraindication). This caused duplicate entries.
**Root Cause:** Agents operate independently in parallel and do not see each other's extractions.
**Solution:** Added a deduplication step between Stage 1 (extraction) and Stage 2 (validation) that merges overlapping entities based on semantic similarity and entity type. Penicillin allergy extracted by both agents merges into a single AllergyIntolerance resource.

### Challenge 3: LangGraph State Serialization for Human Review
**Problem:** When the pipeline pauses for human review, the full pipeline state must be persisted and later restored. Complex Python objects in the state (LLM responses, tool call results) were not JSON-serializable.
**Root Cause:** LangGraph's default state persistence assumes JSON-serializable state.
**Solution:** Implemented custom serialization for all state objects. All LLM responses and tool results are stored as serializable dictionaries rather than LangChain objects. Added a state validation step on resume to catch serialization issues before the pipeline continues.

---

## What I Learned

- **Agentic pipelines need explicit state management.** The jump from a single LLM call to a multi-agent pipeline is not incremental -- it requires fundamentally different engineering. State management, error recovery, and checkpoint persistence are the hard problems, not the LLM calls themselves.
- **Human-in-the-loop is a product design problem, not just a technical one.** Building the checkpoint mechanism was straightforward. Designing a review interface where a clinician can quickly understand what was extracted, what the confidence levels mean, and what needs attention -- that was the real challenge.
- **Parallel agents outperform a single generalist agent.** Splitting extraction into four specialized agents improved F1 across all entity types by 5-12% compared to a single agent extracting everything. The cost increase (4x API calls) is worth it.
- **FHIR compliance is a feature, not an afterthought.** Retrofitting FHIR output onto an extraction pipeline that was not designed for it would have been painful. Building FHIR-awareness into the extraction schemas from the start meant the resource generation stage was straightforward.

---

## Future Improvements

- [ ] Add support for scanned/faxed clinical documents (OCR integration)
- [ ] Implement agent-level caching for repeated entity patterns
- [ ] Build a feedback loop where clinician corrections improve extraction prompts
- [ ] Add support for SNOMED CT and LOINC code systems alongside ICD-10
- [ ] Implement batch processing with priority queue for high-risk notes

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Author

**Kavosh Monfared** -- Senior Software Engineer, AI Automation & Healthcare Systems
- GitHub: [@kavoshmonfared](https://github.com/kavoshmonfared)
- LinkedIn: [kavoshmonfared](https://linkedin.com/in/kavoshmonfared)
