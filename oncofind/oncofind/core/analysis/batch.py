import logging
from typing import List, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class BatchCorrector:
    """Performs simplified Location-and-Scale batch standardization on expression matrices."""

    def correct_batch(
        self,
        expression_df: pd.DataFrame,
        batch_ids: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Adjust expression values to remove batch effects.
        If batch_ids is not provided, extracts plate IDs from TCGA sample barcodes as a proxy.
        
        Args:
            expression_df: DataFrame where rows are samples and columns are genes.
            batch_ids: Optional list of batch labels matching the rows of expression_df.
            
        Returns:
            DataFrame containing the batch-corrected expression matrix.
        """
        # Deduce batches from TCGA barcode if not provided
        # Example TCGA barcode: TCGA-BH-A0DG-01A-21R-A112-07
        # A112 is the plate ID (portion index 5) which is the most common batch variable
        if batch_ids is None:
            batch_ids = []
            for barcode in expression_df.index:
                parts = barcode.split("-")
                if len(parts) >= 6:
                    # Use plate ID (e.g. A112)
                    batch_ids.append(parts[5])
                else:
                    # Fallback to TSS (tissue source site, e.g. BH)
                    if len(parts) >= 2:
                        batch_ids.append(parts[1])
                    else:
                        batch_ids.append("batch_1")

        # Convert to numpy array for speed
        batches = np.array(batch_ids)
        unique_batches = np.unique(batches)
        
        if len(unique_batches) <= 1:
            logger.info("Single batch detected or single plate ID. Skipping batch correction.")
            return expression_df.copy()

        logger.info(f"Applying location-scale batch standardization for {len(unique_batches)} batches: {list(unique_batches)}")

        # Store index and columns
        sample_barcodes = expression_df.index
        gene_symbols = expression_df.columns
        
        # Working with log2-transformed or standard float matrices
        # Let's ensure float type
        data = expression_df.values.astype(float)
        
        # 1. Overall mean and variance per gene
        grand_mean = np.mean(data, axis=0)
        grand_var = np.var(data, axis=0, ddof=1)
        grand_var[grand_var == 0] = 1.0  # avoid division by zero
        grand_std = np.sqrt(grand_var)
        
        # 2. Standardize data
        standardized_data = (data - grand_mean) / grand_std
        
        # 3. Fit batch effect parameters (Location delta and Scale gamma)
        # Location (delta_ig): mean of standardized data per batch
        # Scale (gamma_ig): variance of standardized data per batch
        adjusted_data = np.zeros_like(data)
        
        for batch in unique_batches:
            batch_mask = (batches == batch)
            n_batch = np.sum(batch_mask)
            
            if n_batch < 2:
                # If a batch has only 1 sample, we cannot calculate its variance,
                # so we just center it without scaling.
                batch_mean = np.mean(standardized_data[batch_mask, :], axis=0)
                adjusted_data[batch_mask, :] = standardized_data[batch_mask, :] - batch_mean
            else:
                batch_mean = np.mean(standardized_data[batch_mask, :], axis=0)
                batch_var = np.var(standardized_data[batch_mask, :], axis=0, ddof=1)
                batch_var[batch_var == 0] = 1.0  # avoid division by zero
                batch_std = np.sqrt(batch_var)
                
                # Adjust: (Standardized - Mean) / Std
                adjusted_data[batch_mask, :] = (standardized_data[batch_mask, :] - batch_mean) / batch_std
                
        # 4. Reconstruct corrected data: multiply by grand std and add grand mean
        corrected_data = adjusted_data * grand_std + grand_mean
        
        # Keep non-negative if original was count-like (ensure zero remains zero-ish)
        # But ComBat correction can produce negative numbers. If original was strictly non-negative,
        # we can optional-clip or leave as is. Generally, for normal distributions, we keep negative values.
        # Let's just clip to original range if required, or keep float.
        corrected_df = pd.DataFrame(corrected_data, index=sample_barcodes, columns=gene_symbols)
        return corrected_df


def apply_combat(
    expression_df: pd.DataFrame,
    batch_ids: List[str],
) -> pd.DataFrame:
    """
    Module-level convenience wrapper for BatchCorrector.correct_batch().

    Args:
        expression_df: DataFrame (samples × genes). Index must be sample barcodes.
        batch_ids: List of batch labels, one per row of expression_df.
                   For pan-cancer use, pass cancer type codes as batch labels
                   (e.g. ["BRCA", "BRCA", ..., "LUAD", "LUAD", ...]).

    Returns:
        Batch-corrected DataFrame with identical index and columns.

    Raises:
        ValueError: If batch_ids length doesn't match expression_df rows.
    """
    if len(batch_ids) != len(expression_df):
        raise ValueError(
            f"batch_ids length ({len(batch_ids)}) must match number of rows "
            f"in expression_df ({len(expression_df)})."
        )
    corrector = BatchCorrector()
    return corrector.correct_batch(expression_df, batch_ids=batch_ids)

