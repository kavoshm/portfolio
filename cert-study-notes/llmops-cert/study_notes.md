# LLMOps Certificate -- Comprehensive Study Notes

## 1. LLM Pipeline Versioning

### Why Versioning Is Different for LLM Applications

Traditional software versioning tracks code changes. LLM applications have three additional
axes of change that must be versioned:

1. **Prompt templates** -- A single word change in a system prompt can shift output behavior
   dramatically. Prompts must be versioned with the same rigor as code.
2. **Model configurations** -- Model name, temperature, max_tokens, top_p, and other
   parameters all affect output. A "minor" parameter change can cause a major behavior shift.
3. **Chain architecture** -- The order of operations, retrieval configuration, tool definitions,
   and agent graph structure all affect the pipeline's behavior.

### What to Version

| Artifact | How to Version | Why |
|----------|---------------|-----|
| Prompt templates | Git, with dedicated directory (`config/prompts/`) | Track every change, enable diff and rollback |
| Model parameters | YAML config file in git | Reproducibility; pin model versions for audit |
| Chain configuration | Code + config files | Architecture changes are deployment-impacting |
| Evaluation baselines | JSON in git alongside code | Baselines are the quality benchmark; they must evolve with the code |
| Test datasets | Versioned data files (git LFS for large sets) | Test set changes affect evaluation results |

### Configuration-as-Code Pattern

```yaml
# config/pipeline.yaml
model:
  provider: openai
  name: gpt-4-0613           # Pin specific model version
  temperature: 0
  max_tokens: 1000

prompts:
  system: config/prompts/session_summary_v3.txt
  few_shot: config/prompts/few_shot_examples_v2.json

retrieval:
  embedding_model: text-embedding-ada-002
  chunk_size: 500
  chunk_overlap: 100
  top_k: 5

evaluation:
  baseline: baselines/current.json
  rubrics: [accuracy, safety, completeness, appropriateness]
  judge_model: gpt-4
```

Every field in this configuration is a potential source of behavior change. Version the
entire file in git. When debugging a production issue, you need to know the exact
configuration that produced the problematic output.

### Schema Versioning for Structured Outputs

When the output schema changes (e.g., adding a new field to the clinical extraction output),
you need:
- Backward compatibility: old consumers still work with new outputs
- Forward compatibility: new consumers handle old outputs gracefully
- Version tag in every output: `{"schema_version": "2.1", ...}`

In healthcare, schema changes are especially sensitive because downstream systems (EHR,
reporting, billing) depend on exact field structures. A schema change without versioning
can break integrations silently.

### Reproducibility Requirements

For any past output, you should be able to reconstruct the exact conditions that produced it:
- Which prompt template was used
- Which model and parameters
- What input was provided
- What context was retrieved (for RAG)
- What tools were called (for agents)

In regulated healthcare environments, this is not a best practice -- it is a compliance
requirement. Audit trails must connect outputs to their exact pipeline configuration.

---

## 2. Automated Evaluation in Production

### The Testing Pyramid for LLM Applications

Traditional software has a testing pyramid: many unit tests, fewer integration tests, few
end-to-end tests. LLM applications need a different pyramid:

```
           /\
          /  \  Human evaluation (periodic, expensive, gold standard)
         /    \
        /------\  LLM-as-judge evaluation (every deployment)
       /        \
      /----------\  Stochastic tests (semantic similarity, consistency)
     /            \
    /--------------\  Deterministic tests (schema, format, length, required fields)
   /________________\
```

### Deterministic Tests (Run on Every Commit)

Fast, cheap, binary pass/fail:
- **Schema validation:** Output is valid JSON and matches expected schema
- **Format compliance:** Required fields present, types correct
- **Length bounds:** Output within expected token/word count range
- **Required content:** Expected patterns present (e.g., ICD-10 code format)
- **Forbidden content:** No hallucinated patterns, no treatment recommendations in
  summarization tasks (scope violation)
- **Idempotency:** Same input + same config = same output (at temperature=0)

### Stochastic Tests (Run on PR to Main)

Probabilistic, require statistical reasoning:
- **Rubric-based scoring:** LLM-as-judge rates output quality against explicit criteria
- **Semantic similarity:** Output meaning matches reference (cosine similarity > threshold)
- **Factual accuracy:** Key entities correctly extracted (F1 score)
- **Consistency:** Multiple runs produce similar outputs (low variance)
- **Regression testing:** Scores compared to versioned baseline

### Handling Non-Determinism in Evaluation

LLM outputs are non-deterministic even at temperature=0 (due to model serving infrastructure).
Evaluation must account for this:

1. **Run multiple times:** Evaluate each test case 3-5x, take median score
2. **Use confidence intervals:** Report score ranges, not single numbers
3. **Dead-zone around thresholds:** Scores within 5% of regression threshold are "marginal,"
   not automatic failures
4. **Trend analysis:** Single-point regressions may be noise; persistent trends are real

### Evaluation as a CI/CD Quality Gate

The evaluation pipeline is the quality gate for AI deployments:
- Quick evaluation (10 test cases) runs on every PR
- Full evaluation (50 test cases) runs on PR to main
- Extended evaluation (100 test cases) runs weekly
- Any safety hard-fail blocks the deployment
- Any rubric regression >10% blocks the deployment

### Test Set Management

Test sets are versioned data, not throwaway fixtures:
- Curated by domain experts (in healthcare: clinicians)
- Stratified across use cases, complexity levels, and edge cases
- Updated when new failure modes are discovered
- Never leaked into training data or few-shot examples

---

## 3. Deployment Strategies for LLM Applications

### Blue-Green Deployment

Two identical environments running side-by-side:
- **Blue (current production):** Serves all traffic
- **Green (new version):** Deployed and tested in isolation
- **Switch:** After Green passes evaluation, traffic switches from Blue to Green
- **Rollback:** If issues emerge, switch back to Blue (seconds)

**Healthcare consideration:** Both environments must have identical compliance posture --
same data access controls, same audit logging, same encryption. A "test" environment that
bypasses compliance is not a valid test.

### Canary Releases

Gradual traffic shifting:
1. Deploy new version alongside production
2. Route 5% of traffic to new version
3. Monitor quality metrics for canary cohort
4. If stable, increase to 25%, 50%, 100%
5. If quality drops, roll back immediately

**Healthcare consideration:** Canary cohorts must not receive systematically different care.
Random assignment is essential. Document the canary strategy in compliance records.

### Shadow Mode

Zero-risk evaluation of new versions:
1. New version runs in parallel with production
2. Both receive the same inputs
3. Only production results are served to users
4. Shadow results are logged for offline comparison
5. When shadow consistently matches or beats production, switch

**Healthcare consideration:** This is the safest pattern for initial deployment of clinical
AI features. No patient impact during evaluation. Use this for all first-time deployments.

### Feature Flags for LLM Features

Wrap LLM features behind feature flags:
- Enable per-user, per-organization, or percentage-based
- Instant disable without redeployment
- Track which flag configuration was active for each request
- Essential for controlled rollout and quick response to issues

### Rollback Strategies (Fastest to Slowest)

| Strategy | Time | When to Use |
|----------|------|-------------|
| Feature flag toggle | Seconds | Disable a specific LLM feature |
| Prompt rollback | Seconds | Revert to previous prompt version (config-as-code) |
| Blue-green switch | Minutes | Revert entire service to previous version |
| Version rollback | Minutes-hours | Redeploy previous version from artifact registry |

### Healthcare-Specific Deployment Concerns

- **Audit trail continuity:** During deployment transitions, audit trail must be continuous.
  No gap between old and new version logging.
- **Data in flight:** Requests that started on version A must complete on version A. Do not
  switch mid-request.
- **Compliance documentation:** Every deployment must be documented: what changed, who
  approved it, what evaluation was performed, what the results were.

---

## 4. Monitoring and Observability

### Metrics Categories

#### Operational Metrics
- **Latency:** p50, p95, p99 per endpoint and per model. Healthcare workflows have strict
  time budgets -- a clinical summarization that takes 30 seconds is unusable in a busy clinic.
- **Throughput:** Requests/second, concurrent connections. Capacity planning for peak hours.
- **Error rate:** API errors, timeouts, rate limit hits, parsing failures.
- **Token usage:** Input tokens, output tokens, total per request. Correlates with cost.

#### Quality Metrics
- **Evaluation scores:** Rolling average of rubric scores from automated evaluation. This is
  the most important metric -- it directly measures output quality.
- **Hallucination rate:** Percentage of outputs flagged as containing hallucinated content.
  In healthcare, this is a safety metric.
- **Refusal rate:** Percentage of requests where the model declines to answer. Unusually
  high refusal rates indicate prompt or guardrail issues.
- **User correction rate:** How often clinicians edit or override AI outputs. High correction
  rates signal quality problems.

#### Cost Metrics
- **Cost per request:** Based on token counts and model pricing.
- **Daily/weekly spend:** Budget tracking with alerting on spikes.
- **Cost per task type:** Summarization vs. classification vs. extraction. Different tasks
  have different cost profiles.
- **Cost per model:** Same task across GPT-4, GPT-3.5, and local models.

### Alerting Rules

| Alert | Condition | Severity | Response |
|-------|-----------|----------|----------|
| Latency spike | p95 > 2x baseline for 5 min | Warning | Check model provider status |
| Error rate spike | > 5% for 3 min | Critical | Investigate and potentially rollback |
| Cost spike | Daily cost > 2x average | Warning | Check for infinite loops or prompt bloat |
| Quality drop | Rolling eval score < threshold | Critical | Halt deployments, investigate |
| Safety alert | Any safety hard-fail in production | Critical | Immediate investigation |
| Token anomaly | Avg tokens > 3x baseline | Warning | Check for prompt injection or input bloat |
| Rate limit | > 3 rate limit errors in 1 min | Warning | Implement backoff or upgrade tier |

### Observability Stack

- **Tracing:** LangSmith or Langfuse for LLM-specific tracing. Every chain execution, tool
  call, and retrieval step is traceable.
- **Metrics:** Prometheus + Grafana or Datadog for operational metrics.
- **Logging:** Structured JSON logs with request IDs and trace IDs. Never log PHI.
- **Dashboards:** Real-time dashboards for quality, cost, and latency.

### Feedback Loops

Production monitoring is not just about alerting -- it feeds back into improvement:
1. Collect user corrections (clinician edits to AI outputs)
2. Analyze correction patterns to identify systematic failures
3. Add problematic cases to evaluation test set
4. Update few-shot examples based on correction patterns
5. Track improvement over time through evaluation scores

---

## 5. Cost Management

### Understanding LLM Cost Structure

LLM costs are driven by token volume:
- **Input tokens:** System prompt + user input + retrieved context (for RAG)
- **Output tokens:** Model's generated response (typically 2-4x more expensive than input)
- **Hidden costs:** Evaluation runs (judge model calls), embedding generation, re-ranking

### Cost Optimization Strategies

#### Model Tiering
Not every task needs GPT-4:
- **Simple classification:** GPT-3.5-turbo (~20x cheaper than GPT-4)
- **Complex reasoning:** GPT-4 (higher quality, higher cost)
- **Embeddings:** text-embedding-ada-002 or text-embedding-3-small (cheap)
- **Local models:** Ollama/Llama for non-sensitive, high-volume tasks (zero API cost)

#### Prompt Optimization
- **Remove redundant instructions:** Every token in the system prompt is paid for on every request
- **Optimize few-shot examples:** Use the minimum number that maintains quality
- **Structured output reduces output tokens:** JSON schema constraints produce shorter responses

#### Caching
- **Semantic caching:** Cache responses for semantically similar queries
- **Exact caching:** Cache responses for identical inputs (common in batch processing)
- **Embedding caching:** Cache embeddings for documents that do not change

#### Batch Processing
- **Batch API:** OpenAI's batch API offers 50% discount for non-real-time workloads
- **Evaluation batching:** Group evaluation runs rather than running ad-hoc

### Cost Tracking Implementation

```python
# Per-request cost tracking
class CostTracker:
    PRICING = {
        "gpt-4": {"input": 0.03/1000, "output": 0.06/1000},
        "gpt-3.5-turbo": {"input": 0.001/1000, "output": 0.002/1000},
    }

    def track(self, model, input_tokens, output_tokens):
        cost = (input_tokens * self.PRICING[model]["input"] +
                output_tokens * self.PRICING[model]["output"])
        self.log(model=model, input_tokens=input_tokens,
                 output_tokens=output_tokens, cost=cost)
        return cost
```

### Budget Management

- Set daily and weekly cost budgets per environment
- Alert at 80% of budget consumed
- Hard cap at 100% -- pipeline stops accepting requests
- Separate budgets for production, evaluation, and development
- Monthly cost review with model selection reassessment

---

## Key Takeaways

1. **LLMOps is not MLOps with a new name.** LLM applications have unique challenges:
   non-deterministic outputs, prompt sensitivity, high inference costs, and evaluation
   complexity. These require new patterns, not just adapted ML practices.

2. **Evaluation is the backbone of LLMOps.** Without automated evaluation, you cannot
   confidently deploy, you cannot detect regressions, and you cannot compare alternatives.
   Evaluation infrastructure should be built before the production pipeline.

3. **Healthcare adds a compliance layer to every LLMOps decision.** Versioning is not
   just for reproducibility -- it is for audit trails. Monitoring is not just for
   performance -- it is for patient safety. Deployment is not just about uptime -- it is
   about care continuity.

4. **Cost management is a first-class engineering concern.** An unmonitored LLM pipeline
   can generate surprising bills. Cost tracking, budgets, and model tiering are required
   from day one, not optimizations for later.

5. **The CI/CD pipeline is the most underrated AI artifact.** A well-built evaluation
   pipeline that runs on every PR changes how teams ship AI features. It moves the
   conversation from "does this prompt look right?" to "what do the numbers say?"
