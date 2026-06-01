import logging
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from oncofind.exceptions import VisualizationError

logger = logging.getLogger(__name__)


def generate_report(
    cancer_type: str,
    groupby: str,
    group_a_val: str,
    group_b_val: str,
    n_group_a: int,
    n_group_b: int,
    method: str,
    deg_df: pd.DataFrame,
    fdr_threshold: float,
    fc_threshold: float,
    output_html_path: Path,
    volcano_html: Optional[str] = None,
    heatmap_html: Optional[str] = None,
    include_methods: bool = True
) -> Path:
    """
    Compile a self-contained HTML report with embedded Plotly plots and clinical stats.
    
    Args:
        cancer_type: TCGA cancer code.
        groupby: Clinical variable grouped by.
        group_a_val: Label of Group A.
        group_b_val: Label of Group B.
        n_group_a: Sample count of Group A.
        n_group_b: Sample count of Group B.
        method: Method used ('deseq2' or 'ttest').
        deg_df: DataFrame of differential expression results.
        fdr_threshold: FDR significance threshold.
        fc_threshold: Log2 Fold Change significance threshold.
        output_html_path: Destination HTML path.
        volcano_html: HTML div string for volcano plot.
        heatmap_html: HTML div string for heatmap.
        include_methods: Whether to render methodology explanation.
    """
    template_dir = Path(__file__).parent / "templates"
    if not template_dir.exists():
        raise VisualizationError(f"Report template directory {template_dir} does not exist.")
        
    loader = FileSystemLoader(str(template_dir))
    env = Environment(loader=loader)
    
    try:
        template = env.get_template("report.html.j2")
    except Exception as e:
        raise VisualizationError(f"Failed to load report.html.j2 template: {e}")
        
    # Get top 50 DEGs to show in the table (sorted by padj ascending, then absolute log2FC descending)
    df_temp = deg_df.copy()
    df_temp["abs_fc"] = df_temp["log2FC"].abs()
    
    # Sort by padj ascending (significant first), then absolute fold change descending
    df_sorted = df_temp.sort_values(
        by=["padj", "abs_fc"], 
        ascending=[True, False]
    )
    
    # Take top 50 genes for display
    from oncofind.config.druggability import is_druggable, get_drugs_for_gene
    
    top_genes = df_sorted.head(50).to_dict(orient="records")
    for g in top_genes:
        symbol = g["gene_symbol"]
        g["is_druggable"] = is_druggable(symbol)
        g["drugs"] = get_drugs_for_gene(symbol)
    
    # Prepare rendering context
    context = {
        "cancer_type": cancer_type,
        "groupby": groupby,
        "group_a_val": group_a_val,
        "group_b_val": group_b_val,
        "n_group_a": n_group_a,
        "n_group_b": n_group_b,
        "method": method,
        "top_degs": top_genes,
        "fdr_threshold": fdr_threshold,
        "fc_threshold": fc_threshold,
        "volcano_html": volcano_html,
        "heatmap_html": heatmap_html,
        "include_methods": include_methods
    }
    
    try:
        rendered = template.render(context)
    except Exception as e:
        raise VisualizationError(f"Failed to render HTML report template: {e}")
        
    # Write to target path
    output_html_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(rendered)
        
    logger.info(f"HTML report successfully generated at {output_html_path}")
    return output_html_path
