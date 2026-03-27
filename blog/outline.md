# Blog Post Outline

## Title
"Why LLM-as-Judge Works Differently in Healthcare: Lessons from Building Clinical Evaluation Pipelines"

---

## Opening Hook (100 words)
- Start with a concrete scenario: a prompt change that looked fine in code review but dropped safety scores
- The problem: how do you systematically evaluate LLM outputs in a domain where wrong answers are dangerous?
- Thesis: LLM-as-Judge works in healthcare, but the rubrics, calibration, and failure modes are fundamentally different from general-purpose evaluation

## Section 1: The Problem with Manual Review (150 words)
- Key point: Ad-hoc clinician spot-checks do not scale and do not catch regressions
- Specifics: Clinicians reviewed ~5% of outputs, inconsistently, with no baseline
- Problem: A prompt change that degraded quality by 15% went unnoticed for 3 days
- Transition: We needed automated evaluation, but standard approaches did not work for clinical text

## Section 2: Enter LLM-as-Judge (150 words)
- Key point: G-Eval and reference-free evaluation solve the "no gold standard" problem
- Explain G-Eval briefly: LLM evaluates another LLM's output against explicit criteria
- Why reference-free matters: multiple valid summaries exist for the same clinical note
- How it works: rubric definition -> chain-of-thought scoring -> probability-weighted scores
- Transition: The technique works, but the rubrics are where the real work happens

## Section 3: Four Rubrics That Actually Work (200 words)
- Key point: Domain-specific rubrics are the core intellectual work of evaluation
- Accuracy: factual correctness relative to source note (not general medical knowledge)
- Safety: the hard-fail rubric. Below threshold = blocked deployment, no exceptions
- Completeness: did the output capture all clinically relevant information?
- Clinical Appropriateness: would a clinician trust this document?
- Concrete example: show how a single output scores differently across rubrics
- Key insight: these four rubrics were not my first attempt (originally had 6, collapsed to 4)

## Section 4: What Surprised Me (150 words)
- Calibration is the hardest problem: initial scores clustered at 4.0-4.5 regardless of actual quality
- Fix: detailed per-level criteria + chain-of-thought + probability weighting
- Inter-model agreement: GPT-4 and GPT-3.5 agree on safety (94%) but disagree on appropriateness (78%)
- Edge cases: clinical abbreviations ("SOB" = shortness of breath) confused the judge model
- Concrete number: G-Eval score spread improved from 0.3 standard deviation to 0.64 after calibration

## Section 5: What Failed and Why (150 words)
- Key point: Honest failures, not just successes
- Failure 1: Original 6-rubric system was too granular. Evaluators could not reliably distinguish between "Formatting" and "Readability." Collapsed to 4.
- Failure 2: Single-pass scoring was unreliable. A score of 4 on one run could be 3 on the next. Required 3x runs with median.
- Failure 3: The "Appropriateness" rubric was engineering-driven, not clinician-driven. Clinicians cared about conciseness and front-loading critical findings; my rubric measured different things.
- Key learning: Building rubrics requires clinical collaboration, not just engineering intuition

## Section 6: Practical Advice (150 words)
- 5 concrete recommendations:
  1. Start with 3-4 rubrics, not 10. Fewer rubrics with clear criteria beat many rubrics with vague ones.
  2. Make Safety a hard-fail gate. No exceptions.
  3. Invest in rubric calibration (detailed per-level criteria, not just "1 = bad, 5 = good").
  4. Build baseline management from day one. Scores are meaningless without baselines.
  5. Budget for evaluation cost. A full eval run costs $8-10 and takes 15 minutes. This is not free, and pretending it is leads to skipping it.

## Closing (100 words)
- Evaluation is the most undervalued skill in AI engineering
- In healthcare, it is also the most important
- The industry overinvests in generation and underinvests in evaluation
- The engineers who build reliable AI systems are the ones who take evaluation seriously
- Call to action: if you are building LLM features without automated evaluation, start with one rubric and 10 test cases. It is easier than you think to start, harder than you think to get right, and more valuable than you think once it is running.

## Author Bio
- Name, title, brief background
- Link to GitHub portfolio
- Link to LinkedIn
