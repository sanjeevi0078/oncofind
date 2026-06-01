import difflib
import typer
from pathlib import Path
from typing import List, Optional, Tuple
import pandas as pd

from oncofind.config.cancer_types import is_valid_cancer, CANCER_REGISTRY
from oncofind.core.data.expression_store import ExpressionStore
from oncofind.core.data.clinical_store import ClinicalStore
from oncofind.cli.utils.console import print_error, console


def validate_cancer_type(cancer: str) -> str:
    """Validate that the cancer code is supported, suggesting close matches if not."""
    cancer_upper = cancer.upper()
    if not is_valid_cancer(cancer_upper):
        valid_cancers = sorted(list(CANCER_REGISTRY.keys()))
        suggestions = difflib.get_close_matches(cancer_upper, valid_cancers, n=3, cutoff=0.5)
        
        msg = f"Cancer type '{cancer}' is not supported by TCGA registry."
        if suggestions:
            msg += f"\nDid you mean: {', '.join(suggestions)}?"
        else:
            msg += f"\nSupported types include: {', '.join(valid_cancers[:10])}..."
            
        print_error(msg, title="Invalid Cancer Type")
        raise typer.Exit(code=1)
    return cancer_upper


def validate_data_downloaded(cancer: str, data_dir: Path) -> Tuple[ExpressionStore, ClinicalStore]:
    """Ensure expression and clinical data are downloaded and preprocessed."""
    expr_store = ExpressionStore(data_dir)
    clin_store = ClinicalStore(data_dir)
    
    if not expr_store.is_downloaded(cancer) or not clin_store.is_downloaded(cancer):
        print_error(
            f"Data for cancer '{cancer}' has not been downloaded yet.\n"
            f"Please run the download command first:\n\n"
            f"  [bold cyan]oncofind download --cancer {cancer}[/]",
            title="Missing Dataset"
        )
        raise typer.Exit(code=1)
        
    return expr_store, clin_store


def validate_clinical_variable(clin_store: ClinicalStore, cancer: str, groupby: str) -> str:
    """Ensure clinical grouping column exists in metadata, suggesting alternatives."""
    try:
        df = clin_store.get_clinical_df(cancer)
    except Exception as e:
        print_error(f"Failed to load clinical metadata: {e}")
        raise typer.Exit(code=1)
        
    if groupby not in df.columns:
        # Exclude internal non-annotation columns
        available_cols = [
            col for col in df.columns 
            if col not in ["sample_barcode", "patient_barcode", "case_id", "survival_days", "censored"]
        ]
        suggestions = difflib.get_close_matches(groupby, available_cols, n=3, cutoff=0.5)
        
        msg = f"Clinical variable '{groupby}' not found for TCGA-{cancer}."
        if suggestions:
            msg += f"\nDid you mean: {', '.join(suggestions)}?"
        else:
            msg += f"\nAvailable variables: {', '.join(available_cols)}"
            
        print_error(msg, title="Variable Not Found")
        raise typer.Exit(code=1)
        
    return groupby


def validate_gene_symbols(expr_store: ExpressionStore, cancer: str, genes: List[str]) -> List[str]:
    """Verify that gene symbols exist in the expression dataset, raising typer.Exit on failure."""
    validated = []
    for gene in genes:
        try:
            expr_store.get_gene_column(cancer, gene)
            validated.append(gene)
        except Exception as e:
            # Let the store raise the GeneNotFoundError which includes spelling suggestions
            print_error(str(e), title="Gene Not Found")
            raise typer.Exit(code=1)
    return validated


from typing import Tuple
