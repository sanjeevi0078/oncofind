#!/usr/bin/env python3
"""
Orchestration script to run a full multi-cohort (BRCA, LUAD, COAD) analysis
and generate results for the oncofind research paper.
"""

import subprocess
import sys
import os
import pandas as pd

CANCERS = ["BRCA", "LUAD", "COAD"]
N_SAMPLES = 50

def run_command(cmd_list):
    print(f"\nRunning: {' '.join(cmd_list)}")
    result = subprocess.run(cmd_list, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing command!")
        print(f"Stdout:\n{result.stdout}")
        print(f"Stderr:\n{result.stderr}")
        return False
    print("Success!")
    return True

def main():
    print("======================================================================")
    # 1. Download cohorts
    for cancer in CANCERS:
        print(f"\n--- Downloading data for {cancer} (N={N_SAMPLES}) ---")
        success = run_command([
            "oncofind", "download", 
            "--cancer", cancer, 
            "--n-samples", str(N_SAMPLES)
        ])
        if not success:
            sys.exit(1)

    # 2. Run covariate-adjusted DEG for each cohort
    for cancer in CANCERS:
        print(f"\n--- Running DEG analysis for {cancer} (adjusted for age) ---")
        success = run_command([
            "oncofind", "deg", 
            "--cancer", cancer, 
            "--mode", "tumor_vs_normal", 
            "--method", "ttest",
            "--covariates", "age_at_index"
        ])
        if not success:
            sys.exit(1)

    # 3. Compute the Cross-Cancer Consistency Score (CCCS) across all cohorts
    print("\n--- Scoring genes using Cross-Cancer Consistency Score (CCCS) ---")
    cancers_arg = " ".join(CANCERS)
    success = run_command([
        "oncofind", "score", 
        "--cancers", cancers_arg, 
        "--mode", "tumor_vs_normal",
        "--top-n", "100"
    ])
    if not success:
        sys.exit(1)

    # 4. Validate findings against the COSMIC CGC Tier 1
    print("\n--- Benchmarking rankings against COSMIC Cancer Gene Census ---")
    if os.path.exists("cosmic_census.csv"):
        success = run_command([
            "oncofind", "validate",
            "--cccs-csv", "oncofind_results/pancancer_cccs_rankings.csv",
            "--cosmic-csv", "cosmic_census.csv"
        ])
    else:
        # Fallback to local oncofind folder path
        success = run_command([
            "oncofind", "validate",
            "--cccs-csv", "oncofind_results/pancancer_cccs_rankings.csv",
            "--cosmic-csv", "oncofind/cosmic_census.csv"
        ])
    if not success:
        sys.exit(1)

    # 5. Display the top 10 biomarkers
    print("\n======================================================================")
    print("TOP 10 CROSS-CANCER BIOMARKERS IDENTIFIED FOR THE PAPER:")
    rankings_path = "oncofind_results/pancancer_cccs_rankings.csv"
    if os.path.exists(rankings_path):
        df = pd.read_csv(rankings_path)
        print(df.head(10)[["Gene", "CCCS", "Druggable", "Target Drugs"]].to_string(index=False))
    else:
        print("Rankings file not found!")
    print("======================================================================")

if __name__ == "__main__":
    main()
