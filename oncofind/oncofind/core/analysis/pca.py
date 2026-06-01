import logging
from typing import List, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class PCAAnalyzer:
    """Performs Principal Component Analysis (PCA) on expression matrices."""

    def __init__(self, n_components: int = 5):
        self.n_components = n_components

    def compute_pca(
        self,
        expression_df: pd.DataFrame,
        clinical_df: pd.DataFrame,
        top_n_genes: int = 500,
        color_by: Optional[str] = None
    ) -> Tuple[pd.DataFrame, List[float]]:
        """
        Run PCA on expression data for top N most variable genes.
        
        Args:
            expression_df: DataFrame with sample_barcode index and genes as columns.
            clinical_df: DataFrame with patient clinical annotations.
            top_n_genes: Number of highly variable genes to use.
            color_by: Clinical variable name to join for plotting.
            
        Returns:
            Tuple of:
            - DataFrame with PC1, PC2, ..., PC5 and join fields.
            - List of explained variance ratios (percentages).
        """
        # Align clinical and expression
        samples = list(set(expression_df.index).intersection(clinical_df["sample_barcode"]))
        if len(samples) < 5:
            raise ValueError(f"Too few samples aligned for PCA (N={len(samples)})")

        expr_aligned = expression_df.loc[samples].copy()
        
        # Identify top N most variable genes (by variance)
        variances = expr_aligned.var(axis=0)
        top_genes = variances.nlargest(min(top_n_genes, len(variances))).index
        
        # Subset expression
        data = expr_aligned[top_genes].values
        
        # Standardize data (z-score scale along features/columns)
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data)
        
        # Run PCA
        pca = PCA(n_components=min(self.n_components, data_scaled.shape[0], data_scaled.shape[1]))
        pca_coords = pca.fit_transform(data_scaled)
        
        # Explained variance percentages
        var_ratios = [float(ratio * 100) for ratio in pca.explained_variance_ratio_]
        
        # Build coordinates DataFrame
        pc_cols = [f"PC{i+1}" for i in range(pca_coords.shape[1])]
        pca_df = pd.DataFrame(pca_coords, columns=pc_cols, index=samples)
        pca_df.index.name = "sample_barcode"
        
        # Join with clinical
        clinical_aligned = clinical_df.set_index("sample_barcode").loc[samples]
        
        # Join color_by column if requested
        if color_by and color_by in clinical_aligned.columns:
            pca_df[color_by] = clinical_aligned[color_by]
        
        # Join other basic fields for tooltip labels (gender, stage, vital_status)
        for col in ["stage", "vital_status", "gender", "subtype"]:
            if col in clinical_aligned.columns and col not in pca_df.columns:
                pca_df[col] = clinical_aligned[col]
                
        return pca_df.reset_index(), var_ratios
