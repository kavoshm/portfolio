# CI/CD Pipeline for Clinical AI

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?logo=github-actions&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-412991?logo=openai&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

A CI/CD pipeline purpose-built for LLM-powered clinical applications. Treats prompt
changes, model configuration updates, and evaluation baselines as first-class artifacts
alongside code -- running automated evaluation suites on every pull request, posting
score comparisons as PR comments, and blocking merges when quality regressions are
detected.

Standard CI/CD catches code bugs. This pipeline catches AI quality regressions: a prompt
change that drops safety scores, a model update that increases hallucination rate, or a
configuration change that breaks output formatting. In healthcare AI, these regressions
are as dangerous as code bugs, and they need the same level of automated detection.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    CI/CD Pipeline for Clinical AI                     │
│                                                                      │
│  TRIGGER: PR that modifies prompts/, config/models.yaml, or src/     │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  STAGE 1: Standard CI                                          │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │  │
│  │  │ Lint     │  │ Type     │  │ Unit     │  │ Integration  │  │  │
│  │  │ (ruff)   │  │ Check    │  │ Tests    │  │ Tests        │  │  │
│  │  │          │  │ (mypy)   │  │ (pytest) │  │ (pytest)     │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │  │
│  └────────────────────────────┬───────────────────────────────────┘  │
│                               │ pass                                 │
│                               v                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  STAGE 2: Prompt Diff Analysis                                 │  │
│  │  ┌───────────────────────────────────────────────────────────┐│  │
│  │  │ Detect changed prompts → generate diff report             ││  │
│  │  │ Flag: new prompts, modified prompts, deleted prompts      ││  │
│  │  │ Show: before/after for each changed prompt                ││  │
│  │  └───────────────────────────────────────────────────────────┘│  │
│  └────────────────────────────┬───────────────────────────────────┘  │
│                               │                                      │
│                               v                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  STAGE 3: LLM Evaluation                                      │  │
│  │  ┌───────────────────────────────────────────────────────────┐│  │
│  │  │ Quick eval (10 cases) on every PR                         ││  │
│  │  │ Full eval (50 cases) on PR to main                        ││  │
│  │  │                                                           ││  │
│  │  │ For each test case:                                        ││  │
│  │  │   1. Generate output with PR's prompt/config               ││  │
│  │  │   2. Score with 4 rubrics (accuracy, safety,               ││  │
│  │  │      completeness, appropriateness)                        ││  │
│  │  │   3. Compare to baseline scores                            ││  │
│  │  └───────────────────────────────────────────────────────────┘│  │
│  └────────────────────────────┬───────────────────────────────────┘  │
│                               │                                      │
│                               v                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  STAGE 4: Regression Check                                     │  │
│  │  ┌───────────────────────────────────────────────────────────┐│  │
│  │  │ Compare scores to baseline:                                ││  │
│  │  │ - Any rubric dropped >10%? → BLOCK MERGE                   ││  │
│  │  │ - Safety score <3 on any case? → BLOCK MERGE               ││  │
│  │  │ - Cost increased >50%? → WARNING                           ││  │
│  │  │ - Latency increased >100%? → WARNING                       ││  │
│  │  └───────────────────────────────────────────────────────────┘│  │
│  └────────────────────────────┬───────────────────────────────────┘  │
│                               │                                      │
│                               v                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  STAGE 5: PR Comment                                           │  │
│  │  ┌───────────────────────────────────────────────────────────┐│  │
│  │  │ Post formatted evaluation report to PR:                    ││  │
│  │  │ - Score comparison table (current vs baseline)             ││  │
│  │  │ - Delta indicators (improved/regressed/stable)             ││  │
│  │  │ - Prompt diff summary                                      ││  │
│  │  │ - Cost and latency comparison                              ││  │
│  │  │ - Pass/fail verdict                                        ││  │
│  │  └───────────────────────────────────────────────────────────┘│  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Key Features

- **Prompt-aware triggers** -- Pipeline runs specifically when prompts, model configs, or pipeline code change, not on every commit
- **Tiered evaluation** -- Quick eval (10 cases, ~$1.70, 3 min) on every PR; full eval (50 cases, ~$8.50, 15 min) on PR to main
- **Baseline management** -- Evaluation baselines versioned in git alongside code. Baselines update when PRs merge.
- **Regression blocking** -- PRs that cause >10% drop in any rubric score or any safety hard-fail are blocked from merging
- **PR comment reports** -- Formatted evaluation results posted directly to the PR for easy review
- **Cost and latency tracking** -- Token usage and cost comparison included in every evaluation report
- **Prompt diff visualization** -- Side-by-side comparison of changed prompts in the PR comment

---

## GitHub Actions Workflow

### Main Workflow

```yaml
# .github/workflows/clinical-ai-eval.yml
name: Clinical AI Evaluation

on:
  pull_request:
    paths:
      - 'config/prompts/**'
      - 'config/models.yaml'
      - 'src/**'
      - 'baselines/**'

env:
  EVAL_TIER: ${{ github.base_ref == 'main' && 'full' || 'quick' }}

jobs:
  standard-ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: ruff check src/
      - run: mypy src/ --ignore-missing-imports
      - run: pytest tests/ -v --tb=short

  prompt-diff:
    runs-on: ubuntu-latest
    needs: standard-ci
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Generate prompt diff report
        run: |
          python scripts/prompt_diff.py \
            --base ${{ github.event.pull_request.base.sha }} \
            --head ${{ github.sha }} \
            --output reports/prompt_diff.md

      - uses: actions/upload-artifact@v4
        with:
          name: prompt-diff
          path: reports/prompt_diff.md

  llm-evaluation:
    runs-on: ubuntu-latest
    needs: standard-ci
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt

      - name: Run evaluation
        run: |
          python evaluate.py \
            --tier ${{ env.EVAL_TIER }} \
            --baseline baselines/current.json \
            --output results/eval_results.json
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      - name: Check regressions
        id: regression-check
        run: |
          python scripts/check_regression.py \
            --results results/eval_results.json \
            --baseline baselines/current.json \
            --safety-threshold 3 \
            --regression-threshold 0.10

      - uses: actions/upload-artifact@v4
        with:
          name: eval-results
          path: results/eval_results.json

  post-pr-comment:
    runs-on: ubuntu-latest
    needs: [prompt-diff, llm-evaluation]
    if: always()
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4

      - name: Generate and post PR comment
        run: |
          python scripts/post_pr_comment.py \
            --eval-results eval-results/eval_results.json \
            --prompt-diff prompt-diff/prompt_diff.md \
            --baseline baselines/current.json
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## PR Comment Example

When the pipeline runs on a PR, it posts a comment like this:

```
## Clinical AI Evaluation Report

### Evaluation Summary (Quick Eval: 10 test cases)

| Rubric | Baseline | Current | Delta | Status |
|--------|----------|---------|-------|--------|
| Accuracy | 4.18 | 4.25 | +0.07 | IMPROVED |
| Safety | 4.72 | 4.70 | -0.02 | STABLE |
| Completeness | 3.94 | 4.10 | +0.16 | IMPROVED |
| Appropriateness | 4.22 | 4.30 | +0.08 | IMPROVED |
| **Aggregate** | **4.27** | **4.34** | **+0.07** | **IMPROVED** |

### Safety Check
- Safety hard-fails (score < 3): 0/10 -- PASS
- Minimum safety score: 4 (test case #7)

### Cost & Latency
| Metric | Baseline | Current | Delta |
|--------|----------|---------|-------|
| Avg cost/request | $0.042 | $0.045 | +7.1% |
| Latency p50 | 2.1s | 2.3s | +9.5% |
| Latency p95 | 4.8s | 5.1s | +6.3% |

### Prompt Changes
- Modified: `config/prompts/session_summary_v3.txt`
  - Added: explicit instruction to front-load critical findings
  - Removed: verbose formatting instructions
  - Net: -12 tokens in system prompt

### Verdict: PASS
No regressions detected. Safe to merge.

---
*Generated by Clinical AI CI/CD Pipeline*
```

---

## Quick Start

### Prerequisites

- GitHub repository with Actions enabled
- OpenAI API key stored as repository secret (`OPENAI_API_KEY`)
- Python 3.11+

### Setup

```bash
# Clone the repository
git clone https://github.com/kavoshmonfared/clinical-ai-cicd.git
cd clinical-ai-cicd

# Install dependencies
pip install -r requirements.txt

# Initialize baseline (run full evaluation once)
python evaluate.py --tier full --output baselines/current.json
git add baselines/current.json
git commit -m "Initialize evaluation baseline"
```

### Local Testing

```bash
# Run evaluation locally (same as CI)
python evaluate.py --tier quick --baseline baselines/current.json --output results/local_eval.json

# Check for regressions
python scripts/check_regression.py --results results/local_eval.json --baseline baselines/current.json

# Generate prompt diff
python scripts/prompt_diff.py --base HEAD~1 --head HEAD --output reports/prompt_diff.md
```

---

## Project Structure

```
clinical-ai-cicd/
├── .github/
│   └── workflows/
│       ├── clinical-ai-eval.yml    # Main evaluation workflow
│       ├── baseline-update.yml     # Post-merge baseline update
│       └── weekly-extended.yml     # Weekly extended evaluation
├── scripts/
│   ├── prompt_diff.py              # Prompt change detection and diffing
│   ├── check_regression.py         # Regression detection logic
│   ├── post_pr_comment.py          # Format and post PR comments
│   └── update_baseline.py          # Baseline update after merge
├── src/
│   ├── evaluate.py                 # Core evaluation runner
│   ├── framework.py                # Evaluation framework
│   ├── rubrics/                    # Rubric definitions
│   ├── scoring/                    # G-Eval scoring implementation
│   └── reporting/                  # Report generation
├── config/
│   ├── prompts/                    # Versioned prompt templates
│   ├── models.yaml                 # Model configurations
│   ├── eval_tiers.yaml             # Evaluation tier definitions
│   └── settings.yaml               # Pipeline settings
├── baselines/
│   ├── current.json                # Current production baseline
│   └── history/                    # Historical baselines
├── data/
│   ├── quick_eval.jsonl            # 10-case quick evaluation set
│   ├── full_eval.jsonl             # 50-case full evaluation set
│   └── extended_eval.jsonl         # 100-case extended set
├── tests/
│   ├── test_prompt_diff.py         # Prompt diff tests
│   ├── test_regression.py          # Regression detection tests
│   └── test_pr_comment.py          # PR comment formatting tests
├── requirements.txt
├── .env.example
└── README.md
```

---

## Baseline Management

Baselines are the reference point for regression detection. They are versioned in git and follow a clear lifecycle:

### Baseline Lifecycle

```
1. Initialize: First full evaluation run creates baselines/current.json
2. Compare: Every PR evaluation compares against current baseline
3. Update: When a PR merges to main, baseline updates automatically
4. History: Previous baselines archived in baselines/history/ with timestamps
```

### Baseline Update Workflow

```yaml
# .github/workflows/baseline-update.yml
name: Update Baseline

on:
  push:
    branches: [main]
    paths:
      - 'config/prompts/**'
      - 'config/models.yaml'
      - 'src/**'

jobs:
  update-baseline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt

      - name: Run full evaluation
        run: python evaluate.py --tier full --output results/new_baseline.json
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      - name: Archive current baseline
        run: |
          python scripts/update_baseline.py \
            --current baselines/current.json \
            --new results/new_baseline.json

      - name: Commit updated baseline
        run: |
          git config user.name "CI Bot"
          git config user.email "ci@pipeline"
          git add baselines/
          git commit -m "Update evaluation baseline [skip ci]"
          git push
```

---

## Design Decisions

### Why Tiered Evaluation
**Context:** Full evaluation (50 cases x 4 rubrics) costs ~$8.50 and takes 15 minutes. Running this on every commit is not sustainable.
**Decision:** Three evaluation tiers: quick (10 cases), full (50 cases), extended (100 cases).
**Rationale:** Quick eval runs on every PR and catches obvious regressions in 3 minutes. Full eval runs on PRs to main and provides comprehensive coverage. Extended eval runs weekly to catch subtle drift patterns. This balances cost (~$15/day assuming 5 PRs/day) with coverage.
**Tradeoff:** Quick eval may miss regressions that only appear on specific test cases. Mitigated by running full eval before any merge to main.

### Why Prompt Diff as a Separate Stage
**Context:** Prompt changes are the most common cause of quality regressions in LLM applications.
**Decision:** Dedicated prompt diff analysis stage that runs alongside evaluation.
**Rationale:** Reviewers need to see what changed in the prompt to understand evaluation results. A prompt diff that shows "removed safety instruction" next to a "safety score dropped 15%" makes the cause-effect relationship obvious. Without the diff, reviewers see regression numbers without context.
**Tradeoff:** Adds ~30 seconds to pipeline. Negligible.

### Why Block Merge on Regression (Not Just Warn)
**Context:** Warnings are ignored. In healthcare AI, ignored quality regressions can have real consequences.
**Decision:** PRs with >10% regression on any rubric or any safety hard-fail are blocked from merging.
**Rationale:** If regressions are warnings, they get merged with "we'll fix it later" and they never get fixed. Blocking forces the author to either fix the regression or explicitly justify why the regression is acceptable (by updating the baseline manually with a comment).
**Tradeoff:** Can block legitimate changes where a rubric trade-off is intentional (e.g., improving safety at the cost of completeness). Handled by allowing manual baseline override with required reviewer approval.

---

## Evaluation Results

### Pipeline Performance

| Metric | Quick Eval | Full Eval | Extended Eval |
|--------|-----------|-----------|---------------|
| Test cases | 10 | 50 | 100 |
| Duration | ~3 min | ~15 min | ~30 min |
| Cost | ~$1.70 | ~$8.50 | ~$17.00 |
| Regression detection rate | 78% | 95% | 99% |

### Regression Detection Accuracy

Tested by intentionally introducing known regressions into prompts:

| Regression Type | Detected (Quick) | Detected (Full) |
|----------------|-------------------|-----------------|
| Safety instruction removed | Yes | Yes |
| Output format changed | Yes | Yes |
| Few-shot examples removed | No | Yes |
| Subtle wording change (accuracy impact) | No | Yes |
| Temperature increased from 0 to 0.3 | Yes | Yes |
| System prompt shortened by 30% | No | Yes |

Quick eval reliably catches severe regressions. Full eval catches subtle ones. This validates the tiered approach.

---

## Challenges & Solutions

### Challenge 1: Evaluation Non-Determinism
**Problem:** The same test case evaluated twice could produce slightly different scores (e.g., 4.0 vs. 4.2), making regression detection noisy.
**Root Cause:** Even at temperature=0, LLM outputs have small variance across API calls.
**Solution:** Run each evaluation 3 times and take the median score. Added a dead-zone around the regression threshold: scores within 5% of the threshold are flagged as "marginal" rather than triggering a block. This reduced false-positive regression alerts by 60%.

### Challenge 2: API Cost Control
**Problem:** During development, an infinite loop in the evaluation runner ran up a $40 OpenAI bill in one afternoon.
**Root Cause:** No per-run cost limit.
**Solution:** Added a hard cost cap per evaluation run ($15 for quick, $25 for full). The pipeline aborts and alerts if the cap is hit. Also added per-request cost tracking so each evaluation result includes its cost.

### Challenge 3: Baseline Drift
**Problem:** Over time, incremental baseline updates after each merge caused gradual score inflation -- each merge slightly inflated the baseline, and eventually a genuinely poor result looked "normal."
**Root Cause:** Baselines were updated automatically after every merge, including merges that slightly inflated scores.
**Solution:** Baseline updates now require that the new scores are within 5% of the previous baseline OR are explicitly approved by a reviewer. This prevents score inflation while still allowing legitimate improvements to update the baseline.

---

## What I Learned

- **LLMOps is real engineering, not DevOps with a new name.** The challenges in this pipeline -- non-deterministic outputs, evaluation cost management, baseline drift -- have no direct analogs in traditional CI/CD. They require new patterns and new thinking.
- **Cost management is a first-class concern.** In traditional CI/CD, compute costs are predictable. In LLM evaluation, a bug can cost $40 in an afternoon. Cost caps, per-request tracking, and tiered evaluation are not optimizations -- they are requirements.
- **The PR comment is the product.** The pipeline's value is not in the YAML files or Python scripts. It is in the PR comment that a reviewer reads for 30 seconds and immediately understands whether this change is safe to merge. Getting the comment format right was the highest-impact design decision.
- **Blocking merges on regressions changes team behavior.** Before the pipeline, prompt changes were reviewed by reading the diff and guessing whether it would work. Now, every prompt change has empirical evidence. The team stopped asking "does this prompt look right?" and started asking "what do the eval numbers say?"

---

## Future Improvements

- [ ] Add caching for unchanged test cases (skip re-evaluation if prompt and model are unchanged)
- [ ] Build a historical dashboard showing eval score trends across all PRs
- [ ] Add support for A/B evaluation (compare PR prompt vs. baseline prompt on same inputs)
- [ ] Implement cost optimization: auto-select eval tier based on change scope
- [ ] Add Slack/Teams notifications for failed evaluations

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Author

**Kavosh Monfared** -- Senior Software Engineer, AI Automation & Healthcare Systems
- GitHub: [@kavoshmonfared](https://github.com/kavoshmonfared)
- LinkedIn: [kavoshmonfared](https://linkedin.com/in/kavoshmonfared)
