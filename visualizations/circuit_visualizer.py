"""
Circuit diagram visualization for PV modules
"""

import plotly.graph_objects as go
import numpy as np


def create_module_circuit_diagram(module, current=None, show_voltages=True):
    """
    Create interactive circuit diagram of PV module
    
    Parameters:
    -----------
    module : PVModule
        Module object
    current : float or None
        Operating current (if None, uses MPP)
    show_voltages : bool
        Whether to show voltage values on cells
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    if current is None:
        mpp = module.find_mpp()
        current = mpp['current']
    
    # Get voltage map
    voltage_map_data = module.get_cell_voltage_map(current)
    cell_voltages = voltage_map_data['cell_voltages']
    bypass_states = voltage_map_data['bypass_states']
    
    fig = go.Figure()
    
    # Layout parameters (Realistic PV Module: 6 columns × 18 rows total)
    cell_width = 1.0
    cell_height = 0.5  # Halbzellen sind breiter als hoch
    total_columns = 6  # Gesamtbreite des Moduls
    columns_per_string = 2  # Jeder String hat 2 Spalten Breite
    total_rows = 18  # Höhe des Moduls
    
    # Draw each string
    for string_idx in range(module.num_strings):
        voltages = cell_voltages[string_idx]
        
        # String position: String 1 = Spalten 0-1, String 2 = Spalten 2-3, String 3 = Spalten 4-5
        string_column_offset = string_idx * columns_per_string
        
        for cell_idx, V_cell in enumerate(voltages):
            # 36 cells per string arranged in 2 columns × 18 rows
            row = cell_idx // columns_per_string  # Reihe (0-17)
            col = cell_idx % columns_per_string   # Spalte innerhalb String (0-1)
            
            x = string_column_offset + col * cell_width
            y = -row * cell_height  # Top-Down Layout
            
            # Determine color based on voltage
            if V_cell < 0:
                # Reverse bias - red gradient
                color_intensity = min(abs(V_cell) / 15, 1.0)
                color = f'rgb({int(255*color_intensity)}, 0, 0)'
            else:
                # Forward bias - green gradient
                color_intensity = min(V_cell / 0.65, 1.0)
                color = f'rgb(0, {int(200*color_intensity)}, 0)'
            
            # Draw cell as rectangle
            fig.add_shape(
                type="rect",
                x0=x, y0=y, x1=x+cell_width*0.9, y1=y+cell_height*0.9,
                line=dict(color="black", width=1),
                fillcolor=color,
                opacity=0.7
            )
            
            # Add voltage text
            if show_voltages:
                fig.add_annotation(
                    x=x+cell_width*0.45,
                    y=y+cell_height*0.45,
                    text=f"{V_cell:.2f}V",
                    showarrow=False,
                    font=dict(size=6, color='white' if abs(V_cell) > 0.3 else 'black')
                )
        
        # Draw bypass diode symbol
        bypass_x = string_column_offset + columns_per_string * cell_width * 0.5  # Center of string
        bypass_y = -18 * cell_height - 0.5  # Below the module
        
        bypass_color = 'red' if bypass_states[string_idx] else 'gray'
        bypass_text = 'EIN' if bypass_states[string_idx] else 'AUS'
        
        # Diode symbol (triangle)
        fig.add_shape(
            type="path",
            path=f"M {bypass_x},{bypass_y-0.2} L {bypass_x+0.2},{bypass_y} L {bypass_x},{bypass_y+0.2} Z",
            fillcolor=bypass_color,
            line=dict(color=bypass_color, width=2)
        )
        
        fig.add_annotation(
            x=bypass_x,
            y=bypass_y - 0.5,
            text=f"BD{string_idx+1}: {bypass_text}",
            showarrow=False,
            font=dict(size=9, color=bypass_color)
        )
        
        # String label and voltage at top
        string_voltage = sum(voltages)  # Gesamtspannung des Strings
        
        # Farbcodierung basierend auf Spannung und Bypass-Status
        if bypass_states[string_idx]:
            voltage_color = 'red'  # Bypass aktiv
            voltage_bg = 'rgba(255,200,200,0.8)'
        elif string_voltage < -0.2:
            voltage_color = 'orange'  # Nahe an Bypass-Schwelle
            voltage_bg = 'rgba(255,220,180,0.8)'
        else:
            voltage_color = 'green'  # Normal
            voltage_bg = 'rgba(200,255,200,0.8)'
        
        fig.add_annotation(
            x=string_column_offset + columns_per_string * cell_width * 0.5,
            y=1.2,
            text=f"<b>String {string_idx+1}</b>",
            showarrow=False,
            font=dict(size=11, color='black'),
            xanchor='center'
        )
        
        # String-Spannung prominent anzeigen
        fig.add_annotation(
            x=string_column_offset + columns_per_string * cell_width * 0.5,
            y=0.5,
            text=f"<b>{string_voltage:.2f} V</b>",
            showarrow=False,
            font=dict(size=14, color=voltage_color),
            bgcolor=voltage_bg,
            bordercolor=voltage_color,
            borderwidth=2,
            borderpad=4,
            xanchor='center'
        )
    
    # Calculate total voltages for title
    total_voltage = sum([sum(cv) for cv in cell_voltages])
    active_bypasses = sum(bypass_states)
    
    fig.update_layout(
        title=f"PV-Modul - I = {current:.2f} A | V_modul = {total_voltage:.1f} V | Bypass aktiv: {active_bypasses}/3",
        showlegend=False,
        xaxis=dict(visible=False, range=[-0.5, total_columns * cell_width + 0.5]),
        yaxis=dict(visible=False, scaleanchor="x", scaleratio=1),
        height=650,  # Etwas höher für String-Spannungs-Anzeige
        width=400,   # Schmaler für 6 Spalten (realistisches Modul)
        plot_bgcolor='white',
        annotations=list(fig.layout.annotations) + [
            dict(
                text="String-Spannungen oben: 🟢 Normal | 🟠 Kritisch | 🔴 Bypass aktiv (< -0,4V)",
                xref="paper", yref="paper",
                x=0.5, y=-0.05,
                showarrow=False,
                font=dict(size=9, color='gray'),
                xanchor='center'
            )
        ]
    )
    
    return fig


def create_interactive_shading_editor(module):
    """
    Create clickable cell grid for shading pattern editing
    
    Parameters:
    -----------
    module : PVModule
        Module object
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    fig = go.Figure()
    
    cell_width = 1.0
    cell_height = 0.5  # Halbzellen sind breiter als hoch
    total_columns = 6
    columns_per_string = 2
    total_rows = 18
    
    # Draw grid of cells
    cell_data = []
    
    for string_idx in range(module.num_strings):
        string_column_offset = string_idx * columns_per_string
        
        for cell_idx in range(module.cells_per_string):
            row = cell_idx // columns_per_string
            col = cell_idx % columns_per_string
            
            x = string_column_offset + col * cell_width
            y = -row * cell_height
            
            # Check if cell is shaded
            shading_factor = module.strings[string_idx].cells[cell_idx].shading_factor
            
            if shading_factor > 0:
                color = f'rgb({int(255*shading_factor)}, {int(100*(1-shading_factor))}, 0)'
                opacity = 0.8
            else:
                color = 'lightblue'
                opacity = 0.3
            
            # Store cell info
            cell_data.append({
                'x': x + cell_width*0.45,
                'y': y + cell_height*0.45,
                'string': string_idx,
                'cell': cell_idx,
                'shading': shading_factor
            })
            
            fig.add_shape(
                type="rect",
                x0=x, y0=y, x1=x+cell_width*0.9, y1=y+cell_height*0.9,
                line=dict(color="black", width=1),
                fillcolor=color,
                opacity=opacity
            )
    
    # Add scatter trace for hover information (invisible markers)
    fig.add_trace(go.Scatter(
        x=[c['x'] for c in cell_data],
        y=[c['y'] for c in cell_data],
        mode='markers',
        marker=dict(size=20, color='rgba(0,0,0,0)'),
        text=[f"String {c['string']+1}, Zelle {c['cell']}<br>Verschattung: {c['shading']*100:.0f}%" 
              for c in cell_data],
        hoverinfo='text',
        showlegend=False
    ))
    
    fig.update_layout(
        title="Verschattungsmuster Editor (108 Halbzellen: 6×18)",
        showlegend=False,
        xaxis=dict(visible=False, range=[-0.5, total_columns * cell_width + 0.5]),
        yaxis=dict(visible=False, scaleanchor="x", scaleratio=1),
        height=600,  # Angepasst für Rechteckzellen
        width=400,
        plot_bgcolor='white',
        hovermode='closest'
    )
    
    return fig

