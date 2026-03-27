# Raw Notes for Blog Post

## Topic Selection Reasoning
- Evaluation is the most undervalued skill in AI engineering
- The incident: 3-word prompt change, 15% accuracy drop, 3 days undetected
- Target audience: AI engineers building LLM apps in regulated domains
- Differentiator: practical experience, not theoretical framework

## Key Points to Cover
- Why reference-based metrics (BLEU, ROUGE) fail for clinical text
- G-Eval mechanism: rubric + CoT + probability weighting
- The four rubrics and how they evolved from six
- Calibration as the hardest problem (score distribution from 0.3 to 0.64 std dev)
- Inter-model agreement data (Safety 94%, Appropriateness 78%)
- Clinical abbreviation edge case ("SOB")
- Honest failures: 6-rubric system, single-pass scoring, engineering-driven rubrics
- Practical cost: $8.50 per full eval run, 15 minutes

## Publishing Strategy
- Primary: Medium / personal blog, cross-post Dev.to
- Timing: Tuesday/Wednesday morning
- Social: LinkedIn same day, Twitter/X 2 days later
- Tags: LLM evaluation, healthcare AI, G-Eval, LLM-as-judge, clinical NLP

## Tone Guidelines
- Practitioner-to-practitioner
- Specific numbers and concrete examples
- Honest about failures
- Not academic, not promotional
