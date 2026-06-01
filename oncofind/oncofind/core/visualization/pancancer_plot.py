import logging
from pathlib import Path
from typing import Optional
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from oncofind.core.analysis.cccs import CCCSResult
from oncofind.exceptions import VisualizationError

logger = logging.getLogger(__name__)


def plot_pancancer_comparison(
    cccs_result: CCCSResult,
    output_html_path: Path,
    title: Optional[str] = None
) -> Path:
    """
    Generate an interactive dashboard comparing Log2FC and Survival p-value 
    across all tested cancer types for a single gene.
    
    Args:
        cccs_result: Result from CrossCancerConsistencyScorer.
        output_html_path: Target HTML path.
        title: Optional title.
    """
    if not cccs_result.cancer_results:
        raise VisualizationError("No cancer results available in CCCSResult to plot.")
        
    g = cccs_result.gene_symbol
    
    # Extract data into a flat DataFrame
    records = []
    for r in cccs_result.cancer_results:
        records.append({
            "Cancer": r.cancer_type,
            "Log2FC": r.log2fc,
            "padj": r.padj if not np.isnan(r.padj) else 1.0,
            "Direction": r.direction,
            "Survival_P": r.survival_pvalue if r.survival_pvalue is not None and not np.isnan(r.survival_pvalue) else 1.0
        })
        
    df = pd.DataFrame(records)
    df["-log10_padj"] = -np.log10(df["padj"].clip(lower=1e-15))
    df["-log10_survival_p"] = -np.log10(df["Survival_P"].clip(lower=1e-15))
    
    # Sort by cancer code alphabetically
    df = df.sort_values(by="Cancer")
    
    # Create subplots: 1 row, 2 columns
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            f"Differential Expression (Log2 Fold Change)",
            f"Survival Association (-Log10 P-Value)"
        ),
        horizontal_spacing=0.15
    )
    
    # Color mapping for DEGs
    # Red for Up, Blue for Down, Grey for Non-significant
    colors_deg = []
    for _, row in df.iterrows():
        if row["Direction"] == "up":
            colors_deg.append("#EF553B")
        elif row["Direction"] == "down":
            colors_deg.append("#636EFA")
        else:
            colors_deg.append("#CCCCCC")
            
    # Panel 1: Bar chart of Log2 Fold Change
    fig.add_trace(
        go.Bar(
            x=df["Cancer"],
            y=df["Log2FC"],
            marker_color=colors_deg,
            text=df["Log2FC"].round(2),
            textposition="auto",
            hovertemplate="<b>%{x}</b><br>Log2FC: %{y:.3f}<br>Adjusted P-val: %{customdata:.3e}<extra></extra>",
            customdata=df["padj"],
            name="Log2FC"
        ),
        row=1, col=1
    )
    
    # Panel 2: Bar chart of -log10 Survival P-value
    # Highlight significant survival associations
    colors_surv = ["#AB63FA" if p < 0.05 else "#CCCCCC" for p in df["Survival_P"]]
    
    fig.add_trace(
        go.Bar(
            x=df["Cancer"],
            y=df["-log10_survival_p"],
            marker_color=colors_surv,
            text=df["Survival_P"].apply(lambda p: f"p={p:.3f}" if p >= 0.001 else f"p={p:.2e}"),
            textposition="auto",
            hovertemplate="<b>%{x}</b><br>Survival P-value: %{customdata:.3e}<extra></extra>",
            customdata=df["Survival_P"],
            name="-Log10 Survival P"
        ),
        row=1, col=2
    )
    
    # Add horizontal significance threshold lines
    # Panel 1 has no threshold line but we can add a zero reference line
    fig.add_shape(
        type="line", x0=-0.5, x1=len(df) - 0.5, y0=0, y1=0,
        line=dict(color="black", width=1),
        row=1, col=1
    )
    
    # Panel 2 has significance threshold line at -log10(0.05) = 1.301
    fig.add_shape(
        type="line", x0=-0.5, x1=len(df) - 0.5, y0=-np.log10(0.05), y1=-np.log10(0.05),
        line=dict(color="red", width=1.5, dash="dash"),
        row=1, col=2
    )
    # Add annotation for the threshold line in Panel 2
    fig.add_annotation(
        x=len(df)-1.2, y=-np.log10(0.05) + 0.1,
        text="p = 0.05",
        showarrow=False,
        font=dict(color="red", size=10),
        row=1, col=2
    )
    
    # Update layouts
    fig.update_layout(
        title=title if title else f"Pan-Cancer Analysis Dashboard for {g} (CCCS = {cccs_result.cccs:.2f})",
        showlegend=False,
        template="plotly_white",
        height=500,
        margin=dict(l=60, r=40, t=80, b=60)
    )
    
    fig.update_xaxes(title_text="Cancer Cohort", row=1, col=1)
    fig.update_xaxes(title_text="Cancer Cohort", row=1, col=2)
    fig.update_yaxes(title_text="Log2 Fold Change", row=1, col=1)
    fig.update_yaxes(title_text="-Log10 Survival P-value", row=1, col=2)
    
    # Save HTML
    output_html_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_html_path), include_plotlyjs="cdn")
    
    # Try saving PNG
    try:
        output_png_path = output_html_path.with_suffix(".png")
        fig.write_image(str(output_png_path), engine="kaleido")
    except Exception as e:
        logger.warning(f"Failed to export static PNG via Kaleido (can be ignored): {e}")
        
    return output_html_path
