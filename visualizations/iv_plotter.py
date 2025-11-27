"""
I-V and P-V curve plotting using Plotly
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


def plot_iv_curve(voltages, currents, powers=None, title="I-V Characteristic", 
                  mpp=None, show_power=True):
    """
    Create I-V curve plot
    
    Parameters:
    -----------
    voltages : array
        Voltage values
    currents : array
        Current values
    powers : array or None
        Power values
    title : str
        Plot title
    mpp : dict or None
        MPP information {'voltage': v, 'current': i, 'power': p}
    show_power : bool
        Whether to show power curve on secondary axis
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    if powers is None:
        powers = voltages * currents
    
    if show_power:
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add I-V curve
        fig.add_trace(
            go.Scatter(
                x=voltages, y=currents,
                name="Strom",
                line=dict(color='blue', width=2),
                mode='lines'
            ),
            secondary_y=False
        )
        
        # Add P-V curve
        fig.add_trace(
            go.Scatter(
                x=voltages, y=powers,
                name="Leistung",
                line=dict(color='red', width=2),
                mode='lines'
            ),
            secondary_y=True
        )
        
        # Add MPP marker if provided
        if mpp is not None:
            fig.add_trace(
                go.Scatter(
                    x=[mpp['voltage']],
                    y=[mpp['current']],
                    mode='markers',
                    marker=dict(size=12, color='green', symbol='star'),
                    name='MPP',
                    showlegend=True
                ),
                secondary_y=False
            )
            fig.add_trace(
                go.Scatter(
                    x=[mpp['voltage']],
                    y=[mpp['power']],
                    mode='markers',
                    marker=dict(size=12, color='green', symbol='star'),
                    showlegend=False
                ),
                secondary_y=True
            )
        
        # Set axis labels
        fig.update_xaxes(title_text="Spannung (V)")
        fig.update_yaxes(title_text="Strom (A)", secondary_y=False)
        fig.update_yaxes(title_text="Leistung (W)", secondary_y=True)
        
    else:
        # Only I-V curve
        fig = go.Figure()
        
        fig.add_trace(
            go.Scatter(
                x=voltages, y=currents,
                name="I-V Kennlinie",
                line=dict(color='blue', width=2),
                mode='lines'
            )
        )
        
        if mpp is not None:
            fig.add_trace(
                go.Scatter(
                    x=[mpp['voltage']],
                    y=[mpp['current']],
                    mode='markers',
                    marker=dict(size=12, color='green', symbol='star'),
                    name='MPP'
                )
            )
        
        fig.update_xaxes(title_text="Spannung (V)")
        fig.update_yaxes(title_text="Strom (A)")
    
    fig.update_layout(
        title=title,
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig


def plot_iv_comparison(data_sets, labels=None, title="I-V Vergleich"):
    """
    Compare multiple I-V curves
    
    Parameters:
    -----------
    data_sets : list of dict
        Each dict contains 'voltages' and 'currents'
    labels : list of str
        Labels for each curve
    title : str
        Plot title
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    fig = go.Figure()
    
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
    
    for i, data in enumerate(data_sets):
        label = labels[i] if labels and i < len(labels) else f"Curve {i+1}"
        color = colors[i % len(colors)]
        
        fig.add_trace(
            go.Scatter(
                x=data['voltages'],
                y=data['currents'],
                name=label,
                line=dict(color=color, width=2),
                mode='lines'
            )
        )
    
    fig.update_layout(
        title=title,
        xaxis_title="Spannung (V)",
        yaxis_title="Strom (A)",
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(x=0.7, y=0.95)
    )
    
    return fig


def plot_power_curve(voltages, powers, mpp=None, title="P-V Characteristic"):
    """
    Create power vs voltage curve
    
    Parameters:
    -----------
    voltages : array
        Voltage values
    powers : array
        Power values
    mpp : dict or None
        MPP information
    title : str
        Plot title
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=voltages,
            y=powers,
            name="Leistung",
            line=dict(color='red', width=2),
            mode='lines',
            fill='tozeroy',
            fillcolor='rgba(255, 0, 0, 0.1)'
        )
    )
    
    if mpp is not None:
        fig.add_trace(
            go.Scatter(
                x=[mpp['voltage']],
                y=[mpp['power']],
                mode='markers+text',
                marker=dict(size=12, color='green', symbol='star'),
                text=[f"MPP: {mpp['power']:.1f} W"],
                textposition="top center",
                name='MPP'
            )
        )
    
    fig.update_layout(
        title=title,
        xaxis_title="Spannung (V)",
        yaxis_title="Leistung (W)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig


def plot_cell_iv_with_breakdown(cell, v_range=(-15, 1), title="Zellkennlinie mit Breakdown"):
    """
    Plot cell I-V curve highlighting breakdown region
    
    Parameters:
    -----------
    cell : SolarCell
        Solar cell object
    v_range : tuple
        Voltage range
    title : str
        Plot title
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    voltages, currents = cell.iv_curve(v_min=v_range[0], v_max=v_range[1], points=500)
    powers = voltages * currents
    
    # Identify breakdown region
    breakdown_mask = voltages < -cell.Vbr * 0.9
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Normal region
    fig.add_trace(
        go.Scatter(
            x=voltages[~breakdown_mask],
            y=currents[~breakdown_mask],
            name="Normal",
            line=dict(color='blue', width=2),
            mode='lines'
        ),
        secondary_y=False
    )
    
    # Breakdown region
    if np.any(breakdown_mask):
        fig.add_trace(
            go.Scatter(
                x=voltages[breakdown_mask],
                y=currents[breakdown_mask],
                name="Breakdown",
                line=dict(color='red', width=3),
                mode='lines'
            ),
            secondary_y=False
        )
    
    # Power curve
    fig.add_trace(
        go.Scatter(
            x=voltages,
            y=powers,
            name="Leistung",
            line=dict(color='green', width=1, dash='dash'),
            mode='lines'
        ),
        secondary_y=True
    )
    
    # Mark breakdown voltage
    fig.add_vline(
        x=-cell.Vbr,
        line_dash="dot",
        line_color="red",
        annotation_text=f"Vbr = {cell.Vbr}V"
    )
    
    fig.update_xaxes(title_text="Spannung (V)")
    fig.update_yaxes(title_text="Strom (A)", secondary_y=False)
    fig.update_yaxes(title_text="Leistung (W)", secondary_y=True)
    
    fig.update_layout(
        title=title,
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig


