# 6-2: LLMOps Certificate

## Certificate Details

**Course:** LLMOps -- Large Language Model Operations
**Provider:** DeepLearning.AI (Coursera)
**Completed:** 2024
**Instructor:** Errol Koolmeister (Google Cloud)

## What This Certificate Covers

This course covers the operational lifecycle of LLM-powered applications -- from development
and testing through deployment, monitoring, and ongoing maintenance. It bridges the gap
between building a working LLM prototype and running it reliably in production.

The focus areas are directly applicable to healthcare AI, where production reliability is
not optional: pipeline versioning ensures reproducibility for audit trails, automated
evaluation catches quality regressions before they reach clinicians, and monitoring
detects drift in output quality over time.

## Key Skills Demonstrated

- **Pipeline Versioning** -- Tracking prompt versions, model configurations, and chain
  architectures as code artifacts. Every change is reproducible and auditable.
- **Automated Evaluation** -- Building evaluation pipelines that run on every deployment,
  using both deterministic checks (schema validation, format compliance) and stochastic
  tests (rubric-based scoring, LLM-as-judge).
- **Deployment Strategies** -- Blue-green deployments, canary releases, and feature flags
  for LLM features. Shadow mode for zero-risk initial rollout.
- **Monitoring and Observability** -- Latency tracking, cost monitoring, output quality
  drift detection, and alerting on anomalous patterns.
- **Cost Management** -- Per-request cost tracking, budget alerting, and model selection
  optimization based on cost-quality tradeoffs.

## How This Applies to My Work

At AIMedic, this knowledge directly shaped:
- The prompt management and versioning system I built for production AI features
- The regression testing harness that runs on every deployment
- The monitoring dashboards tracking output quality, latency, and cost
- The decision framework for model selection across healthcare-specific tasks

## Files in This Module

| File | Description |
|------|-------------|
| `study_notes.md` | Comprehensive study notes covering all LLMOps topics |
| `practice_questions.md` | 15 practice questions with detailed answers |

## Connection to Other Phases

This certificate provides the operational foundation for:
- **Phase 5 (LLMOps):** Direct application of concepts in the CI/CD pipeline project
- **Phase 3 (Evaluation):** Automated evaluation is the quality backbone of LLMOps
- **Phase 6 (Portfolio):** The CI/CD project README (Project 5) showcases these skills
