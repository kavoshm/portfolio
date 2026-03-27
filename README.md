# AI Engineering Portfolio

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

A complete portfolio for an AI/ML engineering career in healthcare technology. Contains five polished project READMEs, a technical blog post, certificate study materials, a GitHub profile README, and supporting artifacts -- all connected to demonstrate a coherent narrative of an experienced software engineer who systematically learned AI engineering and applied it to real clinical problems.

This is not a collection of tutorials. Every artifact here was built to solve a real healthcare problem: evaluating LLM-generated clinical text, extracting structured data from unstructured notes, building retrieval systems for treatment protocols, and automating quality assurance for AI deployments.

---

## Portfolio Overview

![Portfolio Overview](docs/images/portfolio_overview.png)

The portfolio tells a coherent story across five projects, a blog post, two certificates, and a GitHub profile. Each piece builds on the previous, progressing from prompt engineering fundamentals through RAG, evaluation, agentic systems, and LLMOps to a complete production-ready skill set.

---

## Skills Demonstrated

![Skills Matrix](docs/images/skills_matrix.png)

The skills matrix shows how each portfolio piece contributes to the overall narrative. The Clinical Eval Framework (flagship project) scores highest on evaluation. The Agentic Intake Pipeline leads on architecture. The blog post and GitHub profile carry the writing dimension. The CI/CD pipeline dominates operations.

---

## Development Timeline

![Project Timeline](docs/images/project_timeline.png)

Each phase builds on the previous. Certificates were completed alongside the projects they informed: the RAG certificate during Phase 2 (RAG Pipelines), and the LLMOps certificate during Phase 5 (CI/CD).

---

## Portfolio Artifacts

### Projects (5 Repos)

| # | Project | What It Does | Key Tech | README |
|---|---------|-------------|----------|--------|
| 1 | [Clinical Note Classifier](https://github.com/kavoshmonfared/clinical-note-classifier) | LLM-powered triage classification with CoT reasoning | Few-shot, structured output | [README](readmes/project1_clinical_note_classifier.md) |
| 2 | [Mental Health RAG](https://github.com/kavoshmonfared/mental-health-rag) | RAG system for clinical treatment protocols | ChromaDB, MMR, FastAPI | [README](readmes/project2_mental_health_rag.md) |
| 3 | [Clinical Eval Framework](https://github.com/kavoshmonfared/clinical-eval-framework) | Automated quality scoring with 4 clinical rubrics | G-Eval, GPT-4-as-judge | [README](readmes/project3_clinical_eval_framework.md) |
| 4 | [Agentic Intake Pipeline](https://github.com/kavoshmonfared/agentic-intake-pipeline) | Multi-agent extraction to FHIR R4 resources | LangGraph, FHIR R4 | [README](readmes/project4_agentic_intake_pipeline.md) |
| 5 | [Clinical AI CI/CD](https://github.com/kavoshmonfared/clinical-ai-cicd) | CI/CD with automated eval and regression blocking | GitHub Actions, eval automation | [README](readmes/project5_clinical_ai_cicd.md) |

### Blog Post

| Artifact | Description | Location |
|----------|------------|----------|
| Full Post | "Why LLM-as-Judge Works Differently in Healthcare" (~1,100 words) | [blog/post.md](blog/post.md) |
| Outline | Section-by-section plan with key arguments | [blog/outline.md](blog/outline.md) |
| Social Posts | LinkedIn (x2) + Twitter/X promotional posts | [blog/social_posts.md](blog/social_posts.md) |

### Certificates

| Certificate | Provider | Key Skills | Materials |
|------------|---------|------------|-----------|
| LLMOps | DeepLearning.AI | Versioning, evaluation, deployment, monitoring, cost | [Study Notes](certificates/llmops-cert/study_notes.md) + [Questions](certificates/llmops-cert/practice_questions.md) |
| Advanced RAG | DeepLearning.AI | Sentence-window, auto-merging, RAG triad, reranking | [Study Notes](certificates/rag-cert/study_notes.md) + [Questions](certificates/rag-cert/practice_questions.md) |

### GitHub Profile

The [GitHub Profile README](readmes/github_profile_readme.md) serves as the front door to the entire portfolio, linking all five projects with descriptions and a tech stack overview.

### README Template

A [reusable template](readmes/templates/project_readme_template.md) for writing portfolio-quality AI project READMEs. Includes sections for architecture, design decisions, evaluation results, and honest reflections.

---

## Project Structure

```
19-portfolio/
├── blog/                              # Technical blog post
│   ├── post.md                        #   Published blog post
│   ├── outline.md                     #   Section-by-section outline
│   └── social_posts.md                #   LinkedIn + Twitter promotional posts
├── readmes/                           # Project READMEs
│   ├── project1_clinical_note_classifier.md
│   ├── project2_mental_health_rag.md
│   ├── project3_clinical_eval_framework.md
│   ├── project4_agentic_intake_pipeline.md
│   ├── project5_clinical_ai_cicd.md
│   ├── github_profile_readme.md       #   GitHub profile README
│   └── templates/
│       └── project_readme_template.md #   Reusable template
├── certificates/                      # Certificate study materials
│   ├── llmops-cert/
│   │   ├── study_notes.md
│   │   └── practice_questions.md
│   └── rag-cert/
│       ├── study_notes.md
│       └── practice_questions.md
├── inputs/                            # Raw inputs and notes
│   ├── blog_outline_raw_notes.md
│   └── blog_post_outline.md
├── outputs/                           # Published version tracking
│   ├── published_blog_post.md
│   ├── published_readmes.md
│   └── certificate_summaries.md
├── scripts/
│   └── generate_figures.py            # Generates all visualizations
├── docs/
│   └── images/
│       ├── portfolio_overview.png     # Portfolio piece connections
│       ├── skills_matrix.png          # Skills heatmap
│       └── project_timeline.png       # Development timeline
├── .gitignore
├── LICENSE
├── requirements.txt
└── README.md
```

---

## Generating Figures

```bash
pip install -r requirements.txt
python scripts/generate_figures.py
```

This generates three PNG files in `docs/images/`:
- `portfolio_overview.png` -- Diagram of all portfolio pieces and how they connect
- `skills_matrix.png` -- Heatmap of skills demonstrated across portfolio pieces
- `project_timeline.png` -- Timeline showing when each portfolio piece was created

---

## How the Pieces Connect

The portfolio is designed to tell a coherent story:

1. **Phase 1 (Prompt Engineering)** -- Clinical Note Classifier demonstrates that careful prompt engineering, without fine-tuning, achieves reliable clinical text classification.

2. **Phase 2 (RAG)** -- Mental Health RAG System shows domain-specific retrieval optimization for clinical protocols, informed by the Advanced RAG certificate.

3. **Phase 3 (Evaluation)** -- Clinical Eval Framework (the flagship project) demonstrates that evaluation is a first-class engineering concern, not an afterthought. The blog post is a deep dive into the evaluation methodology.

4. **Phase 4 (Agentic Systems)** -- Agentic Intake Pipeline demonstrates multi-agent architecture with LangGraph, FHIR R4 integration, and human-in-the-loop design.

5. **Phase 5 (LLMOps)** -- Clinical AI CI/CD brings all the evaluation concepts into a production pipeline, informed by the LLMOps certificate.

6. **Phase 6 (Portfolio)** -- This repo packages everything into a presentable, interconnected body of work.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Author

**Kavosh Monfared** -- Senior Software Engineer, AI Automation & Healthcare Systems
- GitHub: [@kavoshmonfared](https://github.com/kavoshmonfared)
- LinkedIn: [kavoshmonfared](https://linkedin.com/in/kavoshmonfared)
