import typer
from pathlib import Path
from typing import List, Optional
import pandas as pd
from rich.console import Console

from oncofind.config.settings import settings
from oncofind.cli.utils.validators import (
    validate_cancer_type,
    validate_data_downloaded
)
from oncofind.cli.utils.console import print_stats_table, print_error, print_success, print_warning
from oncofind.core.analysis.deg import DEGAnalyzer
from oncofind.core.analysis.survival import SurvivalAnalyzer
from oncofind.core.analysis.cccs import CrossCancerConsistencyScorer, CancerResult
from oncofind.config.druggability import is_druggable, get_drugs_for_gene

app = typer.Typer(help="Rank all genes by Cross-Cancer Consistency Score (CCCS)")
console = Console()

# Default comparisons matching pancancer flagship command
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
def score(
    cancers: Optional[List[str]] = typer.Option(
        None, "--cancers", "-c", help="Cancers to include in scoring (default: BRCA LUAD COAD)"
    ),
    top_n: int = typer.Option(
        50, "--top-n", "-t", help="Show top N genes"
    ),
    min_cancers: int = typer.Option(
        3, "--min-cancers", "-m", help="Minimum cancers a gene must have significant DE in"
    ),
    druggable_only: bool = typer.Option(
        False, "--druggable-only", "-d", help="Filter for targetable/druggable genes only"
    ),
    mode: str = typer.Option(
        "subtype_comparison", "--mode", "-mode", help="DEG analysis mode: 'subtype_comparison' or 'tumor_vs_normal'"
    ),
    output_dir: Optional[Path] = typer.Option(
        None, "--output-dir", "-o", help="Where to save rankings (defaults to ./oncofind_results)"
    ),
    covariates: Optional[str] = typer.Option(
        None, "--covariates", help="Comma-separated list of clinical columns to adjust for in OLS regression."
    ),
):
    """Rank genes by Cross-Cancer Consistency Score (CCCS)."""
    data_dir = settings.data_dir
    cov_list = None
    if covariates:
        cov_list = [c.strip() for c in covariates.split(",") if c.strip()]
    
    # 1. Resolve cancers to test
    resolved_cancers = []
    if cancers:
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

    resolved_cancers = sorted(list(set(validate_cancer_type(c) for c in resolved_cancers)))
    
    if len(resolved_cancers) < 2:
        print_warning(
            f"Pan-cancer ranking is designed for multiple cancers. Only {len(resolved_cancers)} cancer(s) available.",
            title="Low Cohort Count"
        )
        
    out_dir = output_dir if output_dir else Path("./oncofind_results")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    deg_analyzer = DEGAnalyzer()
    survival_analyzer = SurvivalAnalyzer()
    scorer = CrossCancerConsistencyScorer()
    
    # 2. Gather DEG results across all cancers
    cancer_degs = {}
    cancer_counts_dfs = {}
    cancer_clinical_dfs = {}
    cancer_expr_stores = {}
    skipped = []
    
    with console.status("[bold blue]Performing initial DEG screening across all cohorts...", spinner="dots"):
        for cancer in resolved_cancers:
            try:
                expr_store, clin_store = validate_data_downloaded(cancer, data_dir)
                
                # Load matrices
                counts_df = pd.read_parquet(expr_store.get_expression_path(cancer)).set_index("sample_barcode")
                clinical_df = clin_store.get_clinical_df(cancer)
                
                if mode == "tumor_vs_normal":
                    groupby, group_a, group_b = "sample_type", "Primary Tumor", "Solid Tissue Normal"
                else:
                    groupby, group_a_opt, group_b_opt = DEFAULT_COMPARISONS.get(cancer, ("stage", None, None))
                    
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
                    
                    # Resolve group samples and values dynamically
                    samples_a, samples_b, group_a, group_b = clin_store.get_group_samples(
                        cancer, groupby, group_a_opt, group_b_opt
                    )
                
                # Check for cached DEG CSV first
                cov_suffix = ""
                if cov_list:
                    cov_suffix = "_" + "_".join(sorted(cov_list))
                groupby_label = "tumor_vs_normal" if mode == "tumor_vs_normal" else groupby
                cached_path = out_dir / f"{cancer}_{groupby_label}{cov_suffix}_deg_results.csv"
                
                if cached_path.exists():
                    console.print(f"  [green]✓[/] Loaded cached DEG results for {cancer}: {cached_path.name}")
                    deg_res = pd.read_csv(cached_path)
                else:
                    deg_res = deg_analyzer.run_analysis(
                        counts_df=counts_df,
                        clinical_df=clinical_df,
                        groupby=groupby,
                        group_a=group_a,
                        group_b=group_b,
                        method="ttest",
                        mode=mode,
                        covariates=cov_list
                    )
                    # Save to cache so that subsequent score runs are consistent
                    deg_res.to_csv(cached_path, index=False)
                    console.print(f"  [blue]ℹ[/] Computed and cached DEG results for {cancer}: {cached_path.name}")
                
                cancer_degs[cancer] = deg_res
                cancer_counts_dfs[cancer] = counts_df
                cancer_clinical_dfs[cancer] = clinical_df
                cancer_expr_stores[cancer] = expr_store
            except Exception as e:
                skipped.append((cancer, str(e)))
                
    if not cancer_degs:
        print_error("Failed to load DEG data for any cohorts.", title="Scoring Failed")
        raise typer.Exit(code=1)
        
    # 3. Identify candidate genes: those that are significant (direction != "ns") in at least 1 cancer
    # To optimize run-times, we only compute log-rank tests for genes that show a diff-expr signal.
    all_genes_union = set()
    gene_sig_counts = {}
    
    for cancer, deg_df in cancer_degs.items():
        sig_genes = deg_df[deg_df["direction"] != "ns"]["gene_symbol"].tolist()
        all_genes_union.update(sig_genes)
        for g in sig_genes:
            gene_sig_counts[g] = gene_sig_counts.get(g, 0) + 1
            
    # Dynamic adjustment of min_cancers based on available cancers
    effective_min_cancers = min(min_cancers, len(resolved_cancers))
    
    # Filter candidates by effective_min_cancers threshold
    candidates = [g for g, count in gene_sig_counts.items() if count >= effective_min_cancers]
    
    if not candidates and effective_min_cancers > 1:
        console.print(f"[yellow]Warning: No genes were significant in >= {effective_min_cancers} cancers. Falling back to threshold of 1.[/]")
        candidates = list(all_genes_union)
        
    if not candidates:
        print_error("No genes passed the strict FDR significance threshold (padj < 0.05) in any cohort. Scoring failed.", title="Scoring Failed")
        raise typer.Exit(code=1)
        
    # 4. Perform survival analysis & CCCS scoring for all candidate genes
    results = []
    
    with console.status(f"[bold blue]Calculating CCCS scores for {len(candidates)} candidate genes...", spinner="dots"):
        for gene in candidates:
            gene_cancer_results = []
            
            for cancer in resolved_cancers:
                if cancer not in cancer_degs:
                    continue
                    
                deg_df = cancer_degs[cancer]
                # Check if gene in this cancer
                gene_rows = deg_df[deg_df["gene_symbol"].str.upper() == gene.upper()]
                if gene_rows.empty:
                    continue
                    
                gene_row = gene_rows.iloc[0]
                
                # Perform survival analysis on the fly
                counts_df = cancer_counts_dfs[cancer]
                clinical_df = cancer_clinical_dfs[cancer]
                
                # Resolve gene column name
                try:
                    expr_store = cancer_expr_stores[cancer]
                    gene_col = expr_store.get_gene_column(cancer, gene)
                    expression_df = counts_df[[gene_col]].rename(columns={gene_col: gene})
                    
                    survival_res = survival_analyzer.analyze(expression_df, clinical_df, gene, p_value_only=True)
                    survival_p = survival_res.p_value
                except Exception:
                    survival_p = None
                    
                gene_cancer_results.append(CancerResult(
                    cancer_type=cancer,
                    log2fc=float(gene_row["log2FC"]),
                    padj=float(gene_row["padj"]),
                    direction=gene_row["direction"],
                    survival_pvalue=survival_p
                ))
                
            # Score
            cccs_res = scorer.compute(
                gene_symbol=gene,
                gene_id=f"ENSG_{gene}",
                cancer_results=gene_cancer_results
            )
            
            results.append({
                "Gene": gene,
                "CCCS": cccs_res.cccs,
                "Direction": cccs_res.dominant_direction.upper(),
                "Significant Cancers": f"{cccs_res.n_cancers_significant}/{cccs_res.n_cancers_tested}",
                "Survival Significant": f"{cccs_res.n_cancers_survival_significant}/{cccs_res.n_cancers_tested}",
                "Druggable": "YES" if is_druggable(gene) else "NO",
                "Target Drugs": ", ".join(get_drugs_for_gene(gene)) if is_druggable(gene) else "N/A",
                "Interpretation": cccs_res.interpretation
            })
            
    # 5. Sort and display top N
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(by="CCCS", ascending=False)
    
    if druggable_only:
        results_df = results_df[results_df["Druggable"] == "YES"]
        
    top_df = results_df.head(top_n)
    
    # Render table
    if len(resolved_cancers) == 1:
        table_title = f"Top Biomarker Candidates: Single-cohort DEG+survival ranking ({'Druggable Only' if druggable_only else 'All Genes'})"
        headers = ["Rank", "Gene", "Score", "Dominant Dir", "Sig Cancers", "Survival Sig", "Druggable", "Target Drugs"]
        console.print()
        console.print("[bold yellow]⚠️  Warning: Operating on a single cancer. CCCS has collapsed to a single-cohort DEG+survival ranking.[/]")
    else:
        table_title = f"Top Biomarker Candidates Ranked by CCCS (Min Cancers = {min_cancers}{', Druggable Only' if druggable_only else ''})"
        headers = ["Rank", "Gene", "CCCS", "Dominant Dir", "Sig Cancers", "Survival Sig", "Druggable", "Target Drugs"]

    rows = []
    for idx, row in enumerate(top_df.to_dict(orient="records"), 1):
        rows.append([
            idx,
            row["Gene"],
            f"{row['CCCS']:.4f}",
            row["Direction"],
            row["Significant Cancers"],
            row["Survival Significant"],
            row["Druggable"],
            row["Target Drugs"]
        ])
        
    console.print()
    print_stats_table(
        title=table_title,
        headers=headers,
        rows=rows,
        border_style="green"
    )
    
    # Save CSV rankings
    rankings_csv = out_dir / "pancancer_cccs_rankings.csv"
    results_df.to_csv(rankings_csv, index=False)
    
    if skipped:
        print_warning(
            f"Skipped {len(skipped)} cohort(s) during scoring: " +
            ", ".join(c for c, _ in skipped)
        )
        
    console.print()
    if len(resolved_cancers) == 1:
        print_success(
            f"Completed single-cohort DEG+survival ranking.\n\n"
            f"[bold]Rankings CSV:[/] {rankings_csv}\n",
            title="Ranking Complete"
        )
    else:
        print_success(
            f"Completed cross-cancer consistency scoring and ranking.\n\n"
            f"[bold]CCCS Rankings CSV:[/] {rankings_csv}\n",
            title="Scoring Complete"
        )
