import logging
from typing import List, Tuple, Optional, Literal
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests

from oncofind.exceptions import AnalysisError, InsufficientSamplesError

logger = logging.getLogger(__name__)

# TCGA sample type codes that indicate primary tumor vs solid tissue normal
_TUMOR_SAMPLE_TYPES = {
    "Primary Tumor", "Recurrent Tumor", "Additional - New Primary",
    "Metastatic", "Additional Metastatic",
}
_NORMAL_SAMPLE_TYPES = {
    "Solid Tissue Normal", "Blood Derived Normal",
    "Bone Marrow Normal", "Buccal Cell Normal",
}


class DEGAnalyzer:
    """Runs Differential Expression Gene (DEG) analysis using PyDESeq2 or a t-test fallback."""

    def __init__(self, fdr_threshold: float = 0.05, log2fc_threshold: float = 1.0):
        self.fdr_threshold = fdr_threshold
        self.log2fc_threshold = log2fc_threshold

    def run_analysis(
        self,
        counts_df: pd.DataFrame,
        clinical_df: pd.DataFrame,
        groupby: str,
        group_a: str,
        group_b: str,
        method: str = "deseq2",
        mode: Literal["subtype_comparison", "tumor_vs_normal"] = "subtype_comparison",
        covariates: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Run DEG analysis comparing two sample groups.

        Args:
            counts_df: DataFrame where rows are samples and columns are gene symbols (raw counts).
            clinical_df: DataFrame containing sample clinical data.
            groupby: Column name in clinical_df for the comparison variable
                     (ignored when mode='tumor_vs_normal').
            group_a: Value of groupby for group A (numerator; ignored in tumor_vs_normal mode).
            group_b: Value of groupby for group B (denominator; ignored in tumor_vs_normal mode).
            method: 'deseq2' or 'ttest'.
            mode: 'subtype_comparison' (default) compares two clinical sub-groups.
                  'tumor_vs_normal' splits by TCGA sample_type column — Primary Tumor vs
                  Solid Tissue Normal. Requires matched normal samples in the dataset.

        Returns:
            DataFrame with columns: gene_symbol, log2FC, pvalue, padj, direction.
            log2FC is always numerator / denominator:
              subtype_comparison → group_a / group_b
              tumor_vs_normal    → Tumor / Normal  (positive = higher in tumor)
        """
        if mode == "tumor_vs_normal":
            return self._run_tumor_vs_normal(counts_df, clinical_df, method, covariates=covariates)

        # ── subtype_comparison mode (original behaviour) ──────────────────── #
        # Handle both indexed (sample_barcode as index) and column-based clinical DFs
        if clinical_df.index.name == "sample_barcode":
            clin_barcodes = clinical_df.index
            clinical_filtered = clinical_df[clin_barcodes.isin(counts_df.index)].copy()
        else:
            clinical_filtered = clinical_df[clinical_df["sample_barcode"].isin(counts_df.index)].copy()
        
        # Filter for the two comparison groups
        clinical_filtered = clinical_filtered[clinical_filtered[groupby].isin([group_a, group_b])]
        
        # Get samples for each group — use index if sample_barcode is the index
        if clinical_filtered.index.name == "sample_barcode":
            samples_a = clinical_filtered[clinical_filtered[groupby] == group_a].index.tolist()
            samples_b = clinical_filtered[clinical_filtered[groupby] == group_b].index.tolist()
        else:
            samples_a = clinical_filtered[clinical_filtered[groupby] == group_a]["sample_barcode"].tolist()
            samples_b = clinical_filtered[clinical_filtered[groupby] == group_b]["sample_barcode"].tolist()
        
        n_a, n_b = len(samples_a), len(samples_b)
        logger.info(f"Running DEG: Group A ({group_a}) N={n_a}, Group B ({group_b}) N={n_b}")
        
        if n_a < 3 or n_b < 3:
            raise InsufficientSamplesError(
                f"DEG analysis requires at least 3 samples per group. "
                f"Found: {group_a} = {n_a}, {group_b} = {n_b}"
            )
            
        # Align counts to clinical samples
        all_samples = samples_a + samples_b
        counts_aligned = counts_df.loc[all_samples].copy()
        
        # Set up design metadata
        if clinical_filtered.index.name == "sample_barcode":
            design_df = clinical_filtered.loc[all_samples]
        else:
            design_df = clinical_filtered.set_index("sample_barcode")
            design_df = design_df.loc[all_samples]
        
        # Force integer counts for Deseq2
        counts_aligned = counts_aligned.round().astype(int)
        
        if method.lower() == "deseq2":
            try:
                return self._run_deseq2(counts_aligned, design_df, groupby, group_a, group_b)
            except Exception as e:
                logger.warning(f"PyDESeq2 analysis failed or failed to converge: {e}. Falling back to t-test.")
                return self._run_ttest_fallback(counts_aligned, samples_a, samples_b, design_df, covariates=covariates)
        else:
            return self._run_ttest_fallback(counts_aligned, samples_a, samples_b, design_df, covariates=covariates)

    def _run_tumor_vs_normal(
        self,
        counts_df: pd.DataFrame,
        clinical_df: pd.DataFrame,
        method: str,
        covariates: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        DEG analysis comparing Primary Tumor vs Solid Tissue Normal samples.
        Uses the 'sample_type' column from the GDC clinical metadata.
        log2FC > 0 means higher expression in tumor relative to normal.
        """
        if "sample_type" not in clinical_df.columns:
            raise AnalysisError(
                "'sample_type' column not found in clinical data. "
                "This column is populated automatically when you run "
                "'oncofind download'. If using custom clinical data, add a "
                "'sample_type' column with values 'Primary Tumor' or "
                "'Solid Tissue Normal'."
            )

        clin = clinical_df[clinical_df["sample_barcode"].isin(counts_df.index)].copy()

        tumor_samples = clin[
            clin["sample_type"].isin(_TUMOR_SAMPLE_TYPES)
        ]["sample_barcode"].tolist()

        normal_samples = clin[
            clin["sample_type"].isin(_NORMAL_SAMPLE_TYPES)
        ]["sample_barcode"].tolist()

        n_tumor = len(tumor_samples)
        n_normal = len(normal_samples)

        logger.info(
            f"Tumor vs Normal DEG: {n_tumor} tumor samples, {n_normal} normal samples"
        )

        if n_tumor < 3:
            raise InsufficientSamplesError(
                f"Tumor vs Normal requires ≥ 3 tumor samples. Found: {n_tumor}. "
                "Download more samples or check that the expression matrix contains "
                "Primary Tumor barcodes (sample code 01A)."
            )
        if n_normal < 3:
            raise InsufficientSamplesError(
                f"Tumor vs Normal requires ≥ 3 normal samples. Found: {n_normal}. "
                "Most TCGA cohorts have ≤ 10% matched normals. "
                "Download more samples (oncofind download --n-samples 200) or use "
                "'--mode subtype_comparison' for cohorts without matched normals."
            )

        all_samples = tumor_samples + normal_samples
        counts_aligned = counts_df.loc[all_samples].copy().round().astype(int)

        # Build design DataFrame incorporating real clinical metadata columns
        if clinical_df.index.name == "sample_barcode":
            design_df = clinical_df.loc[all_samples].copy()
        else:
            design_df = clinical_df.set_index("sample_barcode").loc[all_samples].copy()
        design_df["sample_type_bin"] = (["Tumor"] * n_tumor + ["Normal"] * n_normal)

        if method.lower() == "deseq2":
            try:
                return self._run_deseq2(
                    counts_aligned, design_df,
                    groupby="sample_type_bin",
                    group_a="Tumor", group_b="Normal"
                )
            except Exception as e:
                logger.warning(
                    f"PyDESeq2 failed for tumor_vs_normal ({e}). Falling back to t-test."
                )
                return self._run_ttest_fallback(counts_aligned, tumor_samples, normal_samples, design_df, covariates=covariates)
        else:
            return self._run_ttest_fallback(counts_aligned, tumor_samples, normal_samples, design_df, covariates=covariates)

    def _run_deseq2(
        self,
        counts_df: pd.DataFrame,
        design_df: pd.DataFrame,
        groupby: str,
        group_a: str,
        group_b: str
    ) -> pd.DataFrame:
        """Execute PyDESeq2 negative binomial GLM analysis."""
        from pydeseq2.dds import DeseqDataSet
        from pydeseq2.ds import DeseqStats
        
        # Filter low count genes to speed up fitting and avoid convergence failures
        # Keep genes with at least 10 counts in at least 3 samples
        keep_genes = (counts_df >= 10).sum(axis=0) >= 3
        counts_filtered = counts_df.loc[:, keep_genes]
        
        if counts_filtered.shape[1] == 0:
            raise AnalysisError("No genes passed the pre-filtering criteria (counts >= 10 in at least 3 samples).")
            
        # Convert design column to categorical
        design_df[groupby] = pd.Categorical(design_df[groupby], categories=[group_b, group_a])
        
        dds = DeseqDataSet(
            counts=counts_filtered,
            metadata=design_df,
            design_factor=groupby,
            refit_cooks=True,
            quiet=True
        )
        
        # Run DESeq2 pipeline
        dds.deseq2()
        
        # Compute stats (contrast: [factor, numerator, denominator])
        stat_res = DeseqStats(dds, contrast=[groupby, group_a, group_b], quiet=True)
        stat_res.summary()
        
        res_df = stat_res.results_df
        
        # Build output structure
        results = pd.DataFrame(index=counts_df.columns)
        results["log2FC"] = res_df["log2FoldChange"]
        results["pvalue"] = res_df["pvalue"]
        results["padj"] = res_df["padj"]
        
        # Handle genes filtered out by DESeq2 or that didn't pass preprocessing
        results["log2FC"] = results["log2FC"].fillna(0.0)
        results["pvalue"] = results["pvalue"].fillna(1.0)
        results["padj"] = results["padj"].fillna(1.0)
        
        # Assign directions
        results["direction"] = "ns"
        results.loc[(results["padj"] < self.fdr_threshold) & (results["log2FC"] > self.log2fc_threshold), "direction"] = "up"
        results.loc[(results["padj"] < self.fdr_threshold) & (results["log2FC"] < -self.log2fc_threshold), "direction"] = "down"
        
        results.index.name = "gene_symbol"
        return results.reset_index()

    def _run_ttest_fallback(
        self,
        counts_df: pd.DataFrame,
        samples_a: List[str],
        samples_b: List[str],
        design_df: Optional[pd.DataFrame] = None,
        covariates: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Run Welch's t-test or multiple regression (OLS) fallback on log2(CPM + 1) normalized counts.
        Controls for age and sex covariates if present in design_df.
        Vectorized across all genes for extremely high performance (seconds vs minutes).
        """
        # 1. CPM Normalization: Counts / Sample Library Size * 1,000,000
        library_sizes = counts_df.sum(axis=1)
        library_sizes = library_sizes.replace(0, 1.0)
        
        cpm_df = counts_df.div(library_sizes, axis=0) * 1e6
        log_cpm = np.log2(cpm_df + 1)
        
        # 2. Identify potential covariates
        resolved_covs = []
        ols_df = None
        if design_df is not None:
            ols_df = pd.DataFrame(index=counts_df.index)
            group_series = pd.Series(0.0, index=counts_df.index)
            group_series.loc[samples_a] = 1.0
            ols_df["group"] = group_series
            
            covs_to_process = covariates if covariates is not None else ["age_at_index", "gender"]
            
            for cov in covs_to_process:
                if cov not in design_df.columns:
                    if covariates is not None:
                        logger.warning(f"Covariate '{cov}' not found in design clinical columns.")
                    continue
                
                col_series = design_df[cov]
                
                is_numeric = False
                try:
                    num_col = pd.to_numeric(col_series, errors="coerce")
                    if num_col.notna().sum() >= 2 and num_col.nunique() > 1:
                        is_numeric = True
                except Exception:
                    pass
                
                if is_numeric:
                    median_val = num_col.median()
                    if pd.isna(median_val):
                        median_val = 0.0
                    col_name = f"{cov}_num"
                    ols_df[col_name] = num_col.fillna(median_val).astype(float)
                    resolved_covs.append(col_name)
                else:
                    clean_col = col_series.astype(str).str.lower().str.strip()
                    clean_col = clean_col.replace({"not reported": np.nan, "unknown": np.nan, "nan": np.nan, "none": np.nan})
                    
                    filled_col = clean_col.fillna("missing")
                    if filled_col.nunique() >= 2:
                        dummies = pd.get_dummies(filled_col, prefix=cov, drop_first=True).astype(float)
                        for d_col in dummies.columns:
                            n_ones = dummies[d_col].sum()
                            n_zeros = len(dummies) - n_ones
                            if n_ones >= 3 and n_zeros >= 3:
                                ols_df[d_col] = dummies[d_col]
                                resolved_covs.append(d_col)

        pvalues = None
        if resolved_covs and ols_df is not None:
            # Vectorized OLS regression: Y = X * beta + error
            try:
                import statsmodels.api as sm
                X_df = sm.add_constant(ols_df[["group"] + resolved_covs].astype(float))
                X = X_df.values
                Y = log_cpm.values  # Shape: (N, G)
                
                if X.shape[0] > X.shape[1] and len(np.unique(X[:, 1])) > 1:
                    XtX = X.T @ X
                    XtX_inv = np.linalg.pinv(XtX)
                    beta = XtX_inv @ X.T @ Y  # Shape: (P, G)
                    
                    residuals = Y - (X @ beta)  # Shape: (N, G)
                    rss = np.sum(residuals**2, axis=0)  # Shape: (G,)
                    
                    df_resid = X.shape[0] - X.shape[1]
                    s2 = rss / df_resid
                    
                    group_idx = X_df.columns.get_loc("group")
                    se_group = np.sqrt(s2 * XtX_inv[group_idx, group_idx])
                    
                    se_group = np.where(se_group == 0, 1e-12, se_group)
                    
                    t_stats = beta[group_idx, :] / se_group
                    pvalues = 2 * stats.t.sf(np.abs(t_stats), df=df_resid)
                    pvalues = np.nan_to_num(pvalues, nan=1.0)
            except Exception as e:
                logger.warning(f"Vectorized OLS failed ({e}). Falling back to vectorized Welch's t-test.")
                pvalues = None

        if pvalues is None:
            # Vectorized Welch's t-test
            vals_a = log_cpm.loc[samples_a].values  # Shape: (N_a, G)
            vals_b = log_cpm.loc[samples_b].values  # Shape: (N_b, G)
            
            n_a = len(samples_a)
            n_b = len(samples_b)
            
            mean_a = np.mean(vals_a, axis=0)
            mean_b = np.mean(vals_b, axis=0)
            
            var_a = np.var(vals_a, axis=0, ddof=1)
            var_b = np.var(vals_b, axis=0, ddof=1)
            
            var_a = np.where(var_a == 0, 1e-12, var_a)
            var_b = np.where(var_b == 0, 1e-12, var_b)
            
            se = np.sqrt(var_a / n_a + var_b / n_b)
            t_stats = (mean_a - mean_b) / se
            
            num = (var_a / n_a + var_b / n_b)**2
            den = (var_a / n_a)**2 / (n_a - 1) + (var_b / n_b)**2 / (n_b - 1)
            df = num / den
            
            pvalues = 2 * stats.t.sf(np.abs(t_stats), df=df)
            pvalues = np.nan_to_num(pvalues, nan=1.0)

        # Compute log2 fold change of mean normalized expression
        mean_cpm_a = np.mean(cpm_df.loc[samples_a].values, axis=0)
        mean_cpm_b = np.mean(cpm_df.loc[samples_b].values, axis=0)
        
        log2fcs = np.log2((mean_cpm_a + 1.0) / (mean_cpm_b + 1.0))
        log2fcs = np.clip(log2fcs, -10.0, 10.0)

        res_df = pd.DataFrame({
            "gene_symbol": counts_df.columns,
            "log2FC": log2fcs.astype(float),
            "pvalue": pvalues.astype(float)
        })
        
        # BH adjustment
        pvals = res_df["pvalue"].values
        _, padjs, _, _ = multipletests(pvals, alpha=self.fdr_threshold, method="fdr_bh")
        res_df["padj"] = padjs
        
        # Determine direction
        res_df["direction"] = "ns"
        res_df.loc[(res_df["padj"] < self.fdr_threshold) & (res_df["log2FC"] > self.log2fc_threshold), "direction"] = "up"
        res_df.loc[(res_df["padj"] < self.fdr_threshold) & (res_df["log2FC"] < -self.log2fc_threshold), "direction"] = "down"
        
        return res_df
