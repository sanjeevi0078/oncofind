import typer
from pathlib import Path
from typing import Optional
import pandas as pd
from rich.console import Console
from rich.panel import Panel

from oncofind.config.settings import settings
from oncofind.cli.utils.validators import (
    validate_cancer_type,
    validate_data_downloaded,
    validate_clinical_variable
)
from oncofind.cli.utils.console import print_stats_table, print_error, print_success, get_progress
from oncofind.cli.utils.manifest import write_manifest
from oncofind.core.analysis.deg import DEGAnalyzer
from oncofind.core.visualization.volcano import plot_volcano
from oncofind.core.visualization.heatmap import plot_heatmap

app = typer.Typer(help="Perform Differential Expression Gene (DEG) analysis")
console = Console()


@app.callback(invoke_without_command=True)
def deg(
    cancer: str = typer.Option(..., "--cancer", "-c", help="TCGA cancer type (e.g. BRCA)"),
    mode: str = typer.Option(
        "subtype_comparison",
        "--mode",
        help="Analysis mode: 'subtype_comparison' (compare clinical groups) or "
             "'tumor_vs_normal' (Primary Tumor vs Solid Tissue Normal).",
    ),
    groupby: Optional[str] = typer.Option(
        None, "--groupby", "-g",
        help="Clinical variable to split groups (e.g. ER_status, stage). "
             "Required when --mode subtype_comparison."
    ),
    group_a: Optional[str] = typer.Option(
        None, "--group-a", help="Value for group A (auto-detect top 2 if omitted)"
    ),
    group_b: Optional[str] = typer.Option(
        None, "--group-b", help="Value for group B"
    ),
    method: str = typer.Option(
        "deseq2", "--method", help="Analysis method: 'deseq2' or 'ttest'"
    ),
    fdr: float = typer.Option(
        0.05, "--fdr", help="FDR threshold for significance"
    ),
    log2fc: float = typer.Option(
        1.0, "--log2fc", help="log2 Fold Change threshold for significance"
    ),
    output_dir: Optional[Path] = typer.Option(
        None, "--output-dir", "-o", help="Where to save results (defaults to ./oncofind_results)"
    ),
    no_plot: bool = typer.Option(
        False, "--no-plot", help="Skip plot generation"
    ),
    covariates: Optional[str] = typer.Option(
        None, "--covariates", help="Comma-separated list of clinical columns to adjust for in OLS regression."
    ),
):
    """Run DEG analysis using PyDESeq2 or t-test fallback."""
    # 0. Validate mode
    valid_modes = {"subtype_comparison", "tumor_vs_normal"}
    if mode not in valid_modes:
        print_error(f"Invalid mode '{mode}'. Choose from: {', '.join(valid_modes)}", title="Invalid Mode")
        raise typer.Exit(code=1)

    if mode == "subtype_comparison" and not groupby:
        print_error(
            "--groupby is required when --mode subtype_comparison. "
            "Example: --groupby ER_status",
            title="Missing Argument"
        )
        raise typer.Exit(code=1)
    # 1. Validate inputs
    cancer_clean = validate_cancer_type(cancer)
    data_dir = settings.data_dir
    expr_store, clin_store = validate_data_downloaded(cancer_clean, data_dir)

    # groupby validation only needed for subtype_comparison
    groupby_clean = None
    if mode == "subtype_comparison":
        groupby_clean = validate_clinical_variable(clin_store, cancer_clean, groupby)
    
    # 2. Setup output directories
    out_dir = output_dir if output_dir else Path("./oncofind_results")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 3. Determine sample groups
        if mode == "tumor_vs_normal":
            group_a_val, group_b_val = "Tumor", "Normal"
            group_a_samples = []
            group_b_samples = []
            n_a = n_b = 0  # will be populated by DEGAnalyzer internally
        else:
            group_a_samples, group_b_samples, group_a_val, group_b_val = clin_store.get_group_samples(
                cancer_clean, groupby_clean, group_a, group_b
            )
            n_a = len(group_a_samples)
            n_b = len(group_b_samples)
        
        # 4. Load count matrix
        with console.status(f"[bold blue]Loading count matrix for TCGA-{cancer_clean}...", spinner="dots"):
            counts_df = pd.read_parquet(expr_store.get_expression_path(cancer_clean)).set_index("sample_barcode")
            
        # 5. Run DEG analysis
        label = f"Tumor vs Normal" if mode == "tumor_vs_normal" else f"{group_a_val} vs {group_b_val}"
        with console.status(f"[bold blue]Running DEG ({method}) — {label}...", spinner="dots"):
            analyzer = DEGAnalyzer(fdr_threshold=fdr, log2fc_threshold=log2fc)
            cov_list = None
            if covariates:
                cov_list = [c.strip() for c in covariates.split(",") if c.strip()]
                
            deg_df = analyzer.run_analysis(
                counts_df,
                clin_store.get_clinical_df(cancer_clean),
                groupby=groupby_clean or "sample_type_bin",
                group_a=group_a_val,
                group_b=group_b_val,
                method=method,
                mode=mode,
                covariates=cov_list,
            )
            
        # 6. Gather summary statistics
        n_genes_tested = deg_df.shape[0]
        n_up = (deg_df["direction"] == "up").sum()
        n_down = (deg_df["direction"] == "down").sum()
        n_sig = n_up + n_down
        
        # Get top gene
        top_gene_symbol = "N/A"
        top_gene_fc = 0.0
        if n_sig > 0:
            sig_df = deg_df[deg_df["direction"] != "ns"]
            top_row = sig_df.loc[sig_df["log2FC"].abs().idxmax()]
            top_gene_symbol = top_row["gene_symbol"]
            top_gene_fc = top_row["log2FC"]
            
        # 7. Save result files
        groupby_label = "tumor_vs_normal" if mode == "tumor_vs_normal" else groupby_clean
        csv_filename = f"{cancer_clean}_{groupby_label}_deg_results.csv"
        csv_path = out_dir / csv_filename
        deg_df.to_csv(csv_path, index=False)
        
        saved_paths_info = f"[bold]DEG CSV Results:[/] {csv_path}\n"
        
        # 8. Generate Plots (Volcano and Heatmap)
        if not no_plot:
            # Volcano Plot
            volcano_html_filename = f"{cancer_clean}_{groupby_label}_volcano.html"
            volcano_html_path = out_dir / volcano_html_filename
            plot_volcano(
                deg_df,
                volcano_html_path,
                title=f"Volcano Plot: TCGA-{cancer_clean} ({group_a_val} vs {group_b_val})",
                log2fc_threshold=log2fc,
                padj_threshold=fdr
            )
            saved_paths_info += f"[bold]Volcano Plot:[/] {volcano_html_path}\n"
            
            # Heatmap of top 50 significant genes
            sig_genes = deg_df[deg_df["direction"] != "ns"].sort_values(by="padj").head(50)["gene_symbol"].tolist()
            if sig_genes:
                heatmap_html_filename = f"{cancer_clean}_{groupby_label}_heatmap.html"
                heatmap_html_path = out_dir / heatmap_html_filename
                
                # Fetch expression
                all_tested_samples = group_a_samples + group_b_samples
                expression_subset = expr_store.query_expression(
                    cancer_clean, sig_genes, sample_barcodes=all_tested_samples
                )
                
                # Setup group mapping for samples
                clinical_df = clin_store.get_clinical_df(cancer_clean)
                if mode == "tumor_vs_normal":
                    from oncofind.core.analysis.deg import _TUMOR_SAMPLE_TYPES, _NORMAL_SAMPLE_TYPES
                    def map_sample_type(st):
                        if st in _TUMOR_SAMPLE_TYPES:
                            return "Tumor"
                        if st in _NORMAL_SAMPLE_TYPES:
                            return "Normal"
                        return "Unknown"
                    group_series = clinical_df.set_index("sample_barcode")["sample_type"].apply(map_sample_type)
                else:
                    group_series = clinical_df.set_index("sample_barcode")[groupby_clean]
                
                plot_heatmap(
                    expression_subset,
                    sig_genes,
                    heatmap_html_path,
                    title=f"Expression Heatmap (Top 50 DEGs): TCGA-{cancer_clean}",
                    group_series=group_series
                )
                saved_paths_info += f"[bold]Clustered Heatmap:[/] {heatmap_html_path}\n"
                
        # 9. Output Rich Stats Table
        console.print()
        comparison_label = "Tumor vs Normal" if mode == "tumor_vs_normal" else f"{group_a_val} vs {group_b_val}"
        print_stats_table(
            title=f"DEG Analysis: {cancer_clean} — {comparison_label}",
            headers=["Parameter", "Value"],
            rows=[
                ["Mode", mode.replace("_", " ").title()],
                [f"Group A ({group_a_val})", f"{n_a} samples" if n_a else "detected by sample_type"],
                [f"Group B ({group_b_val})", f"{n_b} samples" if n_b else "detected by sample_type"],
                ["Method", method.upper()],
                ["Genes tested", f"{n_genes_tested:,}"],
                ["Significant DEGs", f"{n_sig} (↑ {n_up}, ↓ {n_down})"],
                ["Top gene (by Log2FC)", f"{top_gene_symbol} (log2FC={top_gene_fc:.2f})"]
            ]
        )
        console.print()
        
        write_manifest(
            out_dir, "deg",
            params={
                "cancer": cancer_clean, "mode": mode,
                "groupby": groupby_clean, "group_a": group_a_val,
                "group_b": group_b_val, "method": method,
                "fdr": fdr, "log2fc": log2fc,
                "covariates": covariates,
            },
            data_files=[
                expr_store.get_expression_path(cancer_clean),
                clin_store.get_clinical_path(cancer_clean),
            ],
            result_summary={
                "n_genes_tested": n_genes_tested,
                "n_significant": n_sig,
                "n_up": int(n_up), "n_down": int(n_down),
                "top_gene": top_gene_symbol,
            },
        )
        print_success(
            f"Successfully completed analysis.\n\n{saved_paths_info}",
            title="DEG Analysis Complete"
        )
        
    except Exception as e:
        print_error(f"Analysis failed: {e}", title="Execution Error")
        raise typer.Exit(code=1)
