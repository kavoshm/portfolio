"""
Generate portfolio visualization figures.

Outputs:
    docs/images/portfolio_overview.png   - Diagram of all portfolio pieces and connections
    docs/images/skills_matrix.png        - Heatmap of skills demonstrated across portfolio
    docs/images/project_timeline.png     - Timeline of portfolio piece creation

Usage:
    python scripts/generate_figures.py
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# --- Theme ---
BG_COLOR = "#1a1a2e"
COLORS = ["#4f7cac", "#5a9e8f", "#9b6b9e", "#c47e3a", "#b85450"]
TEXT_COLOR = "#e0e0e0"
GRID_COLOR = "#2a2a4e"
ACCENT_LIGHT = "#6a9cc7"

plt.rcParams.update({
    "figure.facecolor": BG_COLOR,
    "axes.facecolor": BG_COLOR,
    "axes.edgecolor": GRID_COLOR,
    "axes.labelcolor": TEXT_COLOR,
    "text.color": TEXT_COLOR,
    "xtick.color": TEXT_COLOR,
    "ytick.color": TEXT_COLOR,
    "grid.color": GRID_COLOR,
    "font.family": "sans-serif",
    "font.size": 11,
})

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def draw_portfolio_overview():
    """Diagram showing all portfolio pieces and how they connect."""
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis("off")
    fig.suptitle("Portfolio Overview: How All Pieces Connect",
                 fontsize=16, fontweight="bold", color=TEXT_COLOR, y=0.96)

    def draw_box(x, y, w, h, label, color, sublabel=""):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15",
                             facecolor=color, edgecolor="white", linewidth=1.2, alpha=0.85)
        ax.add_patch(box)
        ax.text(x + w / 2, y + h / 2 + (0.12 if sublabel else 0), label,
                ha="center", va="center", fontsize=9, fontweight="bold", color="white")
        if sublabel:
            ax.text(x + w / 2, y + h / 2 - 0.18, sublabel,
                    ha="center", va="center", fontsize=7, color="#d0d0d0", style="italic")

    # Center title box
    draw_box(4.5, 7.5, 5, 0.9, "AI Automation Portfolio", COLORS[0], "Kavosh Monfared")

    # 5 Project repos (row 1)
    projects = [
        ("Clinical Note\nClassifier", "Phase 1: Prompts"),
        ("Mental Health\nRAG System", "Phase 2: RAG"),
        ("Clinical Eval\nFramework", "Phase 3: Eval"),
        ("Agentic Intake\nPipeline", "Phase 4: Agents"),
        ("Clinical AI\nCI/CD", "Phase 5: LLMOps"),
    ]
    for i, (name, phase) in enumerate(projects):
        x = 0.3 + i * 2.7
        draw_box(x, 5.0, 2.4, 1.2, name, COLORS[i % len(COLORS)], phase)
        # Arrow from title to project
        ax.annotate("", xy=(x + 1.2, 6.2), xytext=(7, 7.5),
                    arrowprops=dict(arrowstyle="->", color=ACCENT_LIGHT, lw=0.8, alpha=0.4))

    # Blog Post
    draw_box(1.0, 2.8, 3.0, 1.0, "Blog Post", COLORS[3],
             "LLM-as-Judge in Healthcare")
    # Arrow from eval framework to blog
    ax.annotate("", xy=(2.5, 3.8), xytext=(6.0, 5.0),
                arrowprops=dict(arrowstyle="->", color=COLORS[3], lw=1.5, alpha=0.7))

    # Certificates
    draw_box(5.5, 2.8, 3.0, 1.0, "Certificates", COLORS[1],
             "LLMOps + Advanced RAG")
    # Arrows from certs to relevant projects
    ax.annotate("", xy=(7.0, 3.8), xytext=(6.0, 5.0),
                arrowprops=dict(arrowstyle="->", color=COLORS[1], lw=1.2, alpha=0.5))
    ax.annotate("", xy=(7.0, 3.8), xytext=(11.6, 5.0),
                arrowprops=dict(arrowstyle="->", color=COLORS[1], lw=1.2, alpha=0.5))

    # GitHub Profile
    draw_box(10.0, 2.8, 3.0, 1.0, "GitHub Profile\nREADME", COLORS[4],
             "Links all projects")
    # Arrow from profile to all projects
    for i in range(5):
        x = 0.3 + i * 2.7 + 1.2
        ax.annotate("", xy=(x, 5.0), xytext=(11.5, 3.8),
                    arrowprops=dict(arrowstyle="->", color=COLORS[4], lw=0.8, alpha=0.3))

    # Bottom legend
    draw_box(2.0, 0.8, 4.0, 0.8, "5 Project READMEs", COLORS[0], "Polished, portfolio-ready")
    draw_box(7.5, 0.8, 4.5, 0.8, "Interview Prep", COLORS[2],
             "Resume claims + technical depth")

    # Connecting line
    ax.annotate("", xy=(6.0, 1.2), xytext=(7.5, 1.2),
                arrowprops=dict(arrowstyle="<->", color=ACCENT_LIGHT, lw=1.2))

    fig.savefig(os.path.join(OUTPUT_DIR, "portfolio_overview.png"),
                dpi=150, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)
    print("Generated: portfolio_overview.png")


def draw_skills_matrix():
    """Heatmap of skills demonstrated across portfolio pieces."""
    skills = ["Coding", "Evaluation", "Architecture", "Writing", "Operations"]
    pieces = [
        "Clinical Note\nClassifier",
        "Mental Health\nRAG",
        "Clinical Eval\nFramework",
        "Agentic Intake\nPipeline",
        "Clinical AI\nCI/CD",
        "Blog Post",
        "Certificates",
        "GitHub Profile",
    ]

    # Skill intensity matrix (0-10 scale)
    data = np.array([
        # Coding  Eval  Arch  Writing  Ops
        [9,       3,    6,    7,       2],   # Classifier
        [9,       5,    8,    7,       3],   # RAG
        [8,       10,   7,    7,       6],   # Eval Framework
        [9,       5,    9,    6,       4],   # Agentic Pipeline
        [7,       8,    6,    5,       10],  # CI/CD
        [2,       7,    3,    10,      2],   # Blog Post
        [3,       6,    4,    8,       7],   # Certificates
        [1,       3,    2,    10,      1],   # GitHub Profile
    ])

    fig, ax = plt.subplots(figsize=(10, 7))

    # Custom colormap using theme colors
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("portfolio",
        [BG_COLOR, COLORS[0], COLORS[1], "#e8c547"], N=256)

    im = ax.imshow(data, cmap=cmap, aspect="auto", vmin=0, vmax=10)

    ax.set_xticks(range(len(skills)))
    ax.set_xticklabels(skills, fontsize=11, fontweight="bold")
    ax.set_yticks(range(len(pieces)))
    ax.set_yticklabels(pieces, fontsize=10)

    # Add value text in each cell
    for i in range(len(pieces)):
        for j in range(len(skills)):
            val = data[i, j]
            text_c = "white" if val > 5 else "#aaaaaa"
            ax.text(j, i, str(val), ha="center", va="center",
                    fontsize=12, fontweight="bold", color=text_c)

    cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.02)
    cbar.set_label("Skill Intensity (0-10)", color=TEXT_COLOR)
    cbar.ax.yaxis.set_tick_params(color=TEXT_COLOR)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TEXT_COLOR)

    ax.set_title("Skills Demonstrated Across Portfolio Pieces",
                 fontsize=14, fontweight="bold", pad=15)

    ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)
    ax.spines[:].set_visible(False)

    fig.savefig(os.path.join(OUTPUT_DIR, "skills_matrix.png"),
                dpi=150, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)
    print("Generated: skills_matrix.png")


def draw_project_timeline():
    """Timeline showing when each portfolio piece was created."""
    fig, ax = plt.subplots(figsize=(14, 6))

    phases = [
        {"label": "Phase 1\nPrompt Engineering", "start": 0, "end": 2, "color": COLORS[0],
         "project": "Clinical Note Classifier"},
        {"label": "Phase 2\nRAG Pipelines", "start": 2, "end": 4, "color": COLORS[1],
         "project": "Mental Health RAG System"},
        {"label": "Phase 3\nEvaluation", "start": 4, "end": 6.5, "color": COLORS[2],
         "project": "Clinical Eval Framework"},
        {"label": "Phase 4\nAgentic Systems", "start": 6.5, "end": 8.5, "color": COLORS[3],
         "project": "Agentic Intake Pipeline"},
        {"label": "Phase 5\nLLMOps", "start": 8.5, "end": 10.5, "color": COLORS[4],
         "project": "Clinical AI CI/CD"},
        {"label": "Phase 6\nPortfolio", "start": 10.5, "end": 12, "color": COLORS[0],
         "project": "Blog + READMEs + Certs"},
    ]

    # Certificate bars
    certs = [
        {"label": "LLMOps Certificate", "start": 8, "end": 9.5, "color": COLORS[1]},
        {"label": "RAG Certificate", "start": 3, "end": 4.5, "color": COLORS[1]},
    ]

    # Draw main timeline
    ax.axhline(y=2, color=ACCENT_LIGHT, linewidth=2, alpha=0.3, zorder=0)

    # Draw phase bars
    for i, phase in enumerate(phases):
        bar = FancyBboxPatch(
            (phase["start"], 1.4), phase["end"] - phase["start"], 1.2,
            boxstyle="round,pad=0.1", facecolor=phase["color"],
            edgecolor="white", linewidth=1, alpha=0.85, zorder=2
        )
        ax.add_patch(bar)
        mid = (phase["start"] + phase["end"]) / 2
        ax.text(mid, 2.35, phase["label"], ha="center", va="center",
                fontsize=8, fontweight="bold", color="white", zorder=3)
        ax.text(mid, 1.7, phase["project"], ha="center", va="center",
                fontsize=7, color="#d0d0d0", style="italic", zorder=3)

    # Draw certificate markers
    for cert in certs:
        bar = FancyBboxPatch(
            (cert["start"], 0.3), cert["end"] - cert["start"], 0.7,
            boxstyle="round,pad=0.08", facecolor=cert["color"],
            edgecolor="white", linewidth=0.8, alpha=0.6, zorder=2
        )
        ax.add_patch(bar)
        mid = (cert["start"] + cert["end"]) / 2
        ax.text(mid, 0.65, cert["label"], ha="center", va="center",
                fontsize=7, fontweight="bold", color="white", zorder=3)

    # Labels
    ax.text(-0.5, 2, "Projects", ha="right", va="center",
            fontsize=10, fontweight="bold", color=TEXT_COLOR)
    ax.text(-0.5, 0.65, "Certificates", ha="right", va="center",
            fontsize=10, fontweight="bold", color=TEXT_COLOR)

    # Month markers
    months = ["Month 1-2", "Month 3-4", "Month 5-6", "Month 7-8",
              "Month 9-10", "Month 11-12"]
    for i, label in enumerate(months):
        x = i * 2 + 1
        ax.text(x, 3.3, label, ha="center", va="center",
                fontsize=8, color="#888888")
        ax.axvline(x=i * 2, color=GRID_COLOR, linewidth=0.5, alpha=0.3, zorder=0)

    ax.set_xlim(-1.5, 12.5)
    ax.set_ylim(-0.2, 3.8)
    ax.axis("off")
    ax.set_title("Portfolio Development Timeline",
                 fontsize=14, fontweight="bold", pad=15)

    fig.savefig(os.path.join(OUTPUT_DIR, "project_timeline.png"),
                dpi=150, bbox_inches="tight", facecolor=BG_COLOR)
    plt.close(fig)
    print("Generated: project_timeline.png")


if __name__ == "__main__":
    print("Generating portfolio figures...")
    draw_portfolio_overview()
    draw_skills_matrix()
    draw_project_timeline()
    print(f"All figures saved to: {OUTPUT_DIR}")
