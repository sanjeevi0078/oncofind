import logging
from pathlib import Path
from typing import Dict, Any, Optional
import plotly.graph_objects as go
from oncofind.core.analysis.survival import SurvivalResult
from oncofind.exceptions import VisualizationError

logger = logging.getLogger(__name__)


def plot_survival(
    survival_result: SurvivalResult,
    output_html_path: Path,
    title: Optional[str] = None
) -> Path:
    """
    Generate an interactive Kaplan-Meier survival curve with confidence intervals
    and save as HTML.
    
    Args:
        survival_result: Result from SurvivalAnalyzer.
        output_html_path: Path to save the interactive HTML file.
        title: Optional title for the plot.
    """
    km_data = survival_result.km_data
    if "high" not in km_data or "low" not in km_data:
        raise VisualizationError("Invalid survival data: 'high' and 'low' groups must be present.")
        
    g = survival_result.gene_symbol
    p_val = survival_result.p_value
    
    # Title formatting
    if not title:
        title = f"Kaplan-Meier Survival Analysis for {g}"
        
    fig = go.Figure()
    
    # 1. Colors
    group_colors = {
        "high": ("rgba(239, 85, 59, 1.0)", "rgba(239, 85, 59, 0.15)"),   # Red
        "low": ("rgba(99, 110, 250, 1.0)", "rgba(99, 110, 250, 0.15)"),  # Blue
        "T2": ("rgba(254, 188, 59, 1.0)", "rgba(254, 188, 59, 0.15)"),   # Amber/Orange
        "Q2": ("rgba(0, 204, 150, 1.0)", "rgba(0, 204, 150, 0.15)"),     # Teal/Green
        "Q3": ("rgba(230, 126, 34, 1.0)", "rgba(230, 126, 34, 0.15)"),   # Orange
    }
    
    # Determine sorted keys order logically
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
            
    max_time = 100.0
    
    for key in keys_order:
        grp = km_data[key]
        timeline = grp["timeline"]
        survival = grp["survival"]
        ci_lower = grp["ci_lower"]
        ci_upper = grp["ci_upper"]
        lbl = grp.get("label", key)
        n_val = grp.get("n", 0)
        
        if timeline:
            max_time = max(max_time, max(timeline))
            
        color, color_ci = group_colors.get(key, ("rgba(128, 128, 128, 1.0)", "rgba(128, 128, 128, 0.15)"))
        
        # CI Upper boundary
        fig.add_trace(go.Scatter(
            x=timeline, y=ci_upper,
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip"
        ))
        # CI Lower boundary with fill
        fig.add_trace(go.Scatter(
            x=timeline, y=ci_lower,
            line=dict(width=0),
            fill="tonexty",
            fillcolor=color_ci,
            showlegend=False,
            hoverinfo="skip"
        ))
        # KM line
        fig.add_trace(go.Scatter(
            x=timeline, y=survival,
            mode="lines",
            line=dict(color=color, width=2.5, shape="hv"),
            name=f"{lbl} (N={n_val})",
            hovertemplate="Days: %{x}<br>Survival: %{y:.2%}<extra></extra>"
        ))
        
    # Format layout & add metadata panel
    p_text = f"Log-rank p-value: {p_val:.4e}" if p_val < 0.0001 else f"Log-rank p-value: {p_val:.4f}"
    if p_val < 0.05:
        p_text += " (Significant)"
        
    annotation_lines = [
        "<b>Statistical Summary:</b>",
        f"• {p_text}"
    ]
    
    for key in keys_order:
        grp = km_data[key]
        lbl = grp.get("label", key)
        med_val = grp.get("median_survival")
        med_str = f"{med_val:.1f} days" if med_val is not None else "Not reached"
        
        surv_3yr = grp.get("surv_3yr")
        surv_5yr = grp.get("surv_5yr")
        extra_info = []
        if surv_3yr is not None:
            extra_info.append(f"3-yr: {surv_3yr:.1%}")
        if surv_5yr is not None:
            extra_info.append(f"5-yr: {surv_5yr:.1%}")
            
        if extra_info:
            med_str += f" ({', '.join(extra_info)})"
            
        annotation_lines.append(f"• Median Survival ({lbl}): {med_str}")
        
    annotation_text = "<br>".join(annotation_lines)
    
    fig.update_layout(
        title=title,
        xaxis_title="Survival Time (Days)",
        yaxis_title="Overall Survival Probability",
        yaxis_range=[0.0, 1.02],
        xaxis_range=[0, max_time * 1.02],
        template="plotly_white",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor="rgba(255, 255, 255, 0.7)"
        ),
        annotations=[
            dict(
                text=annotation_text,
                align="left",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.05, y=0.05,
                bordercolor="black",
                borderwidth=1,
                borderpad=8,
                bgcolor="rgba(255, 255, 255, 0.8)",
                font=dict(size=11)
            )
        ],
        height=550,
        margin=dict(l=60, r=40, t=60, b=60)
    )
    
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
