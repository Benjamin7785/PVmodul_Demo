"""
Heatmap visualizations for power dissipation and temperature
"""

import plotly.graph_objects as go
import numpy as np


def create_power_dissipation_heatmap(module, current):
    """
    Create heatmap showing power dissipation in each cell
    
    Parameters:
    -----------
    module : PVModule
        Module object
    current : float
        Operating current
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    hotspot_analysis = module.analyze_hotspots(current)
    voltage_map = module.get_cell_voltage_map(current)
    
    # Create 2D array of power dissipation (Realistic: 6 columns × 18 rows total)
    columns_per_string = 2  # 2 Spalten pro String
    rows_per_string = 18  # 18 Reihen pro String
    
    # Initialize power array (6 columns × 18 rows)
    power_matrix = np.zeros((rows_per_string, 6))
    label_matrix = np.empty((rows_per_string, 6), dtype=object)
    
    for string_idx in range(module.num_strings):
        col_offset = string_idx * columns_per_string
        
        for cell_idx in range(module.cells_per_string):
            V_cell = voltage_map['cell_voltages'][string_idx][cell_idx]
            
            if V_cell < 0:
                power = -V_cell * current
            else:
                power = 0.0
            
            # Position in module grid
            row = cell_idx // columns_per_string
            col = col_offset + (cell_idx % columns_per_string)
            
            power_matrix[row, col] = power
            label_matrix[row, col] = f"S{string_idx+1}C{cell_idx}<br>{power:.2f}W"
    
    fig = go.Figure(data=go.Heatmap(
        z=power_matrix,
        text=label_matrix,
        texttemplate='%{text}',
        textfont={"size": 8},
        colorscale='Hot',
        colorbar=dict(title="Leistung (W)"),
        hovertemplate='%{text}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f"Leistungsdissipation bei I = {current:.2f} A<br>Gesamt Hot-Spot-Leistung: {hotspot_analysis['total_hotspot_power']:.2f} W",
        xaxis=dict(title="Spalten (6 total: S1|S2|S3)", showgrid=False),
        yaxis=dict(title="Reihen (18)", showgrid=False),
        height=600,  # Angepasst für Halbzellen-Proportion
        width=400
    )
    
    return fig


def create_voltage_heatmap(module, current):
    """
    Create heatmap showing voltage distribution
    
    Parameters:
    -----------
    module : PVModule
        Module object
    current : float
        Operating current
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    voltage_map = module.get_cell_voltage_map(current)
    
    # Create 2D array of voltages (Realistic: 6 columns × 18 rows)
    columns_per_string = 2
    rows_per_string = 18
    
    voltage_matrix = np.zeros((rows_per_string, 6))
    label_matrix = np.empty((rows_per_string, 6), dtype=object)
    
    for string_idx in range(module.num_strings):
        col_offset = string_idx * columns_per_string
        voltages = voltage_map['cell_voltages'][string_idx]
        
        for cell_idx, V_cell in enumerate(voltages):
            row = cell_idx // columns_per_string
            col = col_offset + (cell_idx % columns_per_string)
            
            voltage_matrix[row, col] = V_cell
            label_matrix[row, col] = f"S{string_idx+1}C{cell_idx}<br>{V_cell:.3f}V"
    
    # Custom colorscale: red for negative (reverse bias), green for positive
    colorscale = [
        [0.0, 'darkred'],
        [0.4, 'red'],
        [0.5, 'yellow'],
        [0.7, 'lightgreen'],
        [1.0, 'darkgreen']
    ]
    
    fig = go.Figure(data=go.Heatmap(
        z=voltage_matrix,
        text=label_matrix,
        texttemplate='%{text}',
        textfont={"size": 7},
        colorscale=colorscale,
        zmid=0,  # Center colorscale at 0V
        colorbar=dict(title="Spannung (V)"),
        hovertemplate='%{text}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f"Spannungsverteilung bei I = {current:.2f} A",
        xaxis=dict(title="Spalten (6 total: S1|S2|S3)", showgrid=False),
        yaxis=dict(title="Reihen (18)", showgrid=False),
        height=600,  # Angepasst für Halbzellen-Proportion
        width=400
    )
    
    return fig


def create_temperature_distribution_3d(module, current, ambient_temp=25):
    """
    Create 3D surface plot of estimated cell temperatures
    
    Parameters:
    -----------
    module : PVModule
        Module object
    current : float
        Operating current
    ambient_temp : float
        Ambient temperature in °C
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    voltage_map = module.get_cell_voltage_map(current)
    
    columns_per_string = 2
    rows_per_string = 18
    
    # Estimate temperature rise from power dissipation
    # Simple model: Delta_T = P * R_th
    R_th = 5  # °C/W thermal resistance (simplified)
    
    temp_matrix = np.zeros((rows_per_string, 6))
    
    for string_idx in range(module.num_strings):
        col_offset = string_idx * columns_per_string
        voltages = voltage_map['cell_voltages'][string_idx]
        
        for cell_idx, V_cell in enumerate(voltages):
            if V_cell < 0:
                power = -V_cell * current
                temp = ambient_temp + power * R_th
            else:
                temp = ambient_temp + 2
            
            row = cell_idx // columns_per_string
            col = col_offset + (cell_idx % columns_per_string)
            temp_matrix[row, col] = temp
    
    # Create coordinate grids
    x = np.arange(cells_per_row)
    y = np.arange(len(temp_matrix))
    X, Y = np.meshgrid(x, y)
    
    fig = go.Figure(data=[go.Surface(
        x=X, y=Y, z=temp_matrix,
        colorscale='Hot',
        colorbar=dict(title="Temperatur (°C)"),
        hovertemplate='X: %{x}<br>Y: %{y}<br>T: %{z:.1f}°C<extra></extra>'
    )])
    
    fig.update_layout(
        title=f"Temperaturverteilung (I = {current:.2f} A)",
        scene=dict(
            xaxis_title="Zellposition (horizontal)",
            yaxis_title="String / Reihe",
            zaxis_title="Temperatur (°C)"
        ),
        height=600
    )
    
    return fig


def create_shading_pattern_heatmap(module):
    """
    Create heatmap showing shading pattern configuration
    
    Parameters:
    -----------
    module : PVModule
        Module object
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    columns_per_string = 2
    rows_per_string = 18
    
    shading_matrix = np.zeros((rows_per_string, 6))
    
    for string_idx in range(module.num_strings):
        col_offset = string_idx * columns_per_string
        
        for cell_idx, cell in enumerate(module.strings[string_idx].cells):
            row = cell_idx // columns_per_string
            col = col_offset + (cell_idx % columns_per_string)
            shading_matrix[row, col] = cell.shading_factor
    
    fig = go.Figure(data=go.Heatmap(
        z=shading_matrix * 100,  # Convert to percentage
        colorscale='gray_r',
        colorbar=dict(title="Verschattung (%)"),
        hovertemplate='Verschattung: %{z:.0f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="Verschattungsmuster",
        xaxis=dict(title="Spalten (6 total: S1|S2|S3)", showgrid=False),
        yaxis=dict(title="Reihen (18)", showgrid=False),
        height=600,  # Angepasst für Halbzellen-Proportion
        width=400
    )
    
    return fig

