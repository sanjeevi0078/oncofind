#!/usr/bin/env python3
"""
Direct CCCS scoring from pre-computed DEG results CSV.
Bypasses the score command's internal DEG re-run.
Uses raw p-value threshold (0.05) instead of BH-corrected padj,
which is appropriate for single-cancer gene candidate filtering.

Usage:
    python scripts/score_from_deg.py \
        --deg-csv oncofind_results/BRCA_stage_deg_results.csv \
        --cancer BRCA \
        --top-n 200 \
        --pvalue-threshold 0.05 \
        --log2fc-threshold 0.2 \
        --output oncofind_results/pancancer_cccs_rankings.csv
"""

import argparse
import logging
from pathlib import Path
import pandas as pd
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from oncofind.core.analysis.cccs import CrossCancerConsistencyScorer, CancerResult
from oncofind.core.analysis.survival import SurvivalAnalyzer
from oncofind.core.data.expression_store import ExpressionStore
from oncofind.core.data.clinical_store import ClinicalStore
from oncofind.config.druggability import is_druggable, get_drugs_for_gene
from oncofind.config.settings import settings

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Score genes by CCCS from pre-computed DEG results")
    parser.add_argument("--deg-csv", type=Path, required=True, help="DEG results CSV")
    parser.add_argument("--cancer", default="BRCA", help="Cancer type")
    parser.add_argument("--top-n", type=int, default=200, help="Number of top genes to include")
    parser.add_argument("--pvalue-threshold", type=float, default=0.05,
                        help="Raw p-value threshold for candidate filtering (default 0.05)")
    parser.add_argument("--log2fc-threshold", type=float, default=0.2,
                        help="Minimum absolute log2FC for candidate filtering (default 0.2)")
    parser.add_argument("--output", type=Path, default=Path("oncofind_results/pancancer_cccs_rankings.csv"))
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  CCCS Scoring from DEG: {args.deg_csv.name}")
    print(f"{'='*60}")

    # Load DEG results
    deg_df = pd.read_csv(args.deg_csv)
    print(f"Total genes in DEG: {len(deg_df):,}")

    # Filter candidates by raw p-value (BH correction is too conservative for 60K genes
    # with only 97 samples — use uncorrected p for candidate selection)
    candidates_df = deg_df[
        (deg_df["pvalue"] < args.pvalue_threshold) &
        (deg_df["log2FC"].abs() >= args.log2fc_threshold)
    ].copy()
    print(f"Candidates (p<{args.pvalue_threshold}, |log2FC|>{args.log2fc_threshold}): {len(candidates_df):,}")

    if candidates_df.empty:
        print("ERROR: No candidates found. Try loosening thresholds.")
        sys.exit(1)

    # Load expression + clinical for survival
    data_dir = settings.data_dir
    expr_store = ExpressionStore(data_dir)
    clin_store = ClinicalStore(data_dir)
    counts_df = pd.read_parquet(expr_store.get_expression_path(args.cancer)).set_index("sample_barcode")
    clinical_df = clin_store.get_clinical_df(args.cancer)

    survival_analyzer = SurvivalAnalyzer()
    scorer = CrossCancerConsistencyScorer()

    results = []
    n = len(candidates_df)
    print(f"\nScoring {n} candidates (this may take a few minutes)...")

    for i, (_, row) in enumerate(candidates_df.iterrows(), 1):
        gene = row["gene_symbol"]
        if i % 50 == 0:
            print(f"  [{i}/{n}] {gene}")

        # Build CancerResult from the DEG row
        direction = row.get("direction", "ns")
        if direction == "ns":
            direction = "up" if row["log2FC"] > 0 else "down"

        # Run survival
        survival_p = None
        try:
            gene_col = expr_store.get_gene_column(args.cancer, gene)
            expression_df = counts_df[[gene_col]].rename(columns={gene_col: gene})
            surv_res = survival_analyzer.analyze(expression_df, clinical_df, gene, p_value_only=True)
            survival_p = surv_res.p_value
        except Exception:
            pass

        cancer_result = CancerResult(
            cancer_type=args.cancer,
            log2fc=float(row["log2FC"]),
            padj=float(row["pvalue"]),   # Use raw pvalue for CCCS input
            direction=direction,
            survival_pvalue=survival_p,
        )

        cccs_res = scorer.compute(
            gene_symbol=gene,
            gene_id=f"ENSG_{gene}",
            cancer_results=[cancer_result],
        )

        results.append({
            "Gene": gene,
            "CCCS": cccs_res.cccs,
            "Direction": direction.upper(),
            "log2FC": round(row["log2FC"], 4),
            "pvalue": round(row["pvalue"], 6),
            "padj_BH": round(row["padj"], 6),
            "Survival_p": round(survival_p, 4) if survival_p is not None else None,
            "Druggable": "YES" if is_druggable(gene) else "NO",
            "Target_Drugs": ", ".join(get_drugs_for_gene(gene)) if is_druggable(gene) else "N/A",
        })

    results_df = pd.DataFrame(results).sort_values("CCCS", ascending=False)
    top_df = results_df.head(args.top_n)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    top_df.to_csv(args.output, index=False)

    print(f"\n{'='*60}")
    print(f"  Top 20 genes by CCCS")
    print(f"{'='*60}")
    print(top_df[["Gene","CCCS","Direction","log2FC","Survival_p","Druggable"]].head(20).to_string(index=False))
    print(f"\nSaved {len(top_df)} genes to: {args.output}")


if __name__ == "__main__":
    main()
