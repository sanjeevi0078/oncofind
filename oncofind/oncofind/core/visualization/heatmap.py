import logging
from pathlib import Path
from typing import List, Dict, Optional, Union
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy.cluster.hierarchy import linkage, leaves_list
from scipy.spatial.distance import pdist
from oncofind.exceptions import VisualizationError

logger = logging.getLogger(__name__)


def plot_heatmap(
    expression_df: pd.DataFrame,
    genes: List[str],
    output_html_path: Optional[Path] = None,
    title: str = "Expression Heatmap",
    group_series: Optional[pd.Series] = None,
    z_score: bool = True
) -> Union[Path, go.Figure]:
    """
    Generate an interactive Plotly expression heatmap and save as HTML.
    Performs hierarchical clustering on genes (rows) and orders samples (columns) 
    by clinical groups, showing a group annotation bar.
    
    Args:
        expression_df: DataFrame with sample_barcode index and genes as columns.
        genes: List of gene symbols to plot.
        output_html_path: Destination path for HTML file (optional).
        title: Title of the heatmap.
        group_series: Series mapping sample_barcode to clinical group.
        z_score: Whether to perform row (gene) Z-score standardization.
    """
    if expression_df.empty or not genes:
        raise VisualizationError("Cannot plot heatmap: empty data or empty gene list.")

    # Filter to only the genes present in the dataframe
    available_genes = [g for g in genes if g in expression_df.columns]
    if not available_genes:
        raise VisualizationError("None of the specified genes found in expression data.")

    # Extract matrix (transpose so genes are rows, samples are columns)
    # df shape: (genes, samples)
    df = expression_df[available_genes].T
    
    # Apply Z-score if requested
    if z_score:
        # Avoid division by zero
        row_means = df.mean(axis=1)
        row_stds = df.std(axis=1).replace(0, 1.0)
        df_z = df.sub(row_means, axis=0).div(row_stds, axis=0)
    else:
        df_z = df.copy()

    # Clip extreme values for better color scale range (standard in heatmaps)
    if z_score:
        df_z = df_z.clip(lower=-3, upper=3)

    # 1. Cluster Genes (Rows)
    gene_order = list(range(len(available_genes)))
    if len(available_genes) > 1:
        try:
            # Calculate pairwise distance and linkage
            dist_matrix = pdist(df_z.values, metric="euclidean")
            linkage_matrix = linkage(dist_matrix, method="ward")
            gene_order = leaves_list(linkage_matrix).tolist()
        except Exception as e:
            logger.warning(f"Hierarchical clustering of genes failed: {e}. Using original order.")

    ordered_genes = [available_genes[i] for i in gene_order]
    df_ordered = df_z.iloc[gene_order]

    # 2. Sort Samples (Columns) by Group
    if group_series is not None:
        # Align group series with columns of df_ordered
        group_aligned = group_series.loc[df_ordered.columns].dropna()
        # Sort samples: first by group label, then by column name
        sorted_samples = group_aligned.sort_values().index.tolist()
        # Append any remaining samples that didn't have groups
        remaining_samples = [s for s in df_ordered.columns if s not in sorted_samples]
        ordered_samples = sorted_samples + remaining_samples
    else:
        ordered_samples = df_ordered.columns.tolist()

    df_final = df_ordered[ordered_samples]

    # 3. Build Plotly figure
    # If groups are provided, we make subplots: top row = Group Bar (height 5-10%), bottom row = Heatmap
    if group_series is not None:
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            row_heights=[0.05, 0.95]
        )
        
        # Build Group Bar data
        groups_for_samples = [str(group_series.get(s, "Unknown")) for s in ordered_samples]
        unique_groups = sorted(list(set(groups_for_samples)))
        
        # Map groups to integers/colors
        group_to_int = {g: i for i, g in enumerate(unique_groups)}
        group_ints = [group_to_int[g] for g in groups_for_samples]
        
        # Color palettes for groups
        group_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
        colorscale_groups = []
        n_grps = len(unique_groups)
        for i, g in enumerate(unique_groups):
            color = group_colors[i % len(group_colors)]
            if n_grps > 1:
                colorscale_groups.append((i / (n_grps - 1), color))
            else:
                colorscale_groups.append((0.0, color))
                colorscale_groups.append((1.0, color))
                
        # Heatmap for groups (single row)
        fig.add_trace(
            go.Heatmap(
                z=[group_ints],
                x=ordered_samples,
                y=["Group"],
                colorscale=colorscale_groups,
                showscale=False,
                hoverinfo="text",
                text=[[f"Sample: {s}<br>Group: {g}" for s, g in zip(ordered_samples, groups_for_samples)]],
            ),
            row=1, col=1
        )
        
        # Main Heatmap
        fig.add_trace(
            go.Heatmap(
                z=df_final.values,
                x=ordered_samples,
                y=ordered_genes,
                colorscale="RdBu_r" if z_score else "Viridis",
                colorbar=dict(title="Z-Score" if z_score else "Expression", len=0.8, y=0.4),
                hoverinfo="all",
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title=title,
            xaxis=dict(showticklabels=False), # Hide sample names if there are too many
            xaxis2=dict(title="Samples", showticklabels=False),
            yaxis=dict(showticklabels=True),
            yaxis2=dict(title="Genes", showticklabels=True),
            template="plotly_white",
            height=600,
        )
    else:
        fig = go.Figure(
            data=go.Heatmap(
                z=df_final.values,
                x=ordered_samples,
                y=ordered_genes,
                colorscale="RdBu_r" if z_score else "Viridis",
                colorbar=dict(title="Z-Score" if z_score else "Expression"),
            )
        )
        fig.update_layout(
            title=title,
            xaxis=dict(title="Samples", showticklabels=False),
            yaxis=dict(title="Genes", showticklabels=True),
            template="plotly_white",
            height=600,
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
