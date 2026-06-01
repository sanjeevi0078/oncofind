import pytest
import numpy as np
import pandas as pd
from scipy import stats

from oncofind.core.data.expression_store import ExpressionStore
from oncofind.core.data.clinical_store import ClinicalStore
from oncofind.core.analysis.deg import DEGAnalyzer
from oncofind.core.analysis.survival import SurvivalAnalyzer
from oncofind.core.analysis.cccs import CrossCancerConsistencyScorer, CancerResult


def test_cccs_known_genes(mock_data_dir):
    """
    Validate CCCS logic against biological controls:
    - TP53 (pan-cancer oncogene/tumor suppressor) should score > 0.7
    - ESR1 (breast cancer specific) should score < 0.3 on pan-cancer analysis.
    """
    expr_store = ExpressionStore(mock_data_dir)
    clin_store = ClinicalStore(mock_data_dir)
    
    deg_analyzer = DEGAnalyzer()
    survival_analyzer = SurvivalAnalyzer()
    scorer = CrossCancerConsistencyScorer()
    
    cancers = ["BRCA", "LUAD", "COAD"]
    genes_to_test = ["TP53", "MYC", "ESR1", "E2F1"]
    
    # Store computed scores for correlation test later
    scores = {}
    
    for gene in genes_to_test:
        cancer_results = []
        for cancer in cancers:
            # Query expression (retrieve all genes for proper library size computation)
            all_genes = ["TP53", "MYC", "EGFR", "ESR1", "BRCA1", "CDK4", "MDM2", "E2F1"] + [f"GENE_{i}" for i in range(100)]
            expr_df = expr_store.query_expression(cancer, all_genes)
            clinical_df = clin_store.get_clinical_df(cancer)
            
            # Find grouping variable (default is ER_status for BRCA, smoking_status for LUAD, msi_status for COAD)
            if cancer == "BRCA":
                groupby = "ER_status"
                group_a, group_b = "Positive", "Negative"
            elif cancer == "LUAD":
                groupby = "smoking_status"
                group_a, group_b = "Smoker", "Non-smoker"
            else:
                groupby = "msi_status"
                group_a, group_b = "MSI-H", "MSS"
            
            # 1. Run DEG
            deg_res = deg_analyzer.run_analysis(
                counts_df=expr_df,
                clinical_df=clinical_df,
                groupby=groupby,
                group_a=group_a,
                group_b=group_b,
                method="ttest"
            )
            gene_deg = deg_res[deg_res["gene_symbol"] == gene].iloc[0]
            
            # 2. Run Survival
            try:
                survival_res = survival_analyzer.analyze(expr_df, clinical_df, gene, split_method="median")
                survival_p = survival_res.p_value
            except Exception:
                survival_p = None
                
            # Create CancerResult
            cancer_results.append(CancerResult(
                cancer_type=cancer,
                log2fc=gene_deg["log2FC"],
                padj=gene_deg["padj"],
                direction=gene_deg["direction"],
                survival_pvalue=survival_p
            ))
            
        # 3. Compute CCCS
        cccs_res = scorer.compute(gene_symbol=gene, gene_id=f"MOCK_{gene}", cancer_results=cancer_results)
        scores[gene] = cccs_res.cccs
        
        # Log findings
        print(f"Gene {gene}: CCCS = {cccs_res.cccs:.4f}. Interpretation: {cccs_res.interpretation}")

    # Validation 1: TP53 should score high (> 0.7)
    # TP53 in our mock data is consistently downregulated and strongly associated with survival
    assert scores["TP53"] >= 0.7, f"TP53 CCCS was only {scores['TP53']}"
    
    # Validation 2: ESR1 should score low (< 0.3)
    # ESR1 in our mock data is only active in BRCA, so its pan-cancer score should be low
    assert scores["ESR1"] < 0.3, f"ESR1 CCCS was {scores['ESR1']}"


def test_cccs_citation_correlation():
    """
    Validate that the CCCS score correctly ranks genes based on the strength
    and consistency of their signals across 50 simulated gene profiles.
    """
    scorer = CrossCancerConsistencyScorer()
    np.random.seed(42)
    
    genes_data = []
    cancers = ["BRCA", "LUAD", "COAD", "STAD", "OV"]
    
    # Generate 50 simulated gene profiles with varying signal strengths
    for i in range(50):
        # We grade the strength of the signal from 0 (pure noise) to 1 (strong pan-cancer driver)
        signal_strength = i / 49.0
        
        cancer_results = []
        for cancer in cancers:
            # Upregulated or downregulated with probability proportional to signal strength
            if np.random.random() < signal_strength:
                direction = "up" if np.random.random() > 0.3 else "down"
                log2fc = float(np.random.uniform(0.5, 3.0)) * (1 if direction == "up" else -1)
                padj = float(np.random.uniform(1e-6, 0.04))
                # Survival significant with probability proportional to signal strength
                surv_p = float(np.random.uniform(1e-5, 0.04)) if np.random.random() < signal_strength else float(np.random.uniform(0.06, 0.99))
            else:
                direction = "ns"
                log2fc = float(np.random.uniform(-0.4, 0.4))
                padj = float(np.random.uniform(0.06, 0.99))
                surv_p = float(np.random.uniform(0.06, 0.99))
                
            cancer_results.append(CancerResult(
                cancer_type=cancer,
                log2fc=log2fc,
                padj=padj,
                direction=direction,
                survival_pvalue=surv_p
            ))
            
        res = scorer.compute(f"SIM_GENE_{i}", f"ENSG_{i:04d}", cancer_results)
        genes_data.append({
            "gene": f"SIM_GENE_{i}",
            "cccs": res.cccs,
            "signal_strength": signal_strength,
            "n_sig": res.n_cancers_significant,
            "n_surv": res.n_cancers_survival_significant
        })
        
    df = pd.DataFrame(genes_data)
    
    # Assert that computed CCCS correlates strongly with the true underlying signal strength
    correlation, p_value = stats.spearmanr(df["cccs"], df["signal_strength"])
    print(f"CCCS vs Signal Strength Spearman rho: {correlation:.4f} (p = {p_value:.4f})")
    
    assert correlation >= 0.80, f"CCCS does not correlate strongly with signal strength (rho = {correlation:.4f})"
    assert p_value < 0.01, f"Correlation is not statistically significant (p = {p_value:.4f})"
    
    # Assert that CCCS increases monotonically with the number of significant cancers and survival associations
    corr_sig, _ = stats.spearmanr(df["cccs"], df["n_sig"])
    corr_surv, _ = stats.spearmanr(df["cccs"], df["n_surv"])
    assert corr_sig >= 0.75
    assert corr_surv >= 0.75

