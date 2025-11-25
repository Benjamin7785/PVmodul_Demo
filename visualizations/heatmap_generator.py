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
    
    # Create 2D array of power dissipation
    cells_per_row = 12
    num_rows = module.cells_per_string // cells_per_row
    
    # Initialize power array
    power_array = []
    cell_labels = []
    
    for string_idx in range(module.num_strings):
        string_powers = []
        string_labels = []
        
        for cell_idx in range(module.cells_per_string):
            V_cell = voltage_map['cell_voltages'][string_idx][cell_idx]
            
            if V_cell < 0:
                # Reverse bias - dissipating power
                power = -V_cell * current
            else:
                power = 0.0
            
            string_powers.append(power)
            string_labels.append(f"S{string_idx+1}C{cell_idx}<br>{power:.2f}W")
        
        # Reshape to 2D grid
        power_grid = np.array(string_powers).reshape(num_rows, cells_per_row)
        label_grid = np.array(string_labels).reshape(num_rows, cells_per_row)
        
        power_array.append(power_grid)
        cell_labels.append(label_grid)
    
    # Concatenate strings vertically
    power_matrix = np.vstack(power_array)
    label_matrix = np.vstack(cell_labels)
    
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
        xaxis=dict(title="Zellposition (horizontal)", showgrid=False),
        yaxis=dict(title="String / Zellreihe", showgrid=False),
        height=600,
        width=1000
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
    
    # Create 2D array of voltages
    cells_per_row = 12
    num_rows = module.cells_per_string // cells_per_row
    
    voltage_array = []
    cell_labels = []
    
    for string_idx in range(module.num_strings):
        voltages = voltage_map['cell_voltages'][string_idx]
        
        # Reshape to 2D grid
        voltage_grid = np.array(voltages).reshape(num_rows, cells_per_row)
        label_grid = np.array([f"S{string_idx+1}C{i}<br>{v:.3f}V" 
                               for i, v in enumerate(voltages)]).reshape(num_rows, cells_per_row)
        
        voltage_array.append(voltage_grid)
        cell_labels.append(label_grid)
    
    # Concatenate strings vertically
    voltage_matrix = np.vstack(voltage_array)
    label_matrix = np.vstack(cell_labels)
    
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
        xaxis=dict(title="Zellposition (horizontal)", showgrid=False),
        yaxis=dict(title="String / Zellreihe", showgrid=False),
        height=600,
        width=1000
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
    
    cells_per_row = 12
    num_rows = module.cells_per_string // cells_per_row
    
    # Estimate temperature rise from power dissipation
    # Simple model: Delta_T = P * R_th
    R_th = 5  # °C/W thermal resistance (simplified)
    
    temp_array = []
    
    for string_idx in range(module.num_strings):
        voltages = voltage_map['cell_voltages'][string_idx]
        
        temps = []
        for V_cell in voltages:
            if V_cell < 0:
                power = -V_cell * current
                temp = ambient_temp + power * R_th
            else:
                temp = ambient_temp + 2  # Small increase from normal operation
            temps.append(temp)
        
        temp_grid = np.array(temps).reshape(num_rows, cells_per_row)
        temp_array.append(temp_grid)
    
    temp_matrix = np.vstack(temp_array)
    
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
    cells_per_row = 12
    num_rows = module.cells_per_string // cells_per_row
    
    shading_array = []
    
    for string_idx in range(module.num_strings):
        shading_factors = [cell.shading_factor for cell in module.strings[string_idx].cells]
        shading_grid = np.array(shading_factors).reshape(num_rows, cells_per_row)
        shading_array.append(shading_grid)
    
    shading_matrix = np.vstack(shading_array)
    
    fig = go.Figure(data=go.Heatmap(
        z=shading_matrix * 100,  # Convert to percentage
        colorscale='gray_r',
        colorbar=dict(title="Verschattung (%)"),
        hovertemplate='Verschattung: %{z:.0f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="Verschattungsmuster",
        xaxis=dict(title="Zellposition", showgrid=False),
        yaxis=dict(title="String / Reihe", showgrid=False),
        height=500,
        width=900
    )
    
    return fig

