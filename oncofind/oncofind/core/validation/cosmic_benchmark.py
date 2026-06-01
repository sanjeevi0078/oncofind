"""
COSMIC Cancer Gene Census benchmark for CCCS validation.

Downloads (or reads a local copy of) the COSMIC Cancer Gene Census CSV and
computes Precision@K: what fraction of the top-K CCCS-ranked genes are
confirmed cancer drivers in COSMIC Tier 1?

Usage:
    from oncofind.core.validation.cosmic_benchmark import CosmicBenchmark

    bench = CosmicBenchmark(cosmic_csv_path="census.csv")
    report = bench.evaluate(cccs_df, ks=[10, 20, 50])
    print(report)

COSMIC Cancer Gene Census is freely available (no login required for Tier 1):
  https://cancer.sanger.ac.uk/census
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

logger = logging.getLogger(__name__)

# Public COSMIC CGC columns we care about
_GENE_SYMBOL_COLS = ["Gene Symbol", "Gene symbol", "GENE_SYMBOL", "symbol"]
_TIER_COLS = ["Tier", "tier", "TIER"]


class CosmicBenchmark:
    """
    Evaluate CCCS rankings against the COSMIC Cancer Gene Census.

    The key metric is **Precision@K**: the fraction of the top-K genes in the
    CCCS output that are confirmed cancer drivers in COSMIC Tier 1 (the most
    confident, manually curated tier).

    A Precision@50 ≥ 0.60 (60%) is a strong signal that the CCCS metric
    is selecting biologically meaningful genes rather than statistical noise.
    """

    def __init__(self, cosmic_csv_path: Path):
        """
        Args:
            cosmic_csv_path: Path to the COSMIC Cancer Gene Census CSV.
                             Download from https://cancer.sanger.ac.uk/census
                             (free, no login required for Tier 1 access).
        """
        self.cosmic_csv_path = Path(cosmic_csv_path)
        self._tier1_genes: Optional[set] = None
        self._all_cosmic_genes: Optional[set] = None

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def load(self) -> None:
        """Parse the COSMIC CSV and extract Tier 1 and all gene sets."""
        if not self.cosmic_csv_path.exists():
            raise FileNotFoundError(
                f"COSMIC CSV not found at: {self.cosmic_csv_path}\n"
                "Download it from: https://cancer.sanger.ac.uk/census\n"
                "(Click 'Download' → 'Cancer Gene Census' → 'CSV')"
            )

        df = pd.read_csv(self.cosmic_csv_path)

        # Resolve column names flexibly
        gene_col = self._find_column(df, _GENE_SYMBOL_COLS)
        tier_col = self._find_column(df, _TIER_COLS)

        if gene_col is None:
            raise ValueError(
                f"Could not find gene symbol column in COSMIC CSV. "
                f"Available columns: {list(df.columns)}"
            )

        all_genes = set(df[gene_col].dropna().str.upper().tolist())

        if tier_col is not None:
            tier1_df = df[df[tier_col].astype(str).str.strip() == "1"]
            tier1_genes = set(tier1_df[gene_col].dropna().str.upper().tolist())
        else:
            logger.warning(
                "No 'Tier' column found in COSMIC CSV — treating all genes as Tier 1."
            )
            tier1_genes = all_genes

        self._all_cosmic_genes = all_genes
        self._tier1_genes = tier1_genes
        logger.info(
            f"Loaded COSMIC CGC: {len(tier1_genes)} Tier 1 genes, "
            f"{len(all_genes)} total genes."
        )

    def evaluate(
        self,
        cccs_df: pd.DataFrame,
        gene_col: str = "gene_symbol",
        score_col: str = "cccs",
        ks: Optional[List[int]] = None,
    ) -> "BenchmarkReport":
        """
        Compute Precision@K for the CCCS-ranked gene list vs COSMIC Tier 1.

        Args:
            cccs_df: DataFrame output from the CCCS scorer. Must have at least
                     a gene symbol column and a CCCS score column.
            gene_col: Name of the gene symbol column in cccs_df.
            score_col: Name of the CCCS score column in cccs_df.
            ks: List of K values for Precision@K. Defaults to [10, 20, 50, 100].

        Returns:
            BenchmarkReport with precision@K values and the overlap gene list.
        """
        if self._tier1_genes is None:
            self.load()

        if ks is None:
            ks = [10, 20, 50, 100]

        # Sort by CCCS descending
        ranked = cccs_df.sort_values(score_col, ascending=False).reset_index(drop=True)
        ranked_genes = ranked[gene_col].str.upper().tolist()

        precision_at_k: Dict[int, float] = {}
        overlap_at_k: Dict[int, List[str]] = {}

        for k in ks:
            top_k = ranked_genes[:k]
            hits = [g for g in top_k if g in self._tier1_genes]
            precision_at_k[k] = len(hits) / k if k > 0 else 0.0
            overlap_at_k[k] = hits

        return BenchmarkReport(
            precision_at_k=precision_at_k,
            overlap_at_k=overlap_at_k,
            n_cosmic_tier1=len(self._tier1_genes),
            n_genes_ranked=len(ranked_genes),
        )

    # ------------------------------------------------------------------ #
    # Internal                                                             #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _find_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
        """Return the first candidate column name that exists in df."""
        for col in candidates:
            if col in df.columns:
                return col
        return None


class BenchmarkReport:
    """Results of a COSMIC benchmark evaluation."""

    def __init__(
        self,
        precision_at_k: Dict[int, float],
        overlap_at_k: Dict[int, List[str]],
        n_cosmic_tier1: int,
        n_genes_ranked: int,
    ):
        self.precision_at_k = precision_at_k
        self.overlap_at_k = overlap_at_k
        self.n_cosmic_tier1 = n_cosmic_tier1
        self.n_genes_ranked = n_genes_ranked

    def summary(self) -> str:
        """Return a plain-text summary of the benchmark results."""
        lines = [
            "COSMIC Cancer Gene Census — CCCS Benchmark",
            "=" * 50,
            f"COSMIC Tier 1 genes: {self.n_cosmic_tier1}",
            f"CCCS genes ranked:   {self.n_genes_ranked}",
            "",
            "Precision@K (fraction of top-K CCCS genes in COSMIC Tier 1):",
        ]
        for k, prec in sorted(self.precision_at_k.items()):
            hits = len(self.overlap_at_k[k])
            bar = "█" * int(prec * 20)
            status = "✅" if prec >= 0.60 else ("⚠️" if prec >= 0.40 else "❌")
            lines.append(f"  P@{k:<4} = {prec:.1%}  ({hits}/{k})  {bar} {status}")

        lines.append("")
        lines.append("Guidance:")
        lines.append("  P@50 ≥ 60% → strong external validation, mention in README")
        lines.append("  P@50 40-60% → moderate signal, describe as 'exploratory'")
        lines.append("  P@50 < 40%  → review CCCS weights or data quality")
        return "\n".join(lines)

    def to_dataframe(self) -> pd.DataFrame:
        """Return results as a tidy DataFrame for export."""
        rows = []
        for k in sorted(self.precision_at_k.keys()):
            rows.append({
                "K": k,
                "precision": self.precision_at_k[k],
                "hits": len(self.overlap_at_k[k]),
                "cosmic_tier1_hits": ", ".join(self.overlap_at_k[k][:20]),
            })
        return pd.DataFrame(rows)
