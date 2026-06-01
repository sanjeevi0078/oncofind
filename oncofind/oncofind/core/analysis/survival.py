import logging
from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test, multivariate_logrank_test

logger = logging.getLogger(__name__)


@dataclass
class SurvivalResult:
    gene_symbol: str
    split_method: str
    threshold_value: float
    p_value: float
    n_high: int
    n_low: int
    median_survival_high: Optional[float]
    median_survival_low: Optional[float]
    high_group_barcodes: list[str]
    low_group_barcodes: list[str]
    km_data: Dict[str, Any]  # for plotting


class SurvivalAnalyzer:
    """Performs Kaplan-Meier survival curve fitting and log-rank statistical testing."""

    PERCENTILES_TO_TEST = list(range(10, 91, 5))

    def __init__(self, p_value_threshold: float = 0.05):
        self.p_value_threshold = p_value_threshold

    def analyze(
        self,
        expression_df: pd.DataFrame,
        clinical_df: pd.DataFrame,
        gene_symbol: str,
        split_method: str = "median",
        p_value_only: bool = False
    ) -> SurvivalResult:
        """
        Run Kaplan-Meier estimation and log-rank test for overall survival.
        
        Args:
            expression_df: DataFrame with sample_barcode index and expression of gene_symbol as column.
            clinical_df: DataFrame containing clinical annotations (survival_days, censored).
            gene_symbol: Gene symbol to analyze.
            split_method: 'median', 'quartile', or 'optimal'.
        """
        # Align clinical and expression data
        merged = clinical_df.merge(expression_df[[gene_symbol]], on="sample_barcode")
        
        # Filter for rows that have valid survival data and expression values
        merged = merged.dropna(subset=["survival_days", "censored", gene_symbol])
        merged = merged[merged["survival_days"] >= 0]
        
        n_total = merged.shape[0]
        if n_total < 10:
            raise ValueError(f"Too few samples with survival data for analysis (N={n_total}).")

        # Determine threshold and split samples
        expr_values = merged[gene_symbol].values
        
        is_multi_group = False
        fallback_to_median = False
        
        # 1. Split samples into groups
        if split_method.lower() in ("tertile", "tertiles"):
            is_multi_group = True
            t33 = float(np.percentile(expr_values, 100.0 / 3.0))
            t67 = float(np.percentile(expr_values, 200.0 / 3.0))
            threshold = (t33 + t67) / 2.0
            
            merged["group"] = "T2"
            merged.loc[merged[gene_symbol] < t33, "group"] = "T1"
            merged.loc[merged[gene_symbol] >= t67, "group"] = "T3"
            
            group_keys = ["T1", "T2", "T3"]
            key_mapping = {"T1": "low", "T3": "high", "T2": "T2"}
            labels = {"T1": "T1 (Low)", "T2": "T2 (Med)", "T3": "T3 (High)"}
            
            # Check group sizes
            for gk in group_keys:
                if (merged["group"] == gk).sum() < 3:
                    fallback_to_median = True
                    break
                    
        elif split_method.lower() in ("quartile_4way", "quartiles"):
            is_multi_group = True
            q25 = float(np.percentile(expr_values, 25))
            q50 = float(np.percentile(expr_values, 50))
            q75 = float(np.percentile(expr_values, 75))
            threshold = q50
            
            merged["group"] = "Q2"
            merged.loc[merged[gene_symbol] < q25, "group"] = "Q1"
            merged.loc[(merged[gene_symbol] >= q25) & (merged[gene_symbol] < q50), "group"] = "Q2"
            merged.loc[(merged[gene_symbol] >= q50) & (merged[gene_symbol] < q75), "group"] = "Q3"
            merged.loc[merged[gene_symbol] >= q75, "group"] = "Q4"
            
            group_keys = ["Q1", "Q2", "Q3", "Q4"]
            key_mapping = {"Q1": "low", "Q4": "high", "Q2": "Q2", "Q3": "Q3"}
            labels = {"Q1": "Q1 (Low)", "Q2": "Q2 (Mid-Low)", "Q3": "Q3 (Mid-High)", "Q4": "Q4 (High)"}
            
            # Check group sizes
            for gk in group_keys:
                if (merged["group"] == gk).sum() < 3:
                    fallback_to_median = True
                    break
                    
        else:
            is_multi_group = False
            if split_method.lower() == "median":
                threshold = float(np.median(expr_values))
                high_mask = expr_values >= threshold
                low_mask = expr_values < threshold
            elif split_method.lower() == "quartile":
                q25 = float(np.percentile(expr_values, 25))
                q75 = float(np.percentile(expr_values, 75))
                
                # For quartiles, we exclude the middle 50%
                merged = merged[(merged[gene_symbol] >= q75) | (merged[gene_symbol] <= q25)]
                expr_values = merged[gene_symbol].values
                threshold = (q25 + q75) / 2.0
                high_mask = expr_values >= q75
                low_mask = expr_values <= q25
            elif split_method.lower() == "optimal":
                threshold, high_mask, low_mask = self._find_optimal_split(merged, gene_symbol)
            else:
                raise ValueError(f"Unknown split method: {split_method}")
                
            merged["group"] = np.where(high_mask, "high", "low")
            group_keys = ["low", "high"]
            key_mapping = {"low": "low", "high": "high"}
            labels = {"low": "Low Expr", "high": "High Expr"}
            
            if (merged["group"] == "low").sum() < 3 or (merged["group"] == "high").sum() < 3:
                fallback_to_median = True

        if fallback_to_median:
            logger.debug("One group is too small in survival split. Falling back to median split.")
            is_multi_group = False
            threshold = float(np.median(merged[gene_symbol].values))
            high_mask = merged[gene_symbol].values >= threshold
            low_mask = merged[gene_symbol].values < threshold
            merged["group"] = np.where(high_mask, "high", "low")
            group_keys = ["low", "high"]
            key_mapping = {"low": "low", "high": "high"}
            labels = {"low": "Low Expr", "high": "High Expr"}

        # Resolve group barcodes for counts/results
        barcodes_by_key = {}
        for gk in group_keys:
            target_key = key_mapping[gk]
            barcodes_by_key[target_key] = merged[merged["group"] == gk]["sample_barcode"].tolist()

        # Run log-rank test
        if is_multi_group:
            lr_results = multivariate_logrank_test(
                merged["survival_days"],
                groups=merged["group"],
                event_observed=1 - merged["censored"]
            )
            p_value = float(lr_results.p_value)
        else:
            merged_high = merged[merged["group"] == "high"]
            merged_low = merged[merged["group"] == "low"]
            lr_results = logrank_test(
                merged_high["survival_days"],
                merged_low["survival_days"],
                event_observed_A=1 - merged_high["censored"],
                event_observed_B=1 - merged_low["censored"]
            )
            p_value = float(lr_results.p_value)
            
            if split_method.lower() == "optimal":
                n_tests = len(self.PERCENTILES_TO_TEST)
                p_value = min(1.0, p_value * float(n_tests))

        if p_value_only:
            return SurvivalResult(
                gene_symbol=gene_symbol,
                split_method=split_method,
                threshold_value=threshold,
                p_value=p_value,
                n_high=len(barcodes_by_key.get("high", [])),
                n_low=len(barcodes_by_key.get("low", [])),
                median_survival_high=None,
                median_survival_low=None,
                high_group_barcodes=barcodes_by_key.get("high", []),
                low_group_barcodes=barcodes_by_key.get("low", []),
                km_data={}
            )

        # Fit Kaplan-Meier for all groups
        km_data = {}
        median_survivals = {}
        
        for gk in group_keys:
            merged_g = merged[merged["group"] == gk]
            n_g = merged_g.shape[0]
            
            kmf = KaplanMeierFitter()
            kmf.fit(
                merged_g["survival_days"],
                event_observed=1 - merged_g["censored"],
                label=labels[gk]
            )
            
            # Median survival time
            med_time = kmf.median_survival_time_
            median_survivals[gk] = float(med_time) if not np.isnan(med_time) else None
            
            target_key = key_mapping[gk]
            
            try:
                surv_3yr = float(kmf.predict(1095))
            except Exception:
                surv_3yr = None
                
            try:
                surv_5yr = float(kmf.predict(1825))
            except Exception:
                surv_5yr = None
                
            km_data[target_key] = {
                "timeline": kmf.survival_function_.index.tolist(),
                "survival": kmf.survival_function_[labels[gk]].tolist(),
                "ci_lower": kmf.confidence_interval_[f"{labels[gk]}_lower_0.95"].tolist(),
                "ci_upper": kmf.confidence_interval_[f"{labels[gk]}_upper_0.95"].tolist(),
                "label": labels[gk],
                "n": n_g,
                "median_survival": median_survivals[gk],
                "surv_3yr": surv_3yr,
                "surv_5yr": surv_5yr,
                "barcodes": barcodes_by_key[target_key]
            }

        # Calculate high/low medians for backwards-compatibility
        med_high_key = "T3" if "T3" in median_survivals else ("Q4" if "Q4" in median_survivals else "high")
        med_low_key = "T1" if "T1" in median_survivals else ("Q1" if "Q1" in median_survivals else "low")
        
        median_high = median_survivals[med_high_key]
        median_low = median_survivals[med_low_key]

        return SurvivalResult(
            gene_symbol=gene_symbol,
            split_method=split_method,
            threshold_value=threshold,
            p_value=p_value,
            n_high=len(barcodes_by_key.get("high", [])),
            n_low=len(barcodes_by_key.get("low", [])),
            median_survival_high=median_high,
            median_survival_low=median_low,
            high_group_barcodes=barcodes_by_key.get("high", []),
            low_group_barcodes=barcodes_by_key.get("low", []),
            km_data=km_data
        )

    def _find_optimal_split(self, df: pd.DataFrame, gene: str) -> Tuple[float, np.ndarray, np.ndarray]:
        """
        Finds the expression split threshold that maximizes the log-rank test statistic.
        Tests percentiles from 10th to 90th.
        """
        expr_values = df[gene].values
        best_p = 1.0
        best_stat = -1.0
        best_threshold = float(np.median(expr_values))
        
        # Test every percentile defined in class config
        for pct in self.PERCENTILES_TO_TEST:
            threshold = float(np.percentile(expr_values, pct))
            high_mask = expr_values >= threshold
            low_mask = expr_values < threshold
            
            # Ensure group sizes are reasonable (at least 5 samples per group)
            if np.sum(high_mask) < 5 or np.sum(low_mask) < 5:
                continue
                
            lr = logrank_test(
                df[high_mask]["survival_days"],
                df[low_mask]["survival_days"],
                event_observed_A=1 - df[high_mask]["censored"],
                event_observed_B=1 - df[low_mask]["censored"]
            )
            
            # We want to maximize the test statistic (i.e. minimize the p-value)
            if lr.test_statistic > best_stat:
                best_stat = lr.test_statistic
                best_p = lr.p_value
                best_threshold = threshold

        high_mask = expr_values >= best_threshold
        low_mask = expr_values < best_threshold
        return best_threshold, high_mask, low_mask
