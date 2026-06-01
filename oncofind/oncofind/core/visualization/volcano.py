import logging
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Union

logger = logging.getLogger(__name__)


def plot_volcano(
    deg_df: pd.DataFrame,
    output_html_path: Optional[Path] = None,
    title: str = "Volcano Plot",
    log2fc_threshold: float = 1.0,
    padj_threshold: float = 0.05
) -> Union[Path, go.Figure]:
    """
    Generate an interactive Plotly volcano plot and save as HTML.
    Attempts to save static PNG if Kaleido is available.
    """
    df = deg_df.copy()
    
    # Clip extreme padj to avoid log10(0)
    df["padj_clipped"] = df["padj"].clip(lower=1e-15)
    df["neg_log10_padj"] = -np.log10(df["padj_clipped"])
    
    # Add grouping for colors
    df["Significance"] = "Not Significant"
    df.loc[(df["padj"] < padj_threshold) & (df["log2FC"] > log2fc_threshold), "Significance"] = "Upregulated"
    df.loc[(df["padj"] < padj_threshold) & (df["log2FC"] < -log2fc_threshold), "Significance"] = "Downregulated"
    
    color_map = {
        "Upregulated": "#EF553B",    # Vibrant red/orange
        "Downregulated": "#636EFA",  # Deep blue
        "Not Significant": "#CCCCCC"  # Grey
    }
    
    # Build scatter plot
    fig = px.scatter(
        df,
        x="log2FC",
        y="neg_log10_padj",
        color="Significance",
        color_discrete_map=color_map,
        hover_name="gene_symbol",
        hover_data={"log2FC": ":.3f", "padj": ":.3e", "neg_log10_padj": False, "Significance": True},
        title=title,
        labels={"log2FC": "Log2 Fold Change", "neg_log10_padj": "-Log10 Adjusted P-Value"},
        template="plotly_white"
    )
    
    # Add threshold lines
    fig.add_shape(
        type="line", x0=-log2fc_threshold, x1=-log2fc_threshold, y0=0, y1=df["neg_log10_padj"].max() * 1.05,
        line=dict(color="grey", width=1, dash="dash")
    )
    fig.add_shape(
        type="line", x0=log2fc_threshold, x1=log2fc_threshold, y0=0, y1=df["neg_log10_padj"].max() * 1.05,
        line=dict(color="grey", width=1, dash="dash")
    )
    fig.add_shape(
        type="line", x0=df["log2FC"].min() * 1.05, x1=df["log2FC"].max() * 1.05,
        y0=-np.log10(padj_threshold), y1=-np.log10(padj_threshold),
        line=dict(color="grey", width=1, dash="dash")
    )
    
    fig.update_layout(
        title_font_size=20,
        xaxis_title_font_size=14,
        yaxis_title_font_size=14,
        legend_title_text="",
        legend_font_size=12
    )
    
    if output_html_path is None:
        return fig
        
    # Save HTML
    output_html_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_html_path), include_plotlyjs="cdn")
    
    # Try saving PNG
    try:
        output_png_path = output_html_path.with_suffix(".png")
        fig.write_image(str(output_png_path))
    except Exception as e:
        logger.warning(f"Failed to export static PNG via Kaleido (can be ignored): {e}")
        
    return output_html_path
