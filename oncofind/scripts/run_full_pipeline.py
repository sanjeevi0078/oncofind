#!/usr/bin/env python3
"""
Full pipeline runner: DEG + Survival + CCCS + COSMIC validate + Weight sensitivity.
Run this after 'oncofind download --cancer BRCA --n-samples 100' completes.

Usage:
    python scripts/run_full_pipeline.py 2>&1 | tee pipeline_run.log
"""

import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
RESULTS = BASE / "oncofind_results"
RESULTS.mkdir(exist_ok=True)

def run(cmd: str, label: str):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, cwd=str(BASE), capture_output=False, text=True)
    if result.returncode != 0:
        print(f"[WARNING] '{label}' exited with code {result.returncode}")
    return result.returncode

steps = [
    (
        "oncofind deg --cancer BRCA --groupby stage --method ttest --output-dir oncofind_results",
        "DEG: BRCA — Stage comparison"
    ),
    (
        "oncofind survival --cancer BRCA --gene TP53 --output-dir oncofind_results",
        "Survival: TP53 in BRCA"
    ),
    (
        "oncofind survival --cancer BRCA --gene ESR1 --output-dir oncofind_results",
        "Survival: ESR1 in BRCA"
    ),
    (
        "oncofind survival --cancer BRCA --gene ERBB2 --output-dir oncofind_results",
        "Survival: ERBB2 (HER2) in BRCA"
    ),
    (
        "oncofind score --cancers BRCA --top-n 500 --output-dir oncofind_results",
        "CCCS Scoring: BRCA top 500 genes"
    ),
    (
        "oncofind validate "
        "--cccs-csv oncofind_results/pancancer_cccs_rankings.csv "
        "--cosmic-csv cosmic_census.csv "
        "--gene-col Gene --score-col CCCS "
        "--ks 10,20,50,100 --export-csv",
        "COSMIC Validation: Precision@K"
    ),
    (
        "python scripts/weight_sensitivity.py "
        "--cccs-csv oncofind_results/pancancer_cccs_rankings.csv",
        "Weight Sensitivity: Kendall-tau stability"
    ),
    (
        "oncofind report --cancer BRCA --output-dir oncofind_results",
        "HTML Report: BRCA comprehensive"
    ),
]

print("\n🔬 oncofind Full Pipeline — Real TCGA-BRCA Data")
print(f"Results directory: {RESULTS}\n")

errors = 0
for cmd, label in steps:
    code = run(cmd, label)
    if code != 0:
        errors += 1

print(f"\n{'='*60}")
print(f"Pipeline complete. Errors: {errors}/{len(steps)}")
print(f"Results: {RESULTS}")
print(f"{'='*60}")
