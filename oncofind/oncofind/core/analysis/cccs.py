import logging
from dataclasses import dataclass
from typing import Literal, List, Optional, Tuple, Dict
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class CancerResult:
    cancer_type: str
    log2fc: float
    padj: float
    direction: Literal["up", "down", "ns"]
    survival_pvalue: float | None


@dataclass  
class CCCSResult:
    gene_symbol: str
    gene_id: str
    cccs: float                        # Final score 0-1
    direction_score: float
    magnitude_score: float
    survival_score: float
    significance_score: float
    n_cancers_tested: int
    n_cancers_significant: int
    n_cancers_survival_significant: int
    dominant_direction: Literal["up", "down", "mixed", "ns"]
    cancer_results: List[CancerResult]
    interpretation: str                # Plain English summary


class CrossCancerConsistencyScorer:
    """
    Computes the Cross-Cancer Consistency Score (CCCS) for a gene.
    
    Biological rationale: A gene that is consistently dysregulated
    in the same direction across multiple cancer types is more likely
    to represent a fundamental oncogenic mechanism rather than a
    cancer-type-specific artifact. Combined with survival association,
    this identifies high-priority biomarker candidates.
    """
    
    WEIGHTS = {
        "direction": 0.25,
        "magnitude": 0.25,
        "survival": 0.35,
        "significance": 0.15,
    }
    
    def compute(
        self,
        gene_symbol: str,
        gene_id: str,
        cancer_results: List[CancerResult],
        padj_threshold: float = 0.05,
        survival_pvalue_threshold: float = 0.05,
    ) -> CCCSResult:
        """
        Compute CCCS for a single gene across multiple cancer types.
        
        Args:
            gene_symbol: HUGO gene symbol (e.g. "ERBB2")
            gene_id: Ensembl ID (e.g. "ENSG00000141736")
            cancer_results: DEG + survival results per cancer type
            padj_threshold: FDR threshold for significance
            survival_pvalue_threshold: p-value threshold for survival
            
        Returns:
            CCCSResult with all component scores and interpretation
        """
        n_cancers = len(cancer_results)
        if n_cancers == 0:
            return CCCSResult(
                gene_symbol=gene_symbol,
                gene_id=gene_id,
                cccs=0.0,
                direction_score=0.0,
                magnitude_score=0.0,
                survival_score=0.0,
                significance_score=0.0,
                n_cancers_tested=0,
                n_cancers_significant=0,
                n_cancers_survival_significant=0,
                dominant_direction="ns",
                cancer_results=[],
                interpretation="Gene was not tested in any cancer types. CCCS = 0.0"
            )

        # 1. Direction score & Dominant direction
        dir_score, dominant_dir, sig_cancers = self._direction_score(cancer_results, padj_threshold)
        
        # 2. Magnitude score
        mag_score = self._magnitude_score(cancer_results, padj_threshold)
        
        # 3. Survival score
        surv_score, surv_sig_cancers = self._survival_score(cancer_results, survival_pvalue_threshold)
        
        # 4. Significance score
        sig_score = self._significance_score(cancer_results)
        
        # Calculate weighted final score, scaled by the consistency fraction (n_cancers_significant / n_cancers_tested)
        raw_score = (
            self.WEIGHTS["direction"] * dir_score +
            self.WEIGHTS["magnitude"] * mag_score +
            self.WEIGHTS["survival"] * surv_score +
            self.WEIGHTS["significance"] * sig_score
        )
        
        n_sig = len(sig_cancers)
        cccs = raw_score * (n_sig / n_cancers)
        
        # Edge cases
        # Handle all cancers non-significant: CCCS should be 0.0 or extremely low
        if len(sig_cancers) == 0:
            dominant_dir = "ns"
            
        result = CCCSResult(
            gene_symbol=gene_symbol,
            gene_id=gene_id,
            cccs=round(float(cccs), 4),
            direction_score=round(dir_score, 4),
            magnitude_score=round(mag_score, 4),
            survival_score=round(surv_score, 4),
            significance_score=round(sig_score, 4),
            n_cancers_tested=n_cancers,
            n_cancers_significant=len(sig_cancers),
            n_cancers_survival_significant=len(surv_sig_cancers),
            dominant_direction=dominant_dir,
            cancer_results=cancer_results,
            interpretation=""
        )
        
        # Generate dynamic interpretation
        result.interpretation = self._generate_interpretation(result, sig_cancers, surv_sig_cancers)
        return result

    def _direction_score(
        self, results: List[CancerResult], padj_threshold: float
    ) -> Tuple[float, Literal["up", "down", "mixed", "ns"], List[str]]:
        """
        Returns (score, dominant_direction, significant_cancer_types).
        Only considers significant results for direction computation.
        """
        sig_results = []
        sig_cancers = []
        for r in results:
            # Handle NaN padj (treat as 1.0)
            padj = r.padj if not np.isnan(r.padj) else 1.0
            if padj < padj_threshold and r.direction in ["up", "down"]:
                sig_results.append(r.direction)
                sig_cancers.append(r.cancer_type)
                
        if not sig_results:
            return 0.0, "ns", []

        n_up = sig_results.count("up")
        n_down = sig_results.count("down")
        
        # Net direction consistency normalized by total tested cancers
        # Example: 3 cancers, 2 UP, 1 DOWN -> |2 - 1| / 3 = 0.33
        # 3 cancers, 3 UP, 0 DOWN -> |3 - 0| / 3 = 1.0
        score = abs(n_up - n_down) / len(results)
        
        if n_up > n_down:
            dom = "up"
        elif n_down > n_up:
            dom = "down"
        else:
            dom = "mixed"
            
        return score, dom, sig_cancers

    def _magnitude_score(
        self, results: List[CancerResult], padj_threshold: float
    ) -> float:
        """Sigmoid-normalized mean |log2FC| across significant cancers."""
        sig_fcs = []
        for r in results:
            padj = r.padj if not np.isnan(r.padj) else 1.0
            if padj < padj_threshold:
                # Handle infinite values if any
                fc = r.log2fc
                if np.isinf(fc):
                    fc = 10.0 if fc > 0 else -10.0
                sig_fcs.append(abs(fc))
                
        if not sig_fcs:
            return 0.0
            
        mean_abs_log2fc = float(np.mean(sig_fcs))
        
        # Sigmoid normalization: score / (score + 1)
        # E.g. mean fold change of 1.0 -> 1.0 / 2.0 = 0.5
        # mean fold change of 3.0 -> 3.0 / 4.0 = 0.75
        # mean fold change of 9.0 -> 9.0 / 10.0 = 0.90
        return mean_abs_log2fc / (mean_abs_log2fc + 1.0)

    def _survival_score(
        self, results: List[CancerResult], threshold: float
    ) -> Tuple[float, List[str]]:
        """Fraction of cancers with significant survival association."""
        surv_sig_cancers = []
        for r in results:
            if r.survival_pvalue is not None and not np.isnan(r.survival_pvalue):
                if r.survival_pvalue < threshold:
                    surv_sig_cancers.append(r.cancer_type)
                    
        score = len(surv_sig_cancers) / len(results)
        return score, surv_sig_cancers

    def _significance_score(self, results: List[CancerResult]) -> float:
        """Normalized mean -log10(padj) across all tested cancers."""
        neg_logs = []
        for r in results:
            padj = r.padj if not np.isnan(r.padj) else 1.0
            # Clip padj to minimum of 1e-15 to avoid infinity
            padj_clipped = max(padj, 1e-15)
            neg_logs.append(-np.log10(padj_clipped))
            
        mean_neg_log = float(np.mean(neg_logs))
        
        # Normalize to [0,1] using mean_val / (mean_val + 2.0)
        # E.g. mean padj of 0.01 -> mean -log10 = 2.0 -> 2.0 / 4.0 = 0.5
        # mean padj of 1e-6 -> mean -log10 = 6.0 -> 6.0 / 8.0 = 0.75
        return mean_neg_log / (mean_neg_log + 2.0)

    def _generate_interpretation(
        self, result: CCCSResult, sig_cancers: List[str], surv_sig_cancers: List[str]
    ) -> str:
        """Generate a plain-English interpretation of the CCCS."""
        g = result.gene_symbol
        n_cancers = result.n_cancers_tested
        
        if n_cancers == 0:
            return f"No results available for {g}."
            
        # Confidence warning if tested on only 1 cancer
        confidence_suffix = " (low confidence, n=1)" if n_cancers == 1 else ""

        if result.n_cancers_significant == 0:
            return (
                f"{g} does not show significant dysregulation in any tested cancers"
                f"{confidence_suffix}. CCCS = {result.cccs:.2f} — no pan-cancer biomarker signal detected."
            )

        dir_word = "upregulation" if result.dominant_direction == "up" else (
            "downregulation" if result.dominant_direction == "down" else "mixed dysregulation"
        )
        
        cancer_list = ", ".join(sig_cancers)
        
        surv_str = ""
        if result.n_cancers_survival_significant > 0:
            surv_cancers = ", ".join(surv_sig_cancers)
            surv_str = f" with a significant survival association in {result.n_cancers_survival_significant}/{n_cancers} cancers ({surv_cancers})"
        else:
            surv_str = " with no significant survival associations"
            
        priority_label = "high-priority pan-cancer biomarker candidate" if result.cccs >= 0.7 else (
            "moderate-priority pan-cancer biomarker candidate" if result.cccs >= 0.4 else "low-priority candidate"
        )
        
        # Build statement
        statement = (
            f"{g} shows consistent {dir_word} across {result.n_cancers_significant}/{n_cancers} cancer types "
            f"({cancer_list}){surv_str}{confidence_suffix}. CCCS = {result.cccs:.2f} — {priority_label}."
        )
        return statement
