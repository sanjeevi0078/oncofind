import logging
import typer
from pathlib import Path
from typing import List, Optional
import pandas as pd
import numpy as np
from rich.console import Console
from rich.panel import Panel

from oncofind.config.settings import settings
from oncofind.cli.utils.validators import (
    validate_cancer_type,
    validate_data_downloaded
)
from oncofind.cli.utils.console import print_stats_table, print_error, print_success, print_warning
from oncofind.cli.utils.manifest import write_manifest
from oncofind.core.analysis.deg import DEGAnalyzer
from oncofind.core.analysis.survival import SurvivalAnalyzer
from oncofind.core.analysis.cccs import CrossCancerConsistencyScorer, CancerResult
from oncofind.core.analysis.batch import apply_combat
from oncofind.core.visualization.pancancer_plot import plot_pancancer_comparison
from oncofind.config.druggability import is_druggable, get_drugs_for_gene

logger = logging.getLogger(__name__)

app = typer.Typer(help="Compare gene dysregulation and survival across multiple cancers")
console = Console()

# Default clinical variables and comparisons for TCGA cancers
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
def pancancer(
    gene: str = typer.Option(..., "--gene", "-g", help="Gene symbol (e.g. TP53)"),
    cancers: Optional[List[str]] = typer.Option(
        None, "--cancers", "-c", help="Space-separated list of cancer types, or 'all'"
    ),
    batch_correct: bool = typer.Option(
        True,
        "--batch-correct/--no-batch-correct",
        help="Apply location-scale batch standardization before cross-cancer DEG analysis (default: ON). "
             "Removes technical variation introduced by different sequencing centres. "
             "Disable only if all samples come from the same batch.",
    ),
    mode: str = typer.Option(
        "subtype_comparison", "--mode", "-mode", help="DEG analysis mode: 'subtype_comparison' or 'tumor_vs_normal'"
    ),
    output_dir: Optional[Path] = typer.Option(
        None, "--output-dir", "-o", help="Where to save comparative reports (defaults to ./oncofind_results)"
    ),
    covariates: Optional[str] = typer.Option(
        None, "--covariates", help="Comma-separated list of clinical columns to adjust for in OLS regression."
    ),
):
    """Run cross-cancer consistency analysis for a specific gene."""
    data_dir = settings.data_dir
    cov_list = None
    if covariates:
        cov_list = [c.strip() for c in covariates.split(",") if c.strip()]
    
    # 1. Resolve cancers to test
    resolved_cancers = []
    if cancers:
        # Support space-separated input like --cancers "BRCA LUAD COAD"
        for c in cancers:
            resolved_cancers.extend(c.replace(",", " ").split())
    else:
        # Auto-detect downloaded cancers
        downloaded = []
        if data_dir.exists():
            for path in data_dir.iterdir():
                if path.is_dir() and not path.name.startswith("."):
                    downloaded.append(path.name.upper())
        resolved_cancers = downloaded if downloaded else ["BRCA", "LUAD", "COAD"]

    # Deduplicate and validate
    resolved_cancers = sorted(list(set(validate_cancer_type(c) for c in resolved_cancers)))
    
    if not resolved_cancers:
        print_error("No valid cancer types specified or found. Run download first.")
        raise typer.Exit(code=1)
        
    out_dir = output_dir if output_dir else Path("./oncofind_results")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    deg_analyzer = DEGAnalyzer()
    survival_analyzer = SurvivalAnalyzer()
    scorer = CrossCancerConsistencyScorer()
    
    cancer_results = []
    skipped = []

    # ── Step 1: Load all expression matrices (needed for batch correction) ── #
    loaded_expr: dict = {}   # cancer → counts_df
    loaded_clin: dict = {}   # cancer → clinical_df
    loaded_clin_stores: dict = {} # cancer → clin_store

    with console.status("[bold blue]Loading expression matrices...", spinner="dots"):
        for cancer in resolved_cancers:
            try:
                expr_store, clin_store = validate_data_downloaded(cancer, data_dir)
                # Check gene exists
                try:
                    expr_store.get_gene_column(cancer, gene)
                except Exception:
                    skipped.append((cancer, f"Gene '{gene}' not present in expression data."))
                    continue
                counts = pd.read_parquet(
                    expr_store.get_expression_path(cancer)
                ).set_index("sample_barcode")
                loaded_expr[cancer] = counts
                loaded_clin[cancer] = clin_store.get_clinical_df(cancer)
                loaded_clin_stores[cancer] = clin_store
            except Exception as e:
                skipped.append((cancer, str(e)))

    if not loaded_expr:
        print_error(f"No data loaded for any cancer type.", title="No Data")
        raise typer.Exit(code=1)

    # ── Step 2 (optional): Apply Location-Scale batch standardization ────── #
    if batch_correct and len(loaded_expr) >= 2:
        with console.status(
            f"[bold blue]Applying Location-Scale batch standardization across {len(loaded_expr)} cohorts...",
            spinner="dots"
        ):
            # Find the intersection of genes across all cancers
            common_genes = None
            for cancer, df in loaded_expr.items():
                genes_here = set(df.columns.tolist())
                common_genes = genes_here if common_genes is None else common_genes & genes_here

            if common_genes and len(common_genes) >= 10:
                common_genes = sorted(common_genes)
                combined_parts = []
                batch_labels = []
                for cancer, df in loaded_expr.items():
                    subset = df[common_genes]
                    combined_parts.append(subset)
                    batch_labels.extend([cancer] * len(subset))

                combined = pd.concat(combined_parts, axis=0)
                try:
                    corrected = apply_combat(combined, batch_labels)
                    # Split back into per-cancer DataFrames
                    idx = 0
                    for cancer, df in loaded_expr.items():
                        n = len(df)
                        corrected_slice = corrected.iloc[idx:idx + n].copy()
                        corrected_slice.index = df.index
                        # Reattach any columns not in common_genes (rare)
                        missing_cols = [c for c in df.columns if c not in common_genes]
                        if missing_cols:
                            corrected_slice = pd.concat(
                                [corrected_slice, df[missing_cols]], axis=1
                            )
                        loaded_expr[cancer] = corrected_slice
                        idx += n
                    logger.info("Batch standardization applied successfully.")
                except Exception as e:
                    logger.warning(f"Batch standardization failed ({e}). Proceeding without correction.")
            else:
                logger.warning(
                    f"Insufficient common genes ({len(common_genes or [])}) for batch correction. Skipping."
                )
    elif batch_correct and len(loaded_expr) < 2:
        logger.info("Only one cancer loaded — batch correction skipped (requires ≥ 2 cohorts).")

    # ── Step 3: Per-cancer DEG + Survival ─────────────────────────────────── #
    loaded_deg_res = {}
    loaded_survival_ps = {}
    loaded_gene_rows = {}
    
    with console.status(f"[bold blue]Running pan-cancer analysis for {gene}...", spinner="dots"):
        for cancer, counts_df in loaded_expr.items():
            try:
                clinical_df = loaded_clin[cancer]
                if mode == "tumor_vs_normal":
                    groupby, group_a, group_b = "sample_type", "Primary Tumor", "Solid Tissue Normal"
                else:
                    groupby, group_a_opt, group_b_opt = DEFAULT_COMPARISONS.get(cancer, ("stage", None, None))
                    clin_store = loaded_clin_stores[cancer]
                    
                    if groupby not in clinical_df.columns:
                        if "stage" in clinical_df.columns:
                            groupby, group_a_opt, group_b_opt = "stage", "Stage II", "Stage I"
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
                                groupby, group_a_opt, group_b_opt = fallback_col, None, None
                            else:
                                raise ValueError(f"No suitable clinical variable found for comparison in {cancer}")
                    
                    samples_a, samples_b, group_a, group_b = clin_store.get_group_samples(
                        cancer, groupby, group_a_opt, group_b_opt
                    )
                
                # Use cache only if no batch correction is performed
                use_cache = not batch_correct or len(loaded_expr) < 2
                cov_suffix = ""
                if cov_list:
                    cov_suffix = "_" + "_".join(sorted(cov_list))
                groupby_label = "tumor_vs_normal" if mode == "tumor_vs_normal" else groupby
                cached_path = out_dir / f"{cancer}_{groupby_label}{cov_suffix}_deg_results.csv"
                
                if use_cache and cached_path.exists():
                    logger.info(f"Loaded cached DEG results for {cancer}: {cached_path.name}")
                    deg_res = pd.read_csv(cached_path)
                else:
                    # Run DEG
                    deg_res = deg_analyzer.run_analysis(
                        counts_df=counts_df,
                        clinical_df=clinical_df,
                        groupby=groupby,
                        group_a=group_a,
                        group_b=group_b,
                        method="ttest",  # Fast ttest for cross-cohort speed
                        mode=mode,
                        covariates=cov_list
                    )
                
                gene_row = deg_res[deg_res["gene_symbol"].str.upper() == gene.upper()].iloc[0]
                loaded_deg_res[cancer] = deg_res
                loaded_gene_rows[cancer] = gene_row
                
                # Run Survival — extract single-gene expression from the (possibly corrected) matrix
                if gene.upper() in counts_df.columns:
                    expression_df = counts_df[[gene.upper()]].copy()
                    expression_df.columns = [gene]
                elif gene in counts_df.columns:
                    expression_df = counts_df[[gene]].copy()
                else:
                    expression_df = counts_df.iloc[:, :1].copy()
                    expression_df.columns = [gene]

                try:
                    survival_res = survival_analyzer.analyze(
                        expression_df, clinical_df, gene, split_method="median", p_value_only=True
                    )
                    survival_p = survival_res.p_value
                except Exception as e:
                    logger.warning(f"Survival analysis failed for {gene} in {cancer}: {e}")
                    survival_p = None
                    
                loaded_survival_ps[cancer] = survival_p
            except Exception as e:
                skipped.append((cancer, str(e)))
                
    # Check if the gene is significant at FDR < 0.05 in any cancer
    any_sig = False
    for cancer, deg_res in loaded_deg_res.items():
        gene_row = loaded_gene_rows[cancer]
        if gene_row["padj"] < 0.05 and gene_row["direction"] != "ns":
            any_sig = True
            break
            
    if not any_sig and loaded_deg_res:
        console.print("[yellow]Warning: Gene is not significant at strict FDR threshold in any cancer. Falling back to unadjusted p-value < 0.05 and |log2FC| > 0.5.[/]")
        for cancer, deg_res in loaded_deg_res.items():
            deg_res["padj"] = deg_res["pvalue"]
            deg_res["direction"] = "ns"
            deg_res.loc[(deg_res["pvalue"] < 0.05) & (deg_res["log2FC"] > 0.5), "direction"] = "up"
            deg_res.loc[(deg_res["pvalue"] < 0.05) & (deg_res["log2FC"] < -0.5), "direction"] = "down"
            loaded_gene_rows[cancer] = deg_res[deg_res["gene_symbol"].str.upper() == gene.upper()].iloc[0]
            
    # Build cancer_results
    for cancer in loaded_deg_res.keys():
        gene_row = loaded_gene_rows[cancer]
        survival_p = loaded_survival_ps[cancer]
        cancer_results.append(CancerResult(
            cancer_type=cancer,
            log2fc=float(gene_row["log2FC"]),
            padj=float(gene_row["padj"]),
            direction=gene_row["direction"],
            survival_pvalue=survival_p
        ))
                
    # Check if we got any results
    if not cancer_results:
        print_error(f"Failed to gather results for {gene} in any of the cohorts.", title="No Results")
        if skipped:
            console.print("[bold]Skipped/Failed cohorts details:[/]")
            for c, err in skipped:
                console.print(f"  • {c}: {err}")
        raise typer.Exit(code=1)
        
    # 3. Compute CCCS Score
    # We map to a mock gene ID for clinical scoring
    cccs_res = scorer.compute(
        gene_symbol=gene,
        gene_id=f"ENSG_{gene}",
        cancer_results=cancer_results
    )
    
    # 4. Generate visualizer plot
    pancancer_html_filename = f"pancancer_{gene}_comparison.html"
    pancancer_html_path = out_dir / pancancer_html_filename
    plot_pancancer_comparison(cccs_res, pancancer_html_path)
    
    # 5. Output Rich table
    headers = ["Cancer", "log2FC", "padj", "Dir", "Survival p"]
    rows = []
    for r in cancer_results:
        dir_char = "↑" if r.direction == "up" else ("↓" if r.direction == "down" else "ns")
        p_str = f"{r.survival_pvalue:.4f}" if r.survival_pvalue is not None else "N/A"
        if r.survival_pvalue is not None and r.survival_pvalue >= 0.05:
            p_str += " (ns)"
        
        rows.append([
            r.cancer_type,
            f"{r.log2fc:+.2f}",
            f"{r.padj:.4e}",
            dir_char,
            p_str
        ])
        
    console.print()
    print_stats_table(
        title=f"Pan-Cancer Analysis: {gene}",
        headers=headers,
        rows=rows,
        border_style="magenta"
    )
    
    # Output CCCS Summary Panel
    druggability_info = ""
    if is_druggable(gene):
        drugs = ", ".join(get_drugs_for_gene(gene))
        druggability_info = f"\n[bold]Druggability:[/] [bold cyan]Actionable Target[/] (Associated drugs: {drugs})"
        
    console.print(Panel(
        f"[bold]Cross-Cancer Consistency Score (CCCS):[/] [bold green]{cccs_res.cccs:.2f}[/]\n"
        f"[bold]Interpretation:[/] {cccs_res.interpretation}{druggability_info}",
        title="CCCS Metric Report",
        border_style="green"
    ))
    
    if skipped:
        print_warning(
            f"Skipped {len(skipped)} cancer type(s) due to missing data or errors:\n" +
            "\n".join(f"  • {c}: {err}" for c, err in skipped),
            title="Partial Analysis Run"
        )
        
    write_manifest(
        out_dir, "pancancer",
        params={"gene": gene, "cancers": list(loaded_expr.keys()), "batch_correct": batch_correct, "covariates": covariates},
        result_summary={"cccs": cccs_res.cccs, "n_cancers_tested": cccs_res.n_cancers_tested, "n_cancers_significant": cccs_res.n_cancers_significant},
    )
    console.print()
    print_success(
        f"Completed Pan-Cancer analysis for {gene}.\n\n"
        f"[bold]Pan-Cancer Dashboard:[/] {pancancer_html_path}\n"
        f"[bold]Comparison CSV Data:[/] {out_dir / f'pancancer_{gene}_data.csv'}\n",
        title="Flagship Analysis Complete"
    )
    
    # Save CSV comparison
    comp_df = pd.DataFrame([{
        "cancer_type": r.cancer_type,
        "log2fc": r.log2fc,
        "padj": r.padj,
        "direction": r.direction,
        "survival_pvalue": r.survival_pvalue
    } for r in cancer_results])
    comp_df.to_csv(out_dir / f"pancancer_{gene}_data.csv", index=False)
