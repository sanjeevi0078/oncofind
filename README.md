# Bioinformatics & Technical Vocabulary Workspace 🧬📚

Welcome to the multi-project monorepo created and maintained by **[Sanjeevi](https://github.com/sanjeevi0078)**. This repository hosts two distinct, production-grade applications that bridge computational oncology and technical domain-specific learning.

---

## 📂 Project Hub

This monorepo is organized into two primary workspaces:

### 1. `oncofind` 🔬 — Computational Oncology CLI Pipeline
An end-to-end command-line bioinformatics pipeline for pan-cancer biomarker discovery and validation.

* **Core Pipeline**: 
  1. Downloads raw transcriptomic (RNA-seq STAR counts) and clinical metadata from the **NIH Genomic Data Commons (GDC)** API.
  2. Runs Differential Gene Expression (DEG) using vectorized OLS covariate-adjusted t-tests.
  3. Fits Kaplan-Meier survival curves and runs log-rank tests (via `lifelines`) with Bonferroni correction to prevent p-hacking.
  4. Computes a **Cross-Cancer Consistency Score (CCCS)** for multi-cohort biomarker consistency.
  5. Benchmarks findings against the **Sanger COSMIC Cancer Gene Census (CGC) Tier 1** database.
* **Key Technologies**: Python 3.10+, Pandas, NumPy, Statsmodels, Lifelines, DuckDB, Parquet, Jinja2, Plotly.
* **Location**: See the dedicated [oncofind subdirectory](./oncofind/) and its [README.md](./oncofind/README.md).

### 2. `JargonQuest` 🎮 — Interactive Domain Vocabulary Web App
An interactive React application designed to master specialized terminology and technical jargon through game-based learning.

* **Core Features**: 
  - Dynamic vocabulary decks covering bioinformatics, oncology, and systems engineering.
  - Interactive grid-matching visual quiz game.
  - Performance feedback with canvas-confetti reward animations.
  - Elegant HSL-tailored dark/light mode interface.
* **Key Technologies**: React 19, TypeScript, Vite, Vanilla CSS, Canvas-Confetti.
* **Run Locally**:
  ```bash
  # Install dependencies and start development server
  npm install
  npm run dev
  ```
* **Location**: The source code is situated directly in the monorepo root directory (`src/`, `public/`, `package.json`).

---

## 📐 Workspace Architecture

```
.
├── oncofind/             # Python CLI pipeline for pan-cancer biomarkers
│   ├── oncofind/         # CLI package source (data clients, analysis models, reports)
│   ├── scripts/          # Run scripts (pipeline orchestration, weight sensitivity)
│   ├── tests/            # Automated pytest suite (26 unit tests)
│   └── pyproject.toml    # Hatch/Pip build manifest
│
├── src/                  # JargonQuest React application source
│   ├── components/       # Game boards, match panels, and UI elements
│   ├── data/             # Vocabulary dictionaries and definitions
│   └── App.tsx           # Application core
│
├── public/               # Static assets & SVG icons
├── package.json          # npm manifest for JargonQuest
└── vite.config.ts        # Vite compiler configurations
```

---

## 🛠️ Verification & Quality Gates

Both projects adhere to strict engineering and software design practices:
* **CI/CD Integrated**: Workflows configured in `.github/workflows/` to automatically test across multiple Python versions (3.10 to 3.13) and linters.
* **Fully Tested**: The `oncofind` package includes a robust test suite of **26 passing unit tests** covering matrix ingestion, survival splits, OLS regression solving, and druggability checks.

---

Developed with ❤️ by **[Sanjeevi](https://github.com/sanjeevi0078)**. For questions or collaboration, please open an issue on the [Bug Tracker](https://github.com/sanjeevi0078/oncofind/issues).
