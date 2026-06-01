import typer
from pathlib import Path
from typing import Optional
from rich.console import Console

from oncofind.core.validation.cosmic_benchmark import CosmicBenchmark
from oncofind.cli.utils.console import print_error, print_success, print_stats_table

app = typer.Typer(help="Validate CCCS rankings against external databases")
console = Console()


@app.callback(invoke_without_command=True)
def validate(
    cccs_csv: Path = typer.Option(
        ..., "--cccs-csv",
        help="Path to the CCCS results CSV (from: oncofind score --export-csv results.csv)",
        exists=True,
    ),
    cosmic_csv: Optional[Path] = typer.Option(
        None, "--cosmic-csv",
        help=(
            "Path to the COSMIC Cancer Gene Census CSV. "
            "Download free from: https://cancer.sanger.ac.uk/census"
        ),
        exists=True,
    ),
    benchmark_genes_file: Optional[Path] = typer.Option(
        None, "--benchmark-genes-file",
        help="Path to a text file containing a custom list of genes (one per line) to validate against.",
        exists=True,
    ),
    gene_col: str = typer.Option("Gene", "--gene-col", help="Gene symbol column name in CCCS CSV"),
    score_col: str = typer.Option("CCCS", "--score-col", help="CCCS score column name in CCCS CSV"),
    ks: str = typer.Option(
        "10,20,50,100",
        "--ks",
        help="Comma-separated list of K values for Precision@K (e.g. 10,20,50)",
    ),
    export_csv: bool = typer.Option(False, "--export-csv", help="Save benchmark results to benchmark_report.csv"),
):
    """
    Benchmark CCCS rankings against COSMIC Tier 1 or a custom gene list.

    Computes Precision@K: what fraction of your top-K CCCS genes are confirmed
    targets in the benchmark list?

    \b
    Example:
        oncofind score --cancers BRCA LUAD COAD --top-n 200 --export-csv cccs.csv
        oncofind validate --cccs-csv cccs.csv --cosmic-csv census.csv
    """
    import pandas as pd

    # Parse K list
    try:
        k_list = [int(k.strip()) for k in ks.split(",")]
    except ValueError:
        print_error(f"Invalid --ks value '{ks}'. Use comma-separated integers, e.g. 10,20,50", title="Invalid Input")
        raise typer.Exit(code=1)

    # Load CCCS results
    try:
        cccs_df = pd.read_csv(cccs_csv)
    except Exception as e:
        print_error(f"Could not read CCCS CSV: {e}", title="File Error")
        raise typer.Exit(code=1)

    if gene_col not in cccs_df.columns:
        print_error(
            f"Column '{gene_col}' not found in CCCS CSV. "
            f"Available columns: {list(cccs_df.columns)}",
            title="Column Not Found"
        )
        raise typer.Exit(code=1)

    if score_col not in cccs_df.columns:
        print_error(
            f"Column '{score_col}' not found in CCCS CSV. "
            f"Available columns: {list(cccs_df.columns)}",
            title="Column Not Found"
        )
        raise typer.Exit(code=1)

    # Run benchmark
    if benchmark_genes_file is not None:
        with console.status("[bold blue]Loading custom benchmark gene list...", spinner="dots"):
            try:
                with open(benchmark_genes_file, "r") as f:
                    benchmark_genes = set(line.strip().upper() for line in f if line.strip())
            except Exception as e:
                print_error(f"Could not read benchmark genes file: {e}", title="File Error")
                raise typer.Exit(code=1)

        # Sort by CCCS descending
        ranked = cccs_df.sort_values(score_col, ascending=False).reset_index(drop=True)
        ranked_genes = ranked[gene_col].astype(str).str.upper().tolist()

        precision_at_k = {}
        overlap_at_k = {}
        for k in k_list:
            top_k = ranked_genes[:k]
            hits = [g for g in top_k if g in benchmark_genes]
            precision_at_k[k] = len(hits) / k if k > 0 else 0.0
            overlap_at_k[k] = hits

        n_cosmic_tier1 = len(benchmark_genes)
        n_genes_ranked = len(ranked_genes)
        benchmark_title = f"Custom Benchmark — CCCS vs Target Gene List (n={n_cosmic_tier1} genes)"
    else:
        if cosmic_csv is None:
            print_error("Either --cosmic-csv or --benchmark-genes-file must be provided.", title="Missing Argument")
            raise typer.Exit(code=1)

        with console.status("[bold blue]Loading COSMIC Cancer Gene Census...", spinner="dots"):
            bench = CosmicBenchmark(cosmic_csv_path=cosmic_csv)
            bench.load()

        with console.status("[bold blue]Computing Precision@K...", spinner="dots"):
            report = bench.evaluate(cccs_df, gene_col=gene_col, score_col=score_col, ks=k_list)

        precision_at_k = report.precision_at_k
        overlap_at_k = report.overlap_at_k
        n_cosmic_tier1 = report.n_cosmic_tier1
        n_genes_ranked = report.n_genes_ranked
        benchmark_title = f"COSMIC Benchmark — CCCS vs Cancer Gene Census Tier 1 (n={n_cosmic_tier1} genes)"

    # Print rich table
    console.print()
    rows = []
    for k in sorted(precision_at_k.keys()):
        prec = precision_at_k[k]
        hits = len(overlap_at_k[k])
        status = "✅ Strong" if prec >= 0.60 else ("⚠️  Moderate" if prec >= 0.40 else "❌ Weak")
        rows.append([f"Precision@{k}", f"{prec:.1%}  ({hits}/{k})", status])

    print_stats_table(
        title=benchmark_title,
        headers=["Metric", "Value", "Signal"],
        rows=rows,
    )

    # Print top overlapping genes at the highest K
    max_k = max(k_list)
    overlap = overlap_at_k[max_k]
    if overlap:
        label_prefix = "COSMIC Tier 1" if benchmark_genes_file is None else "custom target list"
        console.print(f"\n[bold]Top-{max_k} CCCS genes confirmed in {label_prefix} ({len(overlap)}):[/]")
        console.print(", ".join(overlap[:30]) + ("..." if len(overlap) > 30 else ""))

    console.print(f"\n[dim]Total CCCS genes ranked: {n_genes_ranked}[/]")
    console.print(f"[dim]Benchmark target genes: {n_cosmic_tier1}[/]")

    # Export if requested
    if export_csv:
        out_path = Path("benchmark_report.csv")
        rows_df = []
        for k in sorted(precision_at_k.keys()):
            rows_df.append({
                "K": k,
                "precision": precision_at_k[k],
                "hits": len(overlap_at_k[k]),
                "hits_list": ", ".join(overlap_at_k[k][:20]),
            })
        pd.DataFrame(rows_df).to_csv(out_path, index=False)
        print_success(f"Benchmark results saved to {out_path}", title="Export Complete")

    best_k = min(k_list, key=lambda k: abs(k - 50)) if k_list else k_list[0]
    if precision_at_k.get(best_k, 1.0) < 0.40:
        if benchmark_genes_file is None:
            console.print(
                "\n[bold yellow]⚠️  Note: Precision is below 40%. This is biologically expected because "
                "expression-based analysis primarily captures cell-cycle/proliferation markers "
                "(e.g., NEK2, KIF4A, PKMYT1) which are excellent downstream biomarkers, "
                "whereas COSMIC catalogues primary mutational driver genes (e.g., TP53, PIK3CA). "
                "Precision is also influenced by statistical power in smaller cohorts (n=50).[/]"
            )
        else:
            console.print(
                "\n[bold yellow]⚠️  Note: Precision is below 40%. This may be due to low overlap "
                "between your target gene set and the top-ranked genes, or statistical power limitations.[/]"
            )
