import sys
from typing import List, Tuple, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()
stderr_console = Console(stderr=True)


def print_success(message: str, title: str = "Success"):
    """Print a success panel."""
    console.print(Panel.fit(
        f"[bold green]✓ {message}[/]",
        title=title,
        border_style="green"
    ))


def print_warning(message: str, title: str = "Warning"):
    """Print a warning panel."""
    console.print(Panel.fit(
        f"[bold yellow]⚠ {message}[/]",
        title=title,
        border_style="yellow"
    ))


def print_error(message: str, title: str = "Error"):
    """Print an error panel to stderr."""
    stderr_console.print(Panel.fit(
        f"[bold red]❌ {message}[/]",
        title=title,
        border_style="red"
    ))


def print_info(message: str):
    """Print an informational message."""
    console.print(f"[blue]ℹ[/] {message}")


def print_stats_table(
    title: str,
    headers: List[str],
    rows: List[List[Any]],
    border_style: str = "blue"
):
    """Print a styled data table."""
    table = Table(title=title, border_style=border_style, show_header=True, header_style="bold cyan")
    
    for h in headers:
        table.add_column(h)
        
    for r in rows:
        table.add_row(*[str(val) for val in r])
        
    console.print(table)


def get_progress(description: str = "Processing...") -> Progress:
    """Return a standard Rich Progress bar configuration."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn()
    )
