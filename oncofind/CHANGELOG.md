# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-29

### Added
- **Core CLI Framework**: Typer entrypoints for `download`, `deg`, `survival`, `pancancer`, `score`, and `report`.
- **DuckDB + Parquet Storage**: Local column-oriented cache engine for fast out-of-core expression queries.
- **Asynchronous GDC Client**: Async downloader utilizing `httpx` and `tqdm` to pull RNA-seq and clinical datasets from GDC Portal.
- **DEG Engine**: Negative Binomial GLM via `PyDESeq2` with an automated Welch's t-test + Benjamini-Hochberg FDR correction fallback.
- **Survival Analysis**: Kaplan-Meier curves and Log-rank test statistics via `lifelines` supporting Median, Quartile, and Optimal hazard splitting.
- **Novel Biological Metric**: Cross-Cancer Consistency Score (CCCS) combining Directionality, Fold Change, Significance, and Survival association with biological weights.
- **Batch Correction**: Location-and-Scale empirical ComBat batch correction in pure Python.
- **Interactive Visualizations**: Plotly-based volcano plots, clustered heatmaps, survival step functions, and side-by-side pan-cancer comparison dashboards.
- **HTML Reporting**: Jinja2 compiler to bundle datasets, tables, and multiple interactive Plotly plots into a single self-contained HTML report.
- **CI/CD Workflows**: GitHub Actions tests suite runner and PyPI trusted publisher.
