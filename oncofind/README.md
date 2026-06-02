# oncofind 🔬

> **Pan-cancer biomarker discovery from the command line.**  
> Integrates TCGA RNA-seq, clinical data, survival endpoints, and external validation into a reproducible, publication-ready pipeline.

[![Tests](https://img.shields.io/badge/tests-26%20passed-brightgreen)](tests/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![TCGA](https://img.shields.io/badge/data-TCGA%20GDC-orange)](https://portal.gdc.cancer.gov)
[![COSMIC](https://img.shields.io/badge/validated-COSMIC%20CGC-red)](https://cancer.sanger.ac.uk/census)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## What it does

`oncofind` downloads real TCGA RNA-seq data from the NIH Genomic Data Commons, runs differential expression, Kaplan-Meier survival analysis, and cross-cancer consistency scoring — then validates ranked biomarker candidates against the COSMIC Cancer Gene Census.

**In one command chain:**

```bash
oncofind download --cancer BRCA --n-samples 100
oncofind deg --cancer BRCA --groupby stage
oncofind survival --cancer BRCA --gene TP53
oncofind score --cancers BRCA --top-n 200
oncofind validate --cccs-csv oncofind_results/pancancer_cccs_rankings.csv \
                  --cosmic-csv cosmic_census.csv --gene-col Gene --score-col CCCS
```

---

## Architecture

```
GDC API (TCGA)
     │
     ▼
GDCClient ──► ExpressionStore (Parquet)
     │              │
     ▼              ▼
ClinicalStore ──► DEGAnalyzer ──► volcano.html / heatmap.html
(survival_days,        │
 sample_type,          ▼
 ER/PR/HER2)    SurvivalAnalyzer ──► KM plot .html
                       │
                       ▼
               CrossCancerConsistencyScorer (CCCS)
                       │
                       ▼
               CosmicBenchmark (Precision@K vs CGC Tier 1)
                       │
                       ▼
               ReportGenerator ──► report_BRCA.html
```

### Key modules

| Module | Purpose |
|---|---|
| `oncofind/core/data/gdc_client.py` | Async GDC API client (queries + parallel downloads) |
| `oncofind/core/data/expression_store.py` | Parquet expression matrix storage + DuckDB queries |
| `oncofind/core/data/clinical_store.py` | Clinical metadata: survival, subtype, sample_type |
| `oncofind/core/data/dgidb_client.py` | DGIdb drug-gene interaction API (700+ targets, cached) |
| `oncofind/core/analysis/deg.py` | DEG: PyDESeq2 + t-test fallback, tumor-vs-normal mode |
| `oncofind/core/analysis/survival.py` | Kaplan-Meier + log-rank (lifelines) |
| `oncofind/core/analysis/cccs.py` | Cross-Cancer Consistency Score |
| `oncofind/core/analysis/batch.py` | ComBat batch correction for multi-cohort analysis |
| `oncofind/core/validation/cosmic_benchmark.py` | Precision@K vs COSMIC Cancer Gene Census |
| `oncofind/cli/utils/manifest.py` | JSON run manifests for reproducibility |
| `scripts/weight_sensitivity.py` | CCCS rank stability (Kendall-τ) |

---

## Installation

```bash
git clone https://github.com/sanjeevi0078/oncofind
cd oncofind
pip install -e .
```

**Requirements:** Python 3.10+, ~2GB disk space per cancer type.

---

## Quickstart

### 1. Download real TCGA data

```bash
# 97–100 BRCA RNA-seq + clinical samples (~400MB, ~6 min)
oncofind download --cancer BRCA --n-samples 100

# Multiple cancers for pan-cancer analysis
oncofind download --cancer LUAD --n-samples 50
oncofind download --cancer COAD --n-samples 50
```

### 2. Differential expression

```bash
# Clinical subgroup comparison
oncofind deg --cancer BRCA --groupby stage --method ttest

# Tumor vs Normal (uses GDC sample_type field)
oncofind deg --cancer BRCA --mode tumor_vs_normal --method deseq2
```

Outputs: `volcano_BRCA.html`, `heatmap_BRCA.html`, `BRCA_deg_results.csv`

### 3. Survival analysis

```bash
oncofind survival --cancer BRCA --gene TP53
oncofind survival --cancer BRCA --gene ESR1
oncofind survival --cancer BRCA --gene ERBB2
```

Outputs: `BRCA_TP53_survival.html` (Kaplan-Meier), `BRCA_TP53_survival_groups.csv`

### 4. Pan-cancer scoring (CCCS)

```bash
# Single cancer
oncofind score --cancers BRCA --top-n 200

# Multi-cancer with ComBat batch correction
oncofind pancancer --gene TP53 --cancers BRCA LUAD COAD --batch-correct
```

### 5. COSMIC validation

```bash
# Download COSMIC CGC CSV from cancer.sanger.ac.uk/census (free registration)
oncofind validate \
  --cccs-csv oncofind_results/pancancer_cccs_rankings.csv \
  --cosmic-csv cosmic_census.csv \
  --gene-col Gene --score-col CCCS \
  --ks 10,20,50,100
```

### 6. Rank stability analysis

```bash
python scripts/weight_sensitivity.py \
  --cccs-csv oncofind_results/pancancer_cccs_rankings.csv
```

Reports Kendall-τ rank correlation across 5 CCCS weight configurations.

### 7. Full report

```bash
oncofind report --cancer BRCA --output-dir oncofind_results/
```

---

## TCGA Data Access (GDC API)

All data is fetched from the **NIH Genomic Data Commons** public API — no account required for open-access data.

```python
# Under the hood: GDCClient queries the GDC Files endpoint
# and downloads STAR-Counts RNA-seq files (augmented_star_gene_counts format)
GET https://api.gdc.cancer.gov/files?...
GET https://api.gdc.cancer.gov/data/{file_id}
GET https://api.gdc.cancer.gov/cases?...  # clinical
```

**Is the GDC API free and reliable?**  
Yes, for open-access TCGA data (most RNA-seq). Rate limited to ~10 concurrent connections. The client uses an asyncio semaphore (max 5 concurrent) and `aiter_bytes` streaming to handle large files (4–8 MB each). Failed downloads are logged and retried on next run (cached by file path).

---

## The CCCS Metric

The **Cross-Cancer Consistency Score** (0–1) rewards genes that are:
1. Consistent in direction across multiple cancer types (all up or all down)
2. High in fold change magnitude (|log2FC|)
3. Associated with survival when split by expression
4. Highly statistically significant (small adjusted p-value)

```
CCCS = w1·S_dir + w2·S_mag + w3·S_surv + w4·S_sig
```

Default weights: `{"direction": 0.25, "magnitude": 0.25, "survival": 0.35, "significance": 0.15}`

### External validation

Ranked gene lists are benchmarked against **COSMIC Cancer Gene Census Tier 1** (572 manually curated cancer driver genes):

```
Precision@K = |top_K ∩ COSMIC_Tier1| / K
```

A P@50 > 50% means the majority of your top-50 candidates are confirmed cancer drivers.

---

## Reproducibility

Every CLI command writes a `{command}_manifest.json` alongside results:

```json
{
  "oncofind_version": "0.1.0",
  "command": "deg",
  "timestamp_utc": "2026-05-29T16:52:00Z",
  "parameters": {
    "cancer": "BRCA", "mode": "subtype_comparison",
    "groupby": "stage", "method": "ttest",
    "fdr": 0.05, "log2fc": 1.0
  },
  "input_data_hashes": {
    "expression_matrix.parquet": "a3f7c2..."
  },
  "result_summary": {
    "n_genes_tested": 60241,
    "n_significant": 1847,
    "n_up": 923, "n_down": 924,
    "top_gene": "TP53"
  }
}
```

---

## CLI Reference

```
oncofind --help

Commands:
  download    Download TCGA RNA-seq + clinical data from GDC
  deg         Differential expression (PyDESeq2 or t-test, tumor vs normal)
  survival    Kaplan-Meier + log-rank survival analysis
  pancancer   Cross-cancer gene consistency with ComBat batch correction
  score       Rank all genes by CCCS
  validate    Benchmark against COSMIC Cancer Gene Census (Precision@K)
  report      Full HTML report for a cancer type
```

```
oncofind download --cancer BRCA --n-samples 100
oncofind deg      --cancer BRCA --mode tumor_vs_normal --method deseq2
oncofind survival --cancer BRCA --gene TP53 --split tercile
oncofind pancancer --gene TP53 --cancers BRCA LUAD COAD --batch-correct
oncofind score    --cancers BRCA LUAD COAD --top-n 200 --druggable-only
oncofind validate --cccs-csv rankings.csv --cosmic-csv census.csv --gene-col Gene --score-col CCCS
oncofind report   --cancer BRCA --output-dir results/
```

---

## Project Structure

```
oncofind/
├── oncofind/
│   ├── cli/
│   │   ├── commands/          # CLI commands (deg, survival, score, ...)
│   │   └── utils/
│   │       ├── manifest.py    # Run manifest / audit trail
│   │       └── validators.py  # Input validation
│   ├── config/
│   │   ├── druggability.py    # DGIdb facade
│   │   └── settings.py
│   └── core/
│       ├── analysis/
│       │   ├── batch.py       # ComBat batch correction
│       │   ├── cccs.py        # Cross-cancer consistency score
│       │   ├── deg.py         # Differential expression
│       │   └── survival.py    # Kaplan-Meier
│       ├── data/
│       │   ├── clinical_store.py
│       │   ├── dgidb_client.py
│       │   ├── expression_store.py
│       │   └── gdc_client.py
│       ├── validation/
│       │   └── cosmic_benchmark.py
│       └── visualization/
│           ├── heatmap.py
│           ├── pancancer_plot.py
│           ├── survival_plot.py
│           └── volcano.py
├── scripts/
│   ├── run_full_pipeline.py   # End-to-end pipeline runner
│   └── weight_sensitivity.py  # CCCS rank stability (Kendall-τ)
├── tests/                     # 21 unit tests
└── cosmic_census.csv          # COSMIC CGC Tier 1 gene list
```

---

## Methods, Limitations, and Validation Discussion

### The CCCS Scoring System
The Cross-Cancer Consistency Score (CCCS) is a unified heuristic designed to identify robust transcriptomic biomarkers. It integrates four orthogonal signals:
1. **Directional Consistency (25%)**: Rewards genes whose expression changes concordantly (either universally upregulated or universally downregulated) across multiple cohorts.
2. **Magnitude (25%)**: Rewards genes with large absolute log2 fold-changes.
3. **Clinical Association (35%)**: Rewards genes where expression splits (e.g., median or quartile) are significantly associated with overall survival via log-rank tests.
4. **Statistical Significance (15%)**: Rewards genes with small adjusted p-values.

### Covariate Control and Batch Standardization
To prevent false discoveries arising from clinical confounding and technical batch effects:
- **Location-Scale Batch Standardization**: Multi-cohort data is standardized within each cohort by centering and scaling (centering by the mean and dividing by the standard deviation of each batch). This mitigates technical batch differences without the risk of over-fitting associated with small-sample empirical Bayes models.
- **Covariate-Adjusted OLS Regression**: The differential expression fallback method employs ordinary least squares (OLS) regression (`gene ~ group + age + sex`) rather than simple t-tests to control for age and gender covariates, ensuring observed differences are driven by disease state rather than demographic confounding.

### COSMIC CGC Validation and Biological Limitations
Benchmarking `oncofind` rankings against the **COSMIC Cancer Gene Census (CGC) Tier 1** yields a low precision (e.g., ~1% for top-100 candidates). This is a known biological limitation of expression-based biomarker pipelines:
- **Expression vs. Mutation**: COSMIC CGC is curated primarily from genes carrying somatic driver mutations (e.g., `TP53`, `PIK3CA`, `PTEN`, `AKT1`). The activity of these mutated proteins is often regulated post-translationally (e.g., phosphorylation, conformational changes) rather than by massive changes in mRNA expression.
- **Downstream Effectors**: Differential expression between tumor and normal tissue primarily identifies cell-cycle, proliferation, and microenvironment-remodeling markers (e.g., `MMP11`, `NEK2`, `KIF20A`, `ZWINT`, `UHRF1`). While these genes are highly dynamic and strong prognostic factors (thus receiving high CCCS scores), they are downstream effectors rather than primary mutation-based drivers, and are therefore excluded from the COSMIC CGC census.
- **Methodological Recommendation**: For general cancer driver identification, integrate transcriptomic profiling with somatic mutation (SNV/Indel) and copy number variation (CNV) data.

---

## License

MIT License — see [LICENSE](LICENSE).

## Citation

If you use oncofind in research, please cite:

```
Sanjeevi Utchav. oncofind: Pan-cancer biomarker discovery pipeline. 2026.
GitHub: https://github.com/sanjeevi0078/oncofind
```
