# Bioinformatics & Vocabulary Hub 🧬📚

Welcome to the multi-project repository containing two distinct systems: JargonQuest and oncofind.

## Repository Projects

This repository is organized into two primary applications:

### 1. [oncofind](./oncofind/) 🔬 (Python Computational Pipeline)
An end-to-end command-line bioinformatics pipeline for pan-cancer biomarker discovery.
- **Core Functionality**: Downloads real transcriptomic (RNA-seq) and clinical metadata from NIH Genomic Data Commons (GDC) API, runs differential gene expression (DEG) with covariate controls, Kaplan-Meier survival analysis, and ranks candidates using a Cross-Cancer Consistency Score (CCCS).
- **Key Technologies**: Python, Pandas, Numpy, statsmodels, lifelines, DuckDB, Parquet.
- **Location**: See the [oncofind directory](./oncofind/) and its dedicated [oncofind/README.md](./oncofind/README.md).

### 2. JargonQuest (React / TypeScript Frontend Web App)
An interactive educational application for mastering domain-specific vocabulary and concepts.
- **Core Functionality**: Dynamic quizzes, visual matching grids, custom vocabulary decks, and confetti animations to facilitate learning in complex fields.
- **Key Technologies**: React 19, TypeScript, Vite, TailwindCSS / Vanilla CSS, canvas-confetti.
- **Run Locally**:
  ```bash
  npm install
  npm run dev
  ```

---

## Workspace Structure

```
.
├── oncofind/             # Python CLI pipeline for pan-cancer biomarkers
│   ├── oncofind/         # Package source (data modules, analysis engines)
│   ├── scripts/          # Run scripts (pipeline orchestration, sensitivity tests)
│   └── tests/            # pytest suite
│
├── src/                  # JargonQuest React source code
├── public/               # JargonQuest assets
├── package.json          # npm project manifest for JargonQuest
└── vite.config.ts        # Vite build configuration
```
