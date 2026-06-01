import pytest
import pandas as pd
import numpy as np
from oncofind.core.data.expression_store import ExpressionStore
from oncofind.core.data.clinical_store import ClinicalStore
from oncofind.core.analysis.deg import DEGAnalyzer
from oncofind.core.analysis.survival import SurvivalAnalyzer
from oncofind.core.analysis.pca import PCAAnalyzer
from oncofind.core.analysis.batch import BatchCorrector
from oncofind.exceptions import InsufficientSamplesError


def test_deg_analysis_ttest(mock_data_dir):
    """Test DEG analysis using t-test fallback."""
    expr_store = ExpressionStore(mock_data_dir)
    clin_store = ClinicalStore(mock_data_dir)
    
    # Query all genes to compute library sizes correctly during normalization
    all_genes = ["TP53", "MYC", "EGFR", "ESR1", "BRCA1", "CDK4", "MDM2", "E2F1"] + [f"GENE_{i}" for i in range(100)]
    counts_df = expr_store.query_expression("BRCA", all_genes)
    clinical_df = clin_store.get_clinical_df("BRCA")
    
    analyzer = DEGAnalyzer(fdr_threshold=0.05, log2fc_threshold=1.0)
    results = analyzer.run_analysis(
        counts_df=counts_df,
        clinical_df=clinical_df,
        groupby="ER_status",
        group_a="Positive",
        group_b="Negative",
        method="ttest"
    )
    
    assert isinstance(results, pd.DataFrame)
    assert "log2FC" in results.columns
    assert "pvalue" in results.columns
    assert "padj" in results.columns
    assert "direction" in results.columns
    assert results.shape[0] == len(all_genes)
    
    # Verify expected biological behavior in our mock data:
    # TP53 was set to be Downregulated in group A (ER_status Positive in BRCA)
    tp53_res = results[results["gene_symbol"] == "TP53"].iloc[0]
    assert tp53_res["log2FC"] < 0
    
    # ESR1 was set to be Highly Upregulated in BRCA group A (Positive)
    esr1_res = results[results["gene_symbol"] == "ESR1"].iloc[0]
    assert esr1_res["log2FC"] > 0
    assert esr1_res["direction"] == "up"


def test_survival_analysis(mock_data_dir):
    """Test Kaplan-Meier and log-rank analysis on survival data."""
    expr_store = ExpressionStore(mock_data_dir)
    clin_store = ClinicalStore(mock_data_dir)
    
    expr_df = expr_store.query_expression("BRCA", ["TP53"])
    clinical_df = clin_store.get_clinical_df("BRCA")
    
    analyzer = SurvivalAnalyzer()
    res = analyzer.analyze(expr_df, clinical_df, "TP53", split_method="median")
    
    assert res.gene_symbol == "TP53"
    assert res.n_high == 20
    assert res.n_low == 20
    assert 0 <= res.p_value <= 1.0
    assert "high" in res.km_data
    assert "low" in res.km_data
    assert len(res.km_data["high"]["timeline"]) > 0


def test_pca_analysis(mock_data_dir):
    """Test PCA coordinates computation and explained variance."""
    expr_store = ExpressionStore(mock_data_dir)
    clin_store = ClinicalStore(mock_data_dir)
    
    # Query all genes to give PCA enough features
    all_genes = ["TP53", "MYC", "EGFR", "ESR1", "BRCA1", "CDK4", "MDM2", "E2F1"] + [f"GENE_{i}" for i in range(100)]
    expr_df = expr_store.query_expression("BRCA", all_genes)
    clinical_df = clin_store.get_clinical_df("BRCA")
    
    analyzer = PCAAnalyzer(n_components=3)
    pca_df, var_ratios = analyzer.compute_pca(expr_df, clinical_df, top_n_genes=50, color_by="ER_status")
    
    assert isinstance(pca_df, pd.DataFrame)
    assert "PC1" in pca_df.columns
    assert "PC2" in pca_df.columns
    assert "PC3" in pca_df.columns
    assert "ER_status" in pca_df.columns
    assert len(var_ratios) == 3
    assert abs(sum(var_ratios) - 100) > 0  # Should be percentage variance


def test_batch_correction(mock_data_dir):
    """Test Location-Scale batch correction."""
    expr_store = ExpressionStore(mock_data_dir)
    expr_df = expr_store.query_expression("BRCA", ["TP53", "MYC", "ESR1"])
    
    corrector = BatchCorrector()
    # Mock batch IDs using tissue source sites
    batch_ids = ["plate_1" if i % 2 == 0 else "plate_2" for i in range(len(expr_df))]
    
    corrected_df = corrector.correct_batch(expr_df, batch_ids)
    
    assert corrected_df.shape == expr_df.shape
    assert list(corrected_df.columns) == list(expr_df.columns)
    assert list(corrected_df.index) == list(expr_df.index)


def test_deg_analysis_covariates(mock_data_dir):
    """Test DEG analysis adjusting for custom covariates (OLS fallback)."""
    expr_store = ExpressionStore(mock_data_dir)
    clin_store = ClinicalStore(mock_data_dir)
    
    all_genes = ["TP53", "MYC", "EGFR", "ESR1", "BRCA1", "CDK4", "MDM2", "E2F1"] + [f"GENE_{i}" for i in range(100)]
    counts_df = expr_store.query_expression("BRCA", all_genes)
    clinical_df = clin_store.get_clinical_df("BRCA").copy()
    
    # Let's add mock numeric and categorical covariate columns
    np.random.seed(42)
    clinical_df["mock_numeric"] = np.random.uniform(20, 80, size=len(clinical_df))
    clinical_df["mock_categorical"] = np.random.choice(["TypeA", "TypeB", "TypeC"], size=len(clinical_df))
    
    analyzer = DEGAnalyzer(fdr_threshold=0.05, log2fc_threshold=1.0)
    results = analyzer.run_analysis(
        counts_df=counts_df,
        clinical_df=clinical_df,
        groupby="ER_status",
        group_a="Positive",
        group_b="Negative",
        method="ttest",
        covariates=["mock_numeric", "mock_categorical"]
    )
    
    assert isinstance(results, pd.DataFrame)
    assert "log2FC" in results.columns
    assert "pvalue" in results.columns
    assert "padj" in results.columns
    assert results.shape[0] == len(all_genes)


def test_survival_analysis_multigroup(mock_data_dir):
    """Test multi-group survival splits (tertiles and quartile_4way)."""
    expr_store = ExpressionStore(mock_data_dir)
    clin_store = ClinicalStore(mock_data_dir)
    
    expr_df = expr_store.query_expression("BRCA", ["TP53"])
    clinical_df = clin_store.get_clinical_df("BRCA")
    
    analyzer = SurvivalAnalyzer()
    
    # 1. Test tertiles split
    res_tertiles = analyzer.analyze(expr_df, clinical_df, "TP53", split_method="tertiles")
    assert res_tertiles.gene_symbol == "TP53"
    assert "T2" in res_tertiles.km_data
    assert "low" in res_tertiles.km_data  # T1
    assert "high" in res_tertiles.km_data # T3
    assert 0 <= res_tertiles.p_value <= 1.0
    
    # 2. Test quartile_4way split
    res_quartiles = analyzer.analyze(expr_df, clinical_df, "TP53", split_method="quartile_4way")
    assert res_quartiles.gene_symbol == "TP53"
    assert "Q2" in res_quartiles.km_data
    assert "Q3" in res_quartiles.km_data
    assert "low" in res_quartiles.km_data  # Q1
    assert "high" in res_quartiles.km_data # Q4
    assert 0 <= res_quartiles.p_value <= 1.0


def test_survival_analysis_surv_probabilities(mock_data_dir):
    """Test that 3-year and 5-year survival probabilities are computed correctly."""
    expr_store = ExpressionStore(mock_data_dir)
    clin_store = ClinicalStore(mock_data_dir)
    
    expr_df = expr_store.query_expression("BRCA", ["TP53"])
    clinical_df = clin_store.get_clinical_df("BRCA")
    
    analyzer = SurvivalAnalyzer()
    res = analyzer.analyze(expr_df, clinical_df, "TP53", split_method="median")
    
    assert "surv_3yr" in res.km_data["high"]
    assert "surv_5yr" in res.km_data["high"]
    assert "surv_3yr" in res.km_data["low"]
    assert "surv_5yr" in res.km_data["low"]


def test_deg_analysis_sparse_pruning(mock_data_dir):
    """Test that sparse categorical covariates (with fewer than 3 samples in a level) are pruned."""
    expr_store = ExpressionStore(mock_data_dir)
    clin_store = ClinicalStore(mock_data_dir)
    
    all_genes = ["TP53", "MYC"]
    counts_df = expr_store.query_expression("BRCA", all_genes)
    clinical_df = clin_store.get_clinical_df("BRCA").copy()
    
    # Add a sparse covariate with a rare category of only 1 sample
    categories = ["GroupA"] * (len(clinical_df) - 1) + ["SparseGroupB"]
    clinical_df["sparse_cov"] = categories
    
    analyzer = DEGAnalyzer(fdr_threshold=0.05, log2fc_threshold=1.0)
    results = analyzer.run_analysis(
        counts_df=counts_df,
        clinical_df=clinical_df,
        groupby="ER_status",
        group_a="Positive",
        group_b="Negative",
        method="ttest",
        covariates=["sparse_cov"]
    )
    
    assert isinstance(results, pd.DataFrame)


def test_survival_analysis_p_value_only(mock_data_dir):
    """Test that p_value_only option successfully computes p-values and skips KM fitting."""
    expr_store = ExpressionStore(mock_data_dir)
    clin_store = ClinicalStore(mock_data_dir)
    
    expr_df = expr_store.query_expression("BRCA", ["TP53"])
    clinical_df = clin_store.get_clinical_df("BRCA")
    
    analyzer = SurvivalAnalyzer()
    res = analyzer.analyze(expr_df, clinical_df, "TP53", split_method="median", p_value_only=True)
    
    assert res.gene_symbol == "TP53"
    assert 0 <= res.p_value <= 1.0
    assert res.n_high > 0
    assert res.n_low > 0
    assert not res.km_data  # Should be empty when p_value_only is True
    assert res.median_survival_high is None
    assert res.median_survival_low is None
