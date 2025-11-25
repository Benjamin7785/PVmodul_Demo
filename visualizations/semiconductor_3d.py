"""
3D visualizations for semiconductor physics
"""

import plotly.graph_objects as go
import numpy as np


def plot_pn_junction_3d(physics, V_applied=0, show_depletion=True):
    """
    Create 3D visualization of pn-junction structure
    
    Parameters:
    -----------
    physics : SemiconductorPhysics
        Physics object
    V_applied : float
        Applied voltage
    show_depletion : bool
        Whether to highlight depletion region
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    depl = physics.depletion_width(V_applied)
    
    fig = go.Figure()
    
    # Create 3D blocks for p and n regions
    # Dimensions in μm
    width = 5  # μm
    height = 5  # μm
    
    # P-region (left side)
    p_length = depl['xp'] + 2  # Extend beyond depletion
    p_vertices = np.array([
        [-p_length, -width/2, -height/2],
        [-p_length, width/2, -height/2],
        [-p_length, width/2, height/2],
        [-p_length, -width/2, height/2],
        [0, -width/2, -height/2],
        [0, width/2, -height/2],
        [0, width/2, height/2],
        [0, -width/2, height/2],
    ])
    
    # N-region (right side)
    n_length = depl['xn'] + 2
    n_vertices = np.array([
        [0, -width/2, -height/2],
        [0, width/2, -height/2],
        [0, width/2, height/2],
        [0, -width/2, height/2],
        [n_length, -width/2, -height/2],
        [n_length, width/2, -height/2],
        [n_length, width/2, height/2],
        [n_length, -width/2, height/2],
    ])
    
    # Define faces (each face is a set of 4 vertices)
    faces = [
        [0, 1, 2, 3],  # back
        [4, 5, 6, 7],  # front
        [0, 1, 5, 4],  # bottom
        [2, 3, 7, 6],  # top
        [0, 3, 7, 4],  # left
        [1, 2, 6, 5],  # right
    ]
    
    # Create mesh for p-region
    i_p, j_p, k_p = [], [], []
    for face in faces:
        i_p.extend([face[0], face[0]])
        j_p.extend([face[1], face[2]])
        k_p.extend([face[2], face[3]])
    
    fig.add_trace(go.Mesh3d(
        x=p_vertices[:, 0],
        y=p_vertices[:, 1],
        z=p_vertices[:, 2],
        i=i_p, j=j_p, k=k_p,
        color='lightblue',
        opacity=0.5,
        name='p-Region',
        showlegend=True
    ))
    
    # Create mesh for n-region
    i_n, j_n, k_n = [], [], []
    for face in faces:
        i_n.extend([face[0], face[0]])
        j_n.extend([face[1], face[2]])
        k_n.extend([face[2], face[3]])
    
    fig.add_trace(go.Mesh3d(
        x=n_vertices[:, 0],
        y=n_vertices[:, 1],
        z=n_vertices[:, 2],
        i=i_n, j=j_n, k=k_n,
        color='lightcoral',
        opacity=0.5,
        name='n-Region',
        showlegend=True
    ))
    
    # Highlight depletion region
    if show_depletion:
        depl_vertices = np.array([
            [-depl['xp'], -width/2, -height/2],
            [-depl['xp'], width/2, -height/2],
            [-depl['xp'], width/2, height/2],
            [-depl['xp'], -width/2, height/2],
            [depl['xn'], -width/2, -height/2],
            [depl['xn'], width/2, -height/2],
            [depl['xn'], width/2, height/2],
            [depl['xn'], -width/2, height/2],
        ])
        
        fig.add_trace(go.Mesh3d(
            x=depl_vertices[:, 0],
            y=depl_vertices[:, 1],
            z=depl_vertices[:, 2],
            i=i_p, j=j_p, k=k_p,
            color='yellow',
            opacity=0.3,
            name='Sperrschicht',
            showlegend=True
        ))
    
    fig.update_layout(
        title=f"pn-Übergang (V = {V_applied:.1f} V)",
        scene=dict(
            xaxis_title="Position (μm)",
            yaxis_title="y (μm)",
            zaxis_title="z (μm)",
            aspectmode='data'
        ),
        height=600
    )
    
    return fig


def plot_avalanche_animation(physics, V_applied=-15, num_frames=30):
    """
    Create animated visualization of avalanche breakdown
    
    Parameters:
    -----------
    physics : SemiconductorPhysics
        Physics object
    V_applied : float
        Applied reverse voltage
    num_frames : int
        Number of animation frames
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    particles_data = physics.generate_avalanche_particles(V_applied, num_particles=50)
    
    # Create frames showing carrier multiplication
    frames = []
    
    for frame_idx in range(num_frames):
        # Exponentially increase number of particles (avalanche effect)
        num_particles = int(50 * (1 + frame_idx * 0.3))
        particles = physics.generate_avalanche_particles(V_applied, num_particles)
        
        # Separate electrons and holes
        electron_mask = np.array([t == 'electron' for t in particles['types']])
        
        frame = go.Frame(
            data=[
                go.Scatter3d(
                    x=particles['x'][electron_mask],
                    y=particles['y'][electron_mask],
                    z=particles['z'][electron_mask],
                    mode='markers',
                    marker=dict(size=4, color='blue'),
                    name='Elektronen'
                ),
                go.Scatter3d(
                    x=particles['x'][~electron_mask],
                    y=particles['y'][~electron_mask],
                    z=particles['z'][~electron_mask],
                    mode='markers',
                    marker=dict(size=4, color='red'),
                    name='Löcher'
                )
            ],
            name=str(frame_idx)
        )
        frames.append(frame)
    
    # Initial frame
    electron_mask = np.array([t == 'electron' for t in particles_data['types']])
    
    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=particles_data['x'][electron_mask],
                y=particles_data['y'][electron_mask],
                z=particles_data['z'][electron_mask],
                mode='markers',
                marker=dict(size=4, color='blue'),
                name='Elektronen'
            ),
            go.Scatter3d(
                x=particles_data['x'][~electron_mask],
                y=particles_data['y'][~electron_mask],
                z=particles_data['z'][~electron_mask],
                mode='markers',
                marker=dict(size=4, color='red'),
                name='Löcher'
            )
        ],
        frames=frames
    )
    
    # Add animation controls
    fig.update_layout(
        title=f"Lawinendurchbruch (V = {V_applied:.1f} V, M = {particles_data['multiplication_factor']:.1f})",
        scene=dict(
            xaxis_title="Position (μm)",
            yaxis_title="y (μm)",
            zaxis_title="z (μm)",
            aspectmode='cube'
        ),
        updatemenus=[{
            'type': 'buttons',
            'showactive': False,
            'buttons': [
                {'label': 'Play', 'method': 'animate', 'args': [None, {'frame': {'duration': 100}}]},
                {'label': 'Pause', 'method': 'animate', 'args': [[None], {'frame': {'duration': 0}, 'mode': 'immediate'}]}
            ]
        }],
        height=600
    )
    
    return fig


def plot_electric_field_3d(physics, V_applied=0):
    """
    Create 3D surface plot of electric field distribution
    
    Parameters:
    -----------
    physics : SemiconductorPhysics
        Physics object
    V_applied : float
        Applied voltage
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    E_profile = physics.electric_field_profile(V_applied, points=100)
    
    # Create 2D grid for surface plot
    x = E_profile['x']
    y = np.linspace(-2, 2, 50)  # Perpendicular direction
    X, Y = np.meshgrid(x, y)
    
    # E-field only varies with x
    Z = np.tile(E_profile['E'], (len(y), 1))
    
    fig = go.Figure(data=[
        go.Surface(
            x=X, y=Y, z=Z,
            colorscale='Reds',
            colorbar=dict(title="E-Feld (V/cm)"),
            name='E-Feld'
        )
    ])
    
    fig.update_layout(
        title=f"Elektrische Feldverteilung (V = {V_applied:.1f} V)",
        scene=dict(
            xaxis_title="Position (μm)",
            yaxis_title="y (μm)",
            zaxis_title="E-Feld (V/cm)"
        ),
        height=600
    )
    
    return fig


def plot_band_diagram(physics, V_applied=0):
    """
    Plot energy band diagram
    
    Parameters:
    -----------
    physics : SemiconductorPhysics
        Physics object
    V_applied : float
        Applied voltage
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    band_data = physics.band_diagram(V_applied, points=200)
    
    fig = go.Figure()
    
    # Conduction band
    fig.add_trace(go.Scatter(
        x=band_data['x'],
        y=band_data['Ec'],
        name='Leitungsband (Ec)',
        line=dict(color='blue', width=2),
        mode='lines'
    ))
    
    # Valence band
    fig.add_trace(go.Scatter(
        x=band_data['x'],
        y=band_data['Ev'],
        name='Valenzband (Ev)',
        line=dict(color='red', width=2),
        mode='lines',
        fill='tonexty',
        fillcolor='rgba(200, 200, 200, 0.3)'
    ))
    
    # Fermi level
    fig.add_trace(go.Scatter(
        x=band_data['x'],
        y=band_data['Ef'],
        name='Fermi-Niveau (Ef)',
        line=dict(color='green', width=2, dash='dash'),
        mode='lines'
    ))
    
    # Mark junction at x=0
    fig.add_vline(x=0, line_dash="dot", line_color="black", annotation_text="Übergang")
    
    fig.update_layout(
        title=f"Bänderdiagramm (V = {V_applied:.1f} V)",
        xaxis_title="Position (μm)",
        yaxis_title="Energie (eV)",
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig


def plot_depletion_width_vs_voltage(physics, V_range=None):
    """
    Plot how depletion width changes with voltage
    
    Parameters:
    -----------
    physics : SemiconductorPhysics
        Physics object
    V_range : tuple or None
        (V_min, V_max) voltage range
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    if V_range is None:
        V_range = (-20, 1)
    
    voltages = np.linspace(V_range[0], V_range[1], 100)
    widths = []
    
    for V in voltages:
        depl = physics.depletion_width(V)
        widths.append(depl['W_total'])
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=voltages,
        y=widths,
        mode='lines',
        line=dict(color='purple', width=2),
        name='Sperrschichtweite'
    ))
    
    fig.update_layout(
        title="Sperrschichtweite vs. Spannung",
        xaxis_title="Spannung (V)",
        yaxis_title="Sperrschichtweite (μm)",
        template='plotly_white',
        height=400
    )
    
    return fig

