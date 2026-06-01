import asyncio
import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel

from oncofind.config.settings import settings
from oncofind.config.cancer_types import is_valid_cancer, get_cancer_metadata
from oncofind.core.data.gdc_client import GDCClient
from oncofind.core.data.expression_store import ExpressionStore
from oncofind.core.data.clinical_store import ClinicalStore
from oncofind.exceptions import APIError

app = typer.Typer(help="Download RNA-seq and clinical data from GDC")
console = Console()


async def run_download(cancer: str, data_dir: Path, n_samples: Optional[int], dry_run: bool):
    """Run the async GDC download pipeline."""
    # Ensure settings directories are initialized
    store_dir = data_dir if data_dir else settings.data_dir
    store_dir.mkdir(parents=True, exist_ok=True)
    
    client = GDCClient()
    expr_store = ExpressionStore(store_dir)
    clin_store = ClinicalStore(store_dir)
    
    try:
        with console.status(f"[bold blue]Querying GDC for TCGA-{cancer.upper()} RNA-seq files...", spinner="dots"):
            file_hits = await client.query_files(cancer, n_samples)
            
        if not file_hits:
            console.print(f"[bold red]Error:[/] No RNA-seq samples found for cancer type TCGA-{cancer.upper()}.")
            raise typer.Exit(1)
            
        total_samples = len(file_hits)
        total_size_mb = sum(f["file_size"] for f in file_hits) / (1024 * 1024)
        
        console.print(Panel.fit(
            f"[bold green]✓ Found {total_samples} samples for TCGA-{cancer.upper()}[/]\n"
            f"[bold]Total Size:[/] {total_size_mb:.2f} MB",
            title="GDC Dataset Query Result",
            border_style="green"
        ))
        
        if dry_run:
            console.print("[bold yellow]Dry-run enabled. Skipping file download.[/]")
            console.print(f"Would download {total_samples} files to {store_dir / cancer.upper()}")
            await client.close()
            return
            
        # Download files
        cancer_raw_dir = store_dir / cancer.upper() / "raw_counts"
        downloaded = await client.download_files_batch(file_hits, cancer_raw_dir)
        
        # Download clinical data
        case_ids = list(set(hit["case_id"] for hit in file_hits))
        with console.status("[bold blue]Querying clinical metadata...", spinner="dots"):
            clinical_records = await client.query_clinical(case_ids)
            
        # Create mapping of sample_barcode -> patient_barcode and sample_type
        sample_to_patient = {hit["sample_barcode"]: hit["patient_barcode"] for hit in file_hits}
        sample_to_type = {hit["sample_barcode"]: hit.get("sample_type", "Primary Tumor") for hit in file_hits}
        
        # Preprocess and save clinical data
        with console.status("[bold blue]Processing clinical data...", spinner="dots"):
            clin_store.save_clinical_data(cancer, clinical_records, sample_to_patient, sample_to_type=sample_to_type)
            
        # Pivot count files and save as Parquet
        with console.status("[bold blue]Preprocessing RNA-seq count matrix to Parquet...", spinner="dots"):
            expr_store.preprocess_files(cancer, downloaded)
            
        console.print(Panel.fit(
            f"[bold green]✓ Preprocessed expression and clinical data successfully saved.[/]\n"
            f"[bold]Expression Matrix:[/] {expr_store.get_expression_path(cancer)}\n"
            f"[bold]Clinical Metadata:[/] {clin_store.get_clinical_path(cancer)}\n\n"
            f"Ready. Run: [bold cyan]oncofind deg --cancer {cancer.upper()} --groupby stage[/]",
            title="Success",
            border_style="green"
        ))
        
    except APIError as e:
        console.print(f"[bold red]API Error:[/] {e}")
        raise typer.Exit(1)
    finally:
        await client.close()


@app.callback(invoke_without_command=True)
def download(
    cancer: str = typer.Option(..., "--cancer", "-c", help="TCGA cancer type (e.g. BRCA, LUAD)"),
    data_dir: Optional[Path] = typer.Option(
        None, "--data-dir", "-d", help="Where to store data (defaults to ~/.oncofind/data)"
    ),
    n_samples: Optional[int] = typer.Option(
        None, "--n-samples", "-n", help="Limit download to N samples (default: all)"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be downloaded without downloading"
    ),
):
    """Download TCGA genomics and clinical metadata from GDC."""
    # Validate cancer type
    if not is_valid_cancer(cancer):
        # Suggest valid choices
        from oncofind.config.cancer_types import CANCER_REGISTRY
        valid_cancers = ", ".join(CANCER_REGISTRY.keys())
        console.print(f"[bold red]Error:[/] Cancer '{cancer}' is not supported.")
        console.print(f"Supported cancer types: [bold cyan]{valid_cancers}[/]")
        raise typer.Exit(1)
        
    asyncio.run(run_download(cancer, data_dir, n_samples, dry_run))
