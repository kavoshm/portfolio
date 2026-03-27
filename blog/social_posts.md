# Social Media Promotional Posts

## LinkedIn Post 1: Main Promotion (Publish Day)

---

**I spent months building an evaluation framework for clinical AI. Here's what I learned.**

Most teams building LLM applications skip systematic evaluation. In healthcare, that's a patient safety problem.

A three-word prompt change dropped our clinical summarization accuracy by 15%. Nobody noticed for 3 days. That's when I started building an automated evaluation framework using LLM-as-Judge.

Key lessons from the process:

-- LLM-as-Judge works for clinical text, but calibration is everything. Initial scores clustered around 4.0 regardless of actual quality. Detailed per-level rubric criteria + chain-of-thought scoring fixed this.

-- Safety needs a hard-fail gate. If any test case fails safety, the deployment is blocked. Not warned. Blocked. Safety regressions can't be averaged away by strong scores on other rubrics.

-- Rubric design is a collaboration, not a solo engineering task. My first attempt at a "Clinical Appropriateness" rubric measured what engineers care about. Clinicians care about different things. The rewrite was humbling.

-- Evaluation cost is real. ~$8.50 per full evaluation run. If you don't budget for it, the team will skip it when deadlines get tight -- exactly when regressions are most likely.

I wrote about the full experience: what worked, what failed, and 5 concrete recommendations.

[Link to blog post]

#HealthcareAI #LLMEvaluation #AIEngineering #ClinicalAI #LLMOps

---

## LinkedIn Post 2: Key Insight Angle (2 Days Later)

---

**The most undervalued skill in AI engineering isn't RAG or agents. It's evaluation.**

Everyone is building LLM pipelines. Very few are building the infrastructure to know whether those pipelines actually work.

In the past year, I built 5 AI projects for healthcare. The one that changed how my team ships code wasn't a RAG system or an agentic pipeline. It was the evaluation framework.

Before: clinician spot-checks on 5% of outputs, inconsistent feedback, no baseline.

After: automated evaluation on every PR, 4 clinical rubrics, regression detection, merge blocking on safety failures.

The result: prompt changes now have empirical evidence. The conversation shifted from "does this prompt look right?" to "what do the eval numbers say?"

If you're building LLM applications without automated evaluation, here's where to start:
1. Pick one rubric (accuracy or safety)
2. Write 10 test cases
3. Run evaluation on every PR that touches prompts

That's it. You can build from there.

[Link to blog post]

#AIQuality #LLMOps #SoftwareEngineering #HealthcareAI

---

## Twitter/X Post (2 Days After LinkedIn)

---

I built an eval framework for clinical LLM outputs. Biggest surprise:

Calibration > everything else.

"Rate accuracy 1-5" -> everything scores 4.0
Detailed per-level criteria + CoT + probability weighting -> scores actually differentiate quality

Same technique, dramatically different results. The rubric detail is the product.

Wrote about 4 rubrics that work for healthcare AI, what failed (6 rubrics collapsed to 4, engineering-driven rubrics that clinicians rewrote), and 5 practical recommendations.

[Link]

---
