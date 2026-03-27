# LLMOps Certificate -- Practice Questions

15 practice questions covering core LLMOps concepts with detailed answers.

---

## Question 1: Pipeline Versioning

**Q: Your team deploys a prompt change that causes a 15% drop in output accuracy, but nobody
notices for 3 days. What versioning and monitoring practices would have caught this earlier?**

**A:** Three practices would have prevented this:

First, the prompt change should have been versioned in git and triggered an automated
evaluation pipeline before deployment. If the evaluation suite had run with the new prompt
against the existing baseline, the 15% regression would have been detected and the
deployment blocked.

Second, production monitoring should track rolling evaluation scores. Even without
pre-deployment evaluation, a real-time quality dashboard that samples and scores production
outputs would have detected the drop within hours, not days.

Third, the deployment should have used a canary release pattern -- routing 5-10% of traffic
to the new prompt and comparing quality metrics before full rollout. The regression would
have been visible in the canary cohort before affecting all users.

The root cause is treating prompt changes as informal edits rather than code-level changes
with the same review, testing, and deployment rigor.

---

## Question 2: Evaluation Strategy

**Q: You are building an LLM-powered clinical summarization tool. Design a three-tier
evaluation strategy for this application.**

**A:** Tier 1 (every commit): Deterministic tests that run in seconds. Schema validation --
does the output parse as valid JSON with required fields (patient_id, summary_text,
diagnoses, medications)? Format checks -- is the summary under 500 words? Are ICD-10 codes
in valid format? These catch obvious regressions from code or prompt changes.

Tier 2 (every PR to main): Rubric-based evaluation using LLM-as-judge on 50 test cases.
Score against four rubrics: accuracy (does the summary reflect the source note?), safety
(no harmful omissions or fabrications?), completeness (all key clinical findings included?),
and clinical appropriateness (reads like a clinical document?). Compare scores to versioned
baseline. Block merge if any rubric drops >10% or any safety score falls below threshold.

Tier 3 (weekly): Extended evaluation on 100 test cases including edge cases -- very long notes,
notes with conflicting information, multi-system presentations, notes in abbreviated clinical
shorthand. Also includes inter-model agreement analysis (run the same test cases through
GPT-4 and GPT-3.5 as judges, check for scoring divergence). This tier catches subtle drift
that smaller test sets miss.

---

## Question 3: Deployment Strategy

**Q: You are deploying a new LLM feature that generates discharge note drafts for a hospital.
This is the first time AI-generated content will appear in patient records. What deployment
strategy do you recommend and why?**

**A:** Shadow mode first, then canary release, then full deployment.

Phase 1 (Shadow mode, 2-4 weeks): Run the LLM pipeline in parallel with the existing manual
process. Clinicians write discharge notes as usual. The LLM generates a parallel draft that
is logged but never shown to users. Compare LLM drafts to clinician-written notes offline.
This provides zero-risk evaluation data and calibrates expectations.

Phase 2 (Canary with explicit opt-in, 2-4 weeks): Offer the LLM draft as a "suggested draft"
to a small group of volunteering clinicians (5-10). They can use it as a starting point and
edit as needed. Track acceptance rate, edit distance, and time savings. Collect feedback.

Phase 3 (Gradual rollout with feature flag, 4+ weeks): Expand to 25%, 50%, 100% of clinicians,
controlled by feature flag. Monitor quality metrics, clinician correction rate, and user
satisfaction continuously. Keep the feature flag for instant rollback.

The key principle: for a first-time clinical AI deployment, err heavily on the side of caution.
Shadow mode costs time but eliminates patient-impact risk during initial evaluation.

---

## Question 4: Monitoring

**Q: What are the five most critical metrics to monitor for an LLM-powered clinical triage
system, and what alerting thresholds would you set?**

**A:** The five critical metrics:

1. **Safety score (rolling average from automated evaluation):** Alert at < 4.5/5.0. For
   triage, safety is the primary concern -- a missed high-acuity patient is unacceptable.
   This is the most important metric.

2. **Latency p95:** Alert at > 5 seconds. Triage decisions must be fast. If the system takes
   longer than the time a nurse would take to read the note, it slows down the workflow
   rather than helping it.

3. **Error rate:** Alert at > 2%. In a clinical workflow, system errors mean fallback to
   manual triage. Frequent errors undermine clinician trust, and once trust is lost it is
   very hard to regain.

4. **High-acuity recall:** Alert if any known high-acuity test case is misclassified in
   production monitoring. Missing a critical patient is the worst failure mode. This metric
   should have near-zero tolerance.

5. **Cost per classification:** Alert at > 2x baseline. Cost spikes often indicate unexpected
   input patterns (very long notes, prompt injection attempts) or model behavior changes.

---

## Question 5: Cost Management

**Q: Your LLM application costs $500/day using GPT-4. Leadership asks you to reduce costs
by 60% without significantly degrading quality. How do you approach this?**

**A:** Step 1: Analyze cost distribution by task type. Not all tasks need GPT-4. If 70% of
requests are simple classifications and 30% are complex summarizations, the simple tasks
likely work fine with GPT-3.5-turbo at 1/20th the cost.

Step 2: Implement model tiering. Route simple tasks (classification, schema validation,
format extraction) to GPT-3.5-turbo. Keep GPT-4 for complex tasks (clinical summarization,
multi-step reasoning, safety-critical outputs). Evaluate both models on your test suite to
find the quality threshold where GPT-3.5 is acceptable.

Step 3: Optimize prompts for token efficiency. Remove redundant instructions, shorten
few-shot examples, reduce system prompt length. Every token saved on the system prompt
saves money on every single request.

Step 4: Implement caching. If the same clinical protocol is queried repeatedly (common in
RAG systems), cache the response. Semantic caching can catch paraphrased queries too.

Step 5: Measure the impact. Run the full evaluation suite after each optimization to ensure
quality stays above threshold. Document the cost-quality tradeoff for each change.

Expected result: model tiering alone typically saves 40-50%. Combined with prompt
optimization and caching, 60% reduction is achievable while maintaining quality on the
tasks that matter most.

---

## Question 6: Non-Determinism

**Q: You run the same evaluation suite twice with identical inputs and get different scores
(4.18 vs. 4.25). How do you handle this non-determinism in a CI/CD quality gate?**

**A:** LLM non-determinism is inherent even at temperature=0 due to model serving
infrastructure (floating-point arithmetic, batching, load balancing across GPU clusters).
You cannot eliminate it, but you can account for it.

First, run each test case 3 times and take the median score. This reduces the impact of
outlier runs. Second, establish a dead-zone around the regression threshold. If the
threshold is 10% regression, scores within 5% of the threshold are flagged as "marginal"
and require manual review rather than automatic pass/fail. Third, track score variance
over time. If variance exceeds a threshold (e.g., standard deviation > 0.3 for a 1-5
scale), investigate whether the model or evaluation setup has changed.

For the specific case of 4.18 vs. 4.25 -- this is 1.7% variance, which is within normal
range for LLM evaluation. Both runs should produce the same pass/fail decision. If they
do not (because they straddle the regression threshold), the threshold needs a wider
dead-zone.

---

## Question 7: Prompt Management

**Q: Describe a prompt management system that supports versioning, rollback, review, and
audit trails for a healthcare AI application.**

**A:** The system has four components:

1. **Storage:** Prompts stored as text files in a git repository under `config/prompts/`.
   Each prompt file is named with its purpose and version: `session_summary_v3.txt`. Git
   provides versioning, diff, and rollback natively.

2. **Review:** Prompt changes go through the same pull request process as code. The PR
   triggers an automated evaluation that compares the new prompt's scores against the
   baseline. Reviewers see both the prompt diff and the evaluation results.

3. **Deployment:** Prompts are deployed through the CI/CD pipeline, not edited in production.
   The application reads prompt templates from config files, not hardcoded strings. Rollback
   is a config change, not a code deployment.

4. **Audit trail:** Every prompt version is tagged with a git commit hash, author, timestamp,
   and the evaluation results at the time of deployment. For healthcare compliance, you can
   reconstruct which exact prompt was used for any past output.

The key principle: prompts are code. They go through the same lifecycle -- version control,
review, testing, deployment, monitoring -- as any other production artifact.

---

## Question 8: Regression Testing

**Q: Your evaluation baseline was set 3 months ago. Since then, 15 PRs have merged, each
passing the regression check. But clinician feedback indicates quality has gradually
declined. What went wrong?**

**A:** This is baseline drift. Each PR made a small change that passed the 10% regression
threshold individually, but the cumulative effect of 15 small regressions degraded quality
significantly. If each PR caused a 1-2% regression on one rubric, the cumulative effect
after 15 PRs could be 15-30% degradation -- well above the threshold, but never caught
because each individual change was below it.

Solutions: First, periodically compare current evaluation scores to a fixed historical
baseline (not just the rolling baseline). If scores have drifted 15% from the original
baseline, flag it even if no individual PR caused a large regression. Second, implement
a ratcheting baseline: the baseline only moves in the direction of improvement. If a PR
causes any regression (even small), the baseline stays at the previous level. This prevents
gradual drift. Third, schedule regular human evaluation (monthly or quarterly) to calibrate
automated scores against clinician judgment. Automated evaluation can drift as well.

---

## Question 9: Model Selection

**Q: You are evaluating GPT-4, GPT-3.5-turbo, and a locally deployed Llama-3-8B for a
clinical note summarization task. What evaluation framework would you use to compare
them?**

**A:** Run all three models on the same evaluation test suite (50 clinical notes across
diverse categories). Score each model's outputs using the same rubrics (accuracy, safety,
completeness, appropriateness) with the same judge model (GPT-4).

Generate a comparison report with:
- Per-rubric mean scores for each model
- Per-rubric score distributions (not just means -- a model with high mean but high variance
  is less reliable)
- Cost per request for each model
- Latency (p50, p95) for each model
- Safety hard-fail rate for each model
- Failure mode analysis: what types of notes does each model struggle with?

The decision framework weights these factors based on the use case. For clinical
summarization: safety > accuracy > completeness > appropriateness > cost > latency.
A model that is cheaper but has lower safety scores is not acceptable. A model that is
slightly less accurate but 20x cheaper might be acceptable for non-critical use cases.

Present the comparison as a decision matrix, not a single "winner." Different tasks may
warrant different model selections.

---

## Question 10: Observability

**Q: A clinician reports that the AI-generated session summary for a specific patient
"made things up." How do you use observability tooling to investigate?**

**A:** Step 1: Get the request ID from the clinician or from application logs (timestamp +
user ID to look up the specific request). Step 2: Pull the full trace from the tracing
system (LangSmith/Langfuse). This shows: the exact input note, the full prompt (system +
input + few-shot examples), the model and parameters used, the raw model output, and any
post-processing applied.

Step 3: Check the input. Was the original clinical note complete, or was it truncated
(context window overflow)? Step 4: Check the prompt. Was the correct prompt version used?
Were few-shot examples appropriate? Step 5: Check the output. Identify the specific
hallucinated content. Is it plausible text that could come from the model's training data
rather than the input note?

Step 6: Reproduce. Send the same input through the same pipeline configuration. Does the
hallucination recur? If yes, it is a systematic prompt issue. If no, it may be a
non-determinism artifact. Step 7: Add this case to the evaluation test set so future
regressions on similar inputs are caught.

---

## Question 11: Compliance and Audit

**Q: A regulatory auditor asks you to prove that the AI system used in clinical workflows
has been consistently evaluated and that no quality regressions were deployed to production.
What evidence do you provide?**

**A:** Four pieces of evidence:

1. **Evaluation history:** Every PR that modified prompts, models, or pipeline code triggered
   an automated evaluation. The evaluation results are stored as JSON artifacts in the CI/CD
   system, timestamped and linked to the specific git commit. Provide the full evaluation
   history showing pass/fail results for every deployment.

2. **Baseline versioning:** Evaluation baselines are versioned in git with full history.
   Show the auditor the baseline progression over time, demonstrating that quality thresholds
   were maintained or improved.

3. **Deployment logs:** Every deployment is logged with: what changed (prompt diff, model
   change, code change), who approved it (PR reviewer), what evaluation was performed (linked
   evaluation results), and what the outcome was (pass/fail).

4. **Production monitoring data:** Dashboards showing rolling quality scores, safety metrics,
   and alert history. Any triggered alerts and their resolution are documented.

This evidence demonstrates a continuous quality assurance process, not just point-in-time
testing.

---

## Question 12: Feature Flags for LLM Features

**Q: You are rolling out an LLM-powered medication interaction checker. Describe how you
would use feature flags to manage the rollout safely.**

**A:** Define three feature flag states: OFF (feature disabled, manual checking only), SHADOW
(LLM runs but results not shown to users, logged for comparison), and ON (LLM results
displayed to clinicians as decision support).

Rollout sequence:
1. Deploy with flag=SHADOW for all users. Run for 2 weeks. Compare LLM interaction checks
   against pharmacist-verified checks. Calculate accuracy and false-negative rate.
2. If shadow results meet quality thresholds: flag=ON for 5% of pharmacists (opt-in group).
   Monitor for 2 weeks. Track user acceptance, edit rate, and time savings.
3. Gradual expansion: 25% -> 50% -> 100% over 4 weeks, monitoring at each stage.
4. Keep the feature flag active permanently. If a model update causes quality issues, toggle
   flag to SHADOW (continue logging, stop showing) rather than removing entirely.

Critical: the feature flag must be tracked in the audit trail. For every medication
interaction check, log whether the LLM was in SHADOW or ON mode. This is essential for
post-hoc analysis if an adverse event is investigated.

---

## Question 13: Testing Non-Deterministic Outputs

**Q: How do you write meaningful tests for a system whose outputs are inherently
non-deterministic?**

**A:** Separate tests into deterministic and stochastic categories, and apply appropriate
techniques to each.

For deterministic properties (which exist even in non-deterministic systems): test output
schema compliance (always valid JSON, always has required fields), test boundary behavior
(empty input returns error, not hallucination), test safety guardrails (adversarial inputs
do not produce harmful outputs). These are binary pass/fail and should pass on every run.

For stochastic properties: define acceptable ranges rather than exact values. Instead of
"accuracy = 4.2," test "accuracy > 3.8 AND accuracy < 5.0." Run multiple times (3-5) and
test the median. Use statistical tests (e.g., paired t-test) when comparing two versions --
is the difference statistically significant or just noise? Set explicit variance budgets:
if the standard deviation across 5 runs exceeds 0.3 on a 1-5 scale, the test is
inconclusive and needs more runs.

The critical principle: flaky tests are worse than no tests. If a test randomly passes
and fails, teams ignore it. Design tests to be reliable even for non-deterministic systems.

---

## Question 14: Scaling LLM Applications

**Q: Your LLM application handles 100 requests/day. Leadership wants to scale to 10,000
requests/day. What operational changes are needed?**

**A:** Five areas need scaling consideration:

1. **Rate limits and concurrency:** At 10,000 requests/day (~7/minute), you will hit
   default API rate limits. Request rate limit increases from the provider. Implement
   request queuing with priority levels (urgent clinical requests first). Add retry logic
   with exponential backoff for rate limit errors.

2. **Cost:** 100x volume = 100x cost. Implement model tiering (route simple requests to
   cheaper models). Add caching (many clinical queries repeat). Optimize prompts for token
   efficiency. Budget: if 100 requests/day costs $50, 10,000 will cost $5,000/day before
   optimization.

3. **Evaluation at scale:** You cannot evaluate every request. Implement sampling-based
   monitoring: evaluate a random 1-5% of production requests continuously. Alert on
   quality drops in the sample.

4. **Infrastructure:** Move from single-instance to load-balanced multi-instance. Add
   request queuing (Redis/SQS). Implement circuit breakers for provider outages. Consider
   local model deployment (Ollama) for latency-sensitive or high-volume tasks.

5. **Monitoring:** At 100 requests/day, you can review individual outputs. At 10,000,
   you need dashboards, automated alerting, and statistical quality monitoring. Build
   these before scaling, not after.

---

## Question 15: Incident Response for AI Systems

**Q: At 2 AM, your monitoring system alerts that the clinical summarization system's safety
score has dropped below the critical threshold for the last 30 minutes. Walk through your
incident response process.**

**A:** Immediate (first 5 minutes): Acknowledge the alert. Toggle the feature flag to
disable AI-generated summaries and fall back to manual process. This is the clinical AI
equivalent of "stop the bleeding" -- no more potentially unsafe outputs reach clinicians.

Investigation (next 30 minutes): Pull the monitoring data. How many outputs were generated
during the 30-minute window? What were the specific safety scores? Pull traces for the
lowest-scoring outputs and identify the failure pattern. Check: did the model provider
have an incident? Did a deployment happen recently? Did input patterns change (new data
source, different note format)?

Root cause analysis: Identify whether the issue is (a) a model provider issue (their
model behavior changed), (b) a deployment issue (recent prompt or config change), (c) a
data issue (new input patterns that the system does not handle), or (d) an evaluation issue
(the safety scoring itself broke).

Remediation: Fix the root cause. If it was a deployment issue, roll back. If it was a
model provider issue, switch to a fallback model. If it was a data issue, update prompts
or add input validation.

Restoration: Re-enable the feature flag. Run a full evaluation suite to confirm quality
is restored. Monitor closely for 24 hours.

Post-incident: Document the incident with timeline, root cause, impact (how many outputs
were affected, were any acted upon by clinicians), and preventive measures. Update alerting
thresholds if they were too slow. Add the failure case to the evaluation test set.
