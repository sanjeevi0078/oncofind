import typer
from pathlib import Path
from typing import Optional
import pandas as pd
from rich.console import Console

from oncofind.config.settings import settings
from oncofind.cli.utils.validators import (
    validate_cancer_type,
    validate_data_downloaded
)
from oncofind.cli.utils.console import print_stats_table, print_error, print_success
from oncofind.core.analysis.deg import DEGAnalyzer
from oncofind.core.visualization.volcano import plot_volcano
from oncofind.core.visualization.heatmap import plot_heatmap
from oncofind.core.report.generator import generate_report

app = typer.Typer(help="Generate HTML summary report for a cancer type")
console = Console()

# Default comparisons matching other commands
DEFAULT_COMPARISONS = {
    "BRCA": ("ER_status", "Positive", "Negative"),
    "LUAD": ("smoking_status", "Smoker", "Non-smoker"),
    "COAD": ("msi_status", "MSI-H", "MSS"),
    "STAD": ("hpylori_status", "Positive", "Negative"),
    "OV": ("stage", "Stage III", "Stage I"),
    "LUSC": ("smoking_status", "Smoker", "Non-smoker"),
    "SKCM": ("stage", "Stage I", "Stage III"),
    "GBM": ("subtype", "Basal", "LumA"),
    "KIRC": ("stage", "Stage I", "Stage III"),
    "LIHC": ("stage", "Stage I", "Stage III"),
}


@app.callback(invoke_without_command=True)
def report(
    cancer: str = typer.Option(..., "--cancer", "-c", help="TCGA cancer type (e.g. BRCA)"),
    include_methods: bool = typer.Option(
        True, "--include-methods/--exclude-methods", help="Include methodology section in report"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Custom output report HTML path (defaults to ./oncofind_report_{cancer}.html)"
    ),
):
    """Generate a comprehensive HTML report for a specific cancer type."""
    cancer_clean = validate_cancer_type(cancer)
    data_dir = settings.data_dir
    expr_store, clin_store = validate_data_downloaded(cancer_clean, data_dir)
    
    out_path = output if output else Path(f"./oncofind_report_{cancer_clean}.html")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    groupby_clean, group_a, group_b = DEFAULT_COMPARISONS.get(cancer_clean, ("stage", None, None))
    
    try:
        clinical_df = clin_store.get_clinical_df(cancer_clean)
        
        if groupby_clean not in clinical_df.columns:
            if "stage" in clinical_df.columns:
                groupby_clean, group_a, group_b = "stage", "Stage II", "Stage I"
            else:
                fallback_col = None
                for col in clinical_df.columns:
                    if col in ["sample_barcode", "patient_barcode", "case_id"]:
                        continue
                    try:
                        unique_vals = clinical_df[col].dropna().unique().tolist()
                        if len(unique_vals) >= 2:
                            fallback_col = col
                            break
                    except Exception:
                        continue
                if fallback_col:
                    groupby_clean, group_a, group_b = fallback_col, None, None
                else:
                    raise ValueError(f"No suitable clinical variable found for comparison in {cancer_clean}")
        
        # 1. Group samples
        samples_a, samples_b, group_a_val, group_b_val = clin_store.get_group_samples(
            cancer_clean, groupby_clean, group_a, group_b
        )
        
        # 2. Run DEG analysis
        with console.status(f"[bold blue]Running comparative gene expression analysis for TCGA-{cancer_clean}...", spinner="dots"):
            counts_df = pd.read_parquet(expr_store.get_expression_path(cancer_clean)).set_index("sample_barcode")
            
            analyzer = DEGAnalyzer(fdr_threshold=0.05, log2fc_threshold=1.0)
            deg_df = analyzer.run_analysis(
                counts_df=counts_df,
                clinical_df=clinical_df,
                groupby=groupby_clean,
                group_a=group_a_val,
                group_b=group_b_val,
                method="deseq2" # Default to DESeq2 for final reports
            )
            
        # 3. Generate Volcano Plot div
        with console.status("[bold blue]Generating interactive Volcano Plot...", spinner="dots"):
            fig_volcano = plot_volcano(
                deg_df=deg_df,
                output_html_path=None,
                title=f"Volcano Plot: TCGA-{cancer_clean} ({group_a_val} vs {group_b_val})",
                log2fc_threshold=1.0,
                padj_threshold=0.05
            )
            volcano_html = fig_volcano.to_html(full_html=False, include_plotlyjs=True)
            
        # 4. Generate Heatmap div
        heatmap_html = None
        sig_genes = deg_df[deg_df["direction"] != "ns"].sort_values(by="padj").head(50)["gene_symbol"].tolist()
        if sig_genes:
            with console.status("[bold blue]Generating clustered expression heatmap...", spinner="dots"):
                all_tested_samples = samples_a + samples_b
                expression_subset = expr_store.query_expression(
                    cancer_clean, sig_genes, sample_barcodes=all_tested_samples
                )
                group_series = clinical_df.set_index("sample_barcode")[groupby_clean]
                
                fig_heatmap = plot_heatmap(
                    expression_df=expression_subset,
                    genes=sig_genes,
                    output_html_path=None,
                    title=f"Clustered Expression Heatmap: TCGA-{cancer_clean}",
                    group_series=group_series
                )
                heatmap_html = fig_heatmap.to_html(full_html=False, include_plotlyjs=False)
                
        # 5. Compile Jinja2 HTML Report
        with console.status("[bold blue]Compiling HTML report dashboard...", spinner="dots"):
            generate_report(
                cancer_type=cancer_clean,
                groupby=groupby_clean,
                group_a_val=group_a_val,
                group_b_val=group_b_val,
                n_group_a=len(samples_a),
                n_group_b=len(samples_b),
                method="deseq2", # Reported method
                deg_df=deg_df,
                fdr_threshold=0.05,
                fc_threshold=1.0,
                output_html_path=out_path,
                volcano_html=volcano_html,
                heatmap_html=heatmap_html,
                include_methods=include_methods
            )
            
        console.print()
        print_success(
            f"Successfully compiled report for TCGA-{cancer_clean}.\n\n"
            f"[bold]HTML Report Dashboard:[/] {out_path}\n",
            title="Report Generation Complete"
        )
        
    except Exception as e:
        print_error(f"Failed to generate report: {e}", title="Execution Error")
        raise typer.Exit(code=1)
