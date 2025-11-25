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
    
    # Layout parameters
    cell_width = 1.0
    cell_height = 0.5
    string_spacing = 2.0
    cells_per_row = 12
    
    # Draw each string
    for string_idx in range(module.num_strings):
        voltages = cell_voltages[string_idx]
        y_offset = string_idx * string_spacing
        
        for cell_idx, V_cell in enumerate(voltages):
            # Position in grid
            row = cell_idx // cells_per_row
            col = cell_idx % cells_per_row
            
            x = col * cell_width
            y = y_offset - row * cell_height
            
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
        bypass_x = cells_per_row * cell_width + 0.5
        bypass_y = y_offset - cell_height
        
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
            x=bypass_x + 0.5,
            y=bypass_y,
            text=f"Bypass {string_idx+1}<br>{bypass_text}",
            showarrow=False,
            font=dict(size=10, color=bypass_color)
        )
        
        # String label
        fig.add_annotation(
            x=-0.5,
            y=y_offset - cell_height,
            text=f"String {string_idx+1}",
            showarrow=False,
            font=dict(size=12, color='black'),
            xanchor='right'
        )
    
    fig.update_layout(
        title=f"Modulschaltplan (I = {current:.2f} A)",
        showlegend=False,
        xaxis=dict(visible=False, range=[-1, cells_per_row*cell_width+2]),
        yaxis=dict(visible=False, scaleanchor="x", scaleratio=1),
        height=600,
        width=1000,
        plot_bgcolor='white'
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
    cell_height = 0.5
    string_spacing = 2.0
    cells_per_row = 12
    
    # Draw grid of cells
    cell_data = []
    
    for string_idx in range(module.num_strings):
        y_offset = string_idx * string_spacing
        
        for cell_idx in range(module.cells_per_string):
            row = cell_idx // cells_per_row
            col = cell_idx % cells_per_row
            
            x = col * cell_width
            y = y_offset - row * cell_height
            
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
        title="Verschattungsmuster Editor (Klicken zum Ändern)",
        showlegend=False,
        xaxis=dict(visible=False, range=[-1, cells_per_row*cell_width+1]),
        yaxis=dict(visible=False, scaleanchor="x", scaleratio=1),
        height=600,
        width=1000,
        plot_bgcolor='white',
        hovermode='closest'
    )
    
    return fig

