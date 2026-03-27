# Why LLM-as-Judge Works Differently in Healthcare: Lessons from Building Clinical Evaluation Pipelines

Last year, a colleague changed three words in a system prompt for our clinical summarization pipeline. The code review looked fine. The output format was unchanged. But three days later, a clinician mentioned that the summaries "felt off." When we ran the numbers, accuracy scores had dropped 15% and two test cases failed our safety rubric. Three words. Three days of degraded clinical output that nobody caught.

That incident is why I spent the next several months building an automated evaluation framework for LLM-generated clinical outputs. This post shares what I learned -- specifically, why LLM-as-Judge evaluation works in healthcare but requires fundamentally different rubrics, calibration, and failure handling than general-purpose evaluation.

## The Problem with Manual Review

Before the framework, our evaluation process was clinician spot-checks. A psychiatrist would review maybe 5% of generated session summaries, give informal feedback ("looks good" or "this missed the medication change"), and move on. There was no baseline, no tracking, no systematic coverage.

This fails in three predictable ways. First, 5% sampling misses regressions that affect specific output types. A prompt change that degraded triage narratives but not session summaries would go unnoticed because the reviewer happened to check summaries that week. Second, informal feedback has no threshold -- "looks okay" is not a deployable quality metric. Third, clinician time is expensive and unscalable. We could not ask a psychiatrist to review 50 outputs every time we changed a prompt.

We needed automated evaluation. But standard approaches -- BLEU, ROUGE, BERTScore -- measure token overlap with a reference answer, and clinical summarization has no single correct answer. Two summaries can use entirely different wording and both be clinically sound. Reference-based metrics would penalize correct outputs that phrased things differently from the reference.

## Enter LLM-as-Judge

G-Eval solves this by using an LLM as an evaluator instead of comparing against a reference text. You define evaluation criteria in a rubric, then a judge model (GPT-4 in our case) reads the original clinical note, the generated output, and the rubric criteria, then scores the output on each dimension.

The mechanism: the judge receives a detailed rubric with scoring criteria for each level (1 through 5), generates chain-of-thought reasoning about the output's quality, and then assigns a score. We extract token-level probabilities for the score and compute an expected value rather than taking a single discrete score. This probability weighting was critical -- it spread our score distribution from a standard deviation of 0.3 (everything clustered around 4.0) to 0.64 (meaningful differentiation between good and mediocre outputs).

Reference-free evaluation is what makes this work for clinical text. Instead of asking "does this match the reference?", we ask "does this meet the criteria?" Multiple valid outputs all score well, while outputs that hallucinate, omit critical information, or use inappropriate language score poorly.

## Four Rubrics That Actually Work

The rubrics are the intellectual core of the framework. Getting them right took longer than building the evaluation infrastructure itself.

**Accuracy** (1-5): Does the output faithfully represent the clinical information in the source note? This checks for hallucinated findings, incorrect medical facts, and fabricated details. A summary that says "patient was prescribed amoxicillin" when the note says "azithromycin" scores low on accuracy, regardless of how well-written the rest is.

**Safety** (1-5, hard-fail below 3): Does the output avoid potentially harmful content? Missing a critical drug interaction, providing false reassurance about a dangerous symptom, or omitting a risk flag like suicidal ideation are all safety failures. This rubric has a hard-fail rule: any test case scoring below 3 blocks the deployment. No exceptions, no "we'll fix it in the next release." In healthcare, safety regressions are non-negotiable.

**Completeness** (1-5): Does the output cover all clinically relevant information? Key findings, diagnoses, medications, and follow-up plans should all be present. Completeness is weighted by clinical significance -- omitting the primary diagnosis is worse than omitting a minor historical detail.

**Clinical Appropriateness** (1-5): Would a clinician trust this document? Correct terminology, appropriate tone, concise structure. This is the most subjective rubric, and it was the one I got wrong the first time.

These four rubrics were not my first design. I originally had six, including separate rubrics for "Formatting" and "Readability." In practice, evaluators (both LLM and human) could not reliably distinguish between them. Cohen's kappa between the two rubrics was 0.45 -- barely better than chance. Collapsing them into "Clinical Appropriateness" improved inter-rater reliability significantly.

## What Surprised Me

**Calibration is the hardest problem.** Initial G-Eval scores, using only brief rubric descriptions ("Rate accuracy from 1 to 5"), clustered around 4.0-4.5 for everything. A well-written summary and a mediocre one both scored 4.2. The fix was detailed per-level criteria: explicit descriptions of what a 3 looks like versus a 4 versus a 5, with clinical examples at each level. Combined with chain-of-thought reasoning (forcing the judge to explain before scoring) and probability weighting, the score distribution became meaningful.

**Inter-model agreement varies by rubric.** When we ran the same test cases through both GPT-4 and GPT-3.5-turbo as judges, they agreed on Safety 94% of the time but agreed on Clinical Appropriateness only 78% of the time. Safety is relatively objective -- did the output miss a dangerous finding or not? Appropriateness is subjective -- is the tone "clinical enough"? This tells us which rubrics we can trust from automated evaluation and which need periodic human calibration.

**Clinical abbreviations confuse the judge.** "SOB" means shortness of breath in a clinical note. The judge model occasionally interpreted it differently and flagged the output as inappropriate. We added a pre-processing normalization step for common clinical abbreviations before passing outputs to the judge.

## What Failed and Why

Honest accounting: several things did not work.

The original six-rubric system was too granular. Not only did "Formatting" and "Readability" overlap, but evaluators showed fatigue on long rubric sets. Score quality degraded on rubrics 5 and 6 compared to rubrics 1 and 2. Fewer rubrics with clearer criteria produced more reliable scores.

Single-pass scoring was unreliable. A test case that scored 4.0 on one run could score 3.0 on the next, even at temperature=0. Non-determinism in LLM outputs affects evaluation too. We now run every evaluation three times and take the median. This triples cost but eliminates flaky quality gates -- a test that randomly passes and fails is worse than no test at all.

The Clinical Appropriateness rubric, as I originally wrote it, measured things engineers care about (structure, formatting, completeness of sections) rather than things clinicians care about (conciseness, front-loading of critical findings, clinical voice). After reviewing it with two psychiatrists, the rubric was substantially rewritten. This was humbling but necessary. Building clinical evaluation rubrics is a collaboration, not a solo engineering task.

## Practical Advice

Five recommendations from building this system:

1. **Start with 3-4 rubrics, not 10.** Fewer rubrics with clear, detailed criteria beat many rubrics with vague ones. You can always add rubrics later.

2. **Make Safety a hard-fail gate.** If any test case fails the safety rubric, the deployment is blocked. Not warned. Blocked. In healthcare, safety regressions cannot be averaged away by strong scores on other rubrics.

3. **Invest heavily in rubric calibration.** "1 = poor, 5 = excellent" produces useless scores. "3 = one factual error that could cause confusion but not harm; 4 = minor inaccuracies that would not affect clinical decisions" produces meaningful scores. This calibration work is tedious and it is the most important part of the framework.

4. **Build baseline management from day one.** A score of 4.18 is meaningless in isolation. It has meaning only relative to a baseline (was it 4.02 last week?) and a trend (has it been declining for three sprints?).

5. **Budget for evaluation cost.** A full evaluation run -- 50 test cases across 4 rubrics -- costs about $8.50 and takes 15 minutes. This is real money and real time. If you do not budget for it explicitly, the team will skip it when deadlines get tight, which is exactly when regressions are most likely.

## Closing Thought

The industry overinvests in generation and underinvests in evaluation. Everyone is building RAG pipelines and agentic systems. Very few are building the evaluation infrastructure to know whether those systems actually work. In healthcare, that gap is not just bad engineering -- it is a patient safety problem.

Evaluation is not glamorous work. It does not demo well. Nobody posts "I built an evaluation framework" on social media. But it is the difference between a prototype that impresses in a demo and a system that is safe to deploy in a clinic. If you are building LLM features without automated evaluation, start with one rubric and 10 test cases. It is easier than you think to start, harder than you think to get right, and more valuable than you think once it is running.

---

*Kavosh Monfared is a Senior Software Engineer specializing in AI automation and healthcare systems at AIMedic. He builds evaluation frameworks, agentic pipelines, and LLMOps infrastructure for clinical AI applications. Find him on [GitHub](https://github.com/kavoshmonfared) and [LinkedIn](https://linkedin.com/in/kavoshmonfared).*
