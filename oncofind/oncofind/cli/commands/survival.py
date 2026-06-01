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
    validate_gene_symbols
)
from oncofind.cli.utils.console import print_stats_table, print_error, print_success
from oncofind.cli.utils.manifest import write_manifest
from oncofind.core.analysis.survival import SurvivalAnalyzer
from oncofind.core.visualization.survival_plot import plot_survival

app = typer.Typer(help="Perform survival analysis for a specific gene")
console = Console()


@app.callback(invoke_without_command=True)
def survival(
    cancer: str = typer.Option(..., "--cancer", "-c", help="TCGA cancer type (e.g. BRCA)"),
    gene: str = typer.Option(..., "--gene", "-g", help="Gene symbol (e.g. ERBB2)"),
    split: str = typer.Option(
        "median", "--split", help="How to split expression: 'median', 'quartile', 'optimal', 'tertile', or 'quartile_4way'"
    ),
    output_dir: Optional[Path] = typer.Option(
        None, "--output-dir", "-o", help="Where to save plots and tables (defaults to ./oncofind_results)"
    ),
):
    """Run survival analysis (Kaplan-Meier & Log-rank) for a gene."""
    # 1. Validate inputs
    cancer_clean = validate_cancer_type(cancer)
    data_dir = settings.data_dir
    expr_store, clin_store = validate_data_downloaded(cancer_clean, data_dir)
    
    # Verify the gene exists
    validated_genes = validate_gene_symbols(expr_store, cancer_clean, [gene])
    gene_clean = validated_genes[0]
    
    # 2. Setup output directories
    out_dir = output_dir if output_dir else Path("./oncofind_results")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 3. Query expression
        with console.status(f"[bold blue]Loading expression and clinical records for {gene_clean}...", spinner="dots"):
            expression_df = expr_store.query_expression(cancer_clean, [gene_clean])
            clinical_df = clin_store.get_clinical_df(cancer_clean)
            
        # 4. Run survival analysis
        with console.status(f"[bold blue]Performing Kaplan-Meier fitting and Log-rank test...", spinner="dots"):
            analyzer = SurvivalAnalyzer()
            result = analyzer.analyze(expression_df, clinical_df, gene_clean, split_method=split)
            
        # 5. Build dynamic interpretation text
        p_val = result.p_value
        p_str = f"{p_val:.4e}" if p_val < 0.0001 else f"{p_val:.4f}"
        
        med_high = result.median_survival_high
        med_low = result.median_survival_low
        
        if p_val < 0.05:
            # Significant survival association
            if med_high is not None and med_low is not None:
                if med_high < med_low:
                    interpretation = (
                        f"High {gene_clean} expression is associated with significantly worse survival "
                        f"(p={p_str}, median survival {med_high:.1f} vs {med_low:.1f} days). "
                        f"This is consistent with {gene_clean} acting as a potential oncogene."
                    )
                else:
                    interpretation = (
                        f"High {gene_clean} expression is associated with significantly better survival "
                        f"(p={p_str}, median survival {med_high:.1f} vs {med_low:.1f} days). "
                        f"This is consistent with {gene_clean} acting as a potential tumor suppressor."
                    )
            else:
                interpretation = (
                    f"High {gene_clean} expression shows a significant overall survival correlation (p={p_str}). "
                    f"However, median survival times could not be fully resolved."
                )
        else:
            interpretation = (
                f"High {gene_clean} expression does not show a statistically significant survival association "
                f"(p={p_str})."
            )
            
        # 6. Save Plotly HTML and PNG
        plot_html_filename = f"{cancer_clean}_{gene_clean}_survival.html"
        plot_html_path = out_dir / plot_html_filename
        plot_survival(result, plot_html_path)
        
        # 7. Print Rich output
        console.print()
        
        # Determine sorted keys order logically
        km_data = result.km_data
        if "T2" in km_data:
            keys_order = ["low", "T2", "high"]
        elif "Q2" in km_data or "Q3" in km_data:
            keys_order = ["low", "Q2", "Q3", "high"]
        else:
            keys_order = ["low", "high"]
            
        keys_order = [k for k in keys_order if k in km_data]
        for k in km_data:
            if k not in keys_order:
                keys_order.append(k)
                
        headers = ["Metric"]
        for key in keys_order:
            grp = km_data[key]
            lbl = grp.get("label", key)
            n_val = grp.get("n", 0)
            headers.append(f"{lbl} (N={n_val})")
            
        med_survival_row = ["Median Survival"]
        for key in keys_order:
            grp = km_data[key]
            med_val = grp.get("median_survival")
            med_str = f"{med_val:.1f} days" if med_val is not None else "Not reached"
            med_survival_row.append(med_str)
            
        surv_3yr_row = ["3-Year Survival"]
        for key in keys_order:
            grp = km_data[key]
            val = grp.get("surv_3yr")
            val_str = f"{val:.1%}" if val is not None else "N/A"
            surv_3yr_row.append(val_str)
            
        surv_5yr_row = ["5-Year Survival"]
        for key in keys_order:
            grp = km_data[key]
            val = grp.get("surv_5yr")
            val_str = f"{val:.1%}" if val is not None else "N/A"
            surv_5yr_row.append(val_str)
            
        p_row = ["Log-rank p-value", p_str] + [""] * (len(keys_order) - 1)
        
        print_stats_table(
            title=f"Kaplan-Meier Analysis: {gene_clean} in TCGA-{cancer_clean}",
            headers=headers,
            rows=[med_survival_row, surv_3yr_row, surv_5yr_row, p_row]
        )
        
        console.print(Panel(
            f"[bold]Interpretation:[/] {interpretation}",
            title="Biological Insight",
            border_style="cyan"
        ))
        
        write_manifest(
            out_dir, "survival",
            params={"cancer": cancer_clean, "gene": gene_clean, "split": split},
            data_files=[
                expr_store.get_expression_path(cancer_clean),
                clin_store.get_clinical_path(cancer_clean),
            ],
            result_summary={"logrank_pvalue": result.p_value, "median_survival_high": result.median_survival_high, "median_survival_low": result.median_survival_low},
        )
        console.print()
        print_success(
            f"Successfully executed survival analysis.\n\n"
            f"[bold]Survival Plot:[/] {plot_html_path}\n"
            f"[bold]Output Data CSV:[/] {out_dir / f'{cancer_clean}_{gene_clean}_survival_groups.csv'}\n",
            title="Analysis Complete"
        )
        
        # Save sample grouping metadata
        groups_df = pd.DataFrame(index=expression_df.index)
        groups_df["expression"] = expression_df[gene_clean]
        groups_df["group"] = "Unknown"
        for key in keys_order:
            grp = km_data[key]
            lbl = grp.get("label", key)
            barcodes = grp.get("barcodes", [])
            groups_df.loc[barcodes, "group"] = lbl
        groups_df.to_csv(out_dir / f"{cancer_clean}_{gene_clean}_survival_groups.csv")
        
    except Exception as e:
        print_error(f"Survival analysis failed: {e}", title="Execution Error")
        raise typer.Exit(code=1)
