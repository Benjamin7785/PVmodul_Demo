"""
Reusable control components for the Dash app
"""

import dash_bootstrap_components as dbc
from dash import dcc, html


def create_parameter_controls():
    """
    Create control panel for basic parameters
    
    Returns:
    --------
    dbc.Card
        Card containing parameter controls
    """
    return dbc.Card([
        dbc.CardHeader(html.H4("Parameter")),
        dbc.CardBody([
            # Irradiance
            html.Label("Einstrahlung (W/m²):"),
            dcc.Slider(
                id='irradiance-slider',
                min=200,
                max=1000,
                step=50,
                value=1000,
                marks={i: str(i) for i in range(200, 1001, 200)},
                tooltip={"placement": "bottom", "always_visible": True},
                updatemode='mouseup'  # OPTIMIZED: Update nur beim Loslassen
            ),
            html.Br(),
            
            # Temperature (erweitert: -20°C bis +90°C für Winter/Sommer)
            html.Label("Temperatur (°C):"),
            html.Small("Winter bis Sommer: -20°C bis +90°C", className="text-muted d-block mb-1"),
            dcc.Slider(
                id='temperature-slider',
                min=-20,
                max=90,
                step=5,
                value=25,
                marks={
                    -20: '-20°',
                    0: '0°',
                    25: '25° (STC)',
                    45: '45° (NOCT)',
                    70: '70°',
                    90: '90°'
                },
                tooltip={"placement": "bottom", "always_visible": True},
                updatemode='mouseup'  # OPTIMIZED: Update nur beim Loslassen
            ),
            html.Br(),
            html.Hr(),
            html.Small([
                "ℹ️ ", 
                html.Strong("Physikalische Kopplung:"), 
                " Der maximale Strom wird automatisch aus der Einstrahlung berechnet: ",
                html.Code("I_max = (G/1000) × I_sc")
            ], className="text-info"),
        ])
    ], className="mb-3")


def create_shading_controls():
    """
    Create controls for shading configuration
    
    Returns:
    --------
    dbc.Card
        Card containing shading controls
    """
    return dbc.Card([
        dbc.CardHeader(html.H4("Verschattung")),
        dbc.CardBody([
            html.Label("Anzahl verschatteter Zellen (String 1):"),
            dcc.Slider(
                id='num-shaded-cells-s1',
                min=0,
                max=10,
                step=1,
                value=0,
                marks={i: str(i) for i in range(0, 11, 2)},
                tooltip={"placement": "bottom", "always_visible": True},
                updatemode='mouseup'  # OPTIMIZED: Update nur beim Loslassen
            ),
            html.Br(),
            
            html.Label("Anzahl verschatteter Zellen (String 2):"),
            dcc.Slider(
                id='num-shaded-cells-s2',
                min=0,
                max=10,
                step=1,
                value=0,
                marks={i: str(i) for i in range(0, 11, 2)},
                tooltip={"placement": "bottom", "always_visible": True},
                updatemode='mouseup'  # OPTIMIZED: Update nur beim Loslassen
            ),
            html.Br(),
            
            html.Label("Anzahl verschatteter Zellen (String 3):"),
            dcc.Slider(
                id='num-shaded-cells-s3',
                min=0,
                max=10,
                step=1,
                value=0,
                marks={i: str(i) for i in range(0, 11, 2)},
                tooltip={"placement": "bottom", "always_visible": True},
                updatemode='mouseup'  # OPTIMIZED: Update nur beim Loslassen
            ),
            html.Br(),
            
            html.Label("Verschattungsintensität:"),
            dcc.Slider(
                id='shading-intensity',
                min=0,
                max=1,
                step=0.1,
                value=1.0,
                marks={i/10: f"{i*10}%" for i in range(0, 11, 2)},
                tooltip={"placement": "bottom", "always_visible": True},
                updatemode='mouseup'  # OPTIMIZED: Update nur beim Loslassen
            ),
            html.Br(),
            
            dbc.Button("Verschattung zurücksetzen", id="reset-shading-btn", color="secondary", className="mt-2")
        ])
    ], className="mb-3")


def create_scenario_selector():
    """
    Create dropdown for predefined scenarios
    
    Returns:
    --------
    dbc.Card
        Card containing scenario selector
    """
    return dbc.Card([
        dbc.CardHeader(html.H4("Vordefinierte Szenarien")),
        dbc.CardBody([
            html.Label("Szenario auswählen:"),
            dcc.Dropdown(
                id='scenario-dropdown',
                options=[
                    {'label': 'Keine Verschattung', 'value': 'none'},
                    {'label': 'Einzelne Zelle', 'value': 'single_cell'},
                    {'label': 'Zwei Zellen (selber String)', 'value': 'two_cells_same_string'},
                    {'label': 'Kritische Verschattung (3 Zellen)', 'value': 'three_cells_critical'},
                    {'label': 'Kaminschatten', 'value': 'chimney_shadow'},
                    {'label': 'Baumzweig', 'value': 'tree_branch'},
                    {'label': 'Teilweise Zellreihe', 'value': 'partial_row'},
                    {'label': 'Kompletter String', 'value': 'full_string'},
                    {'label': 'Stufenverschattung', 'value': 'gradient_shading'}
                ],
                value='none',
                clearable=False
            ),
            html.Br(),
            html.Div(id='scenario-description', className="text-muted")
        ])
    ], className="mb-3")


def create_physics_controls():
    """
    Create controls for semiconductor physics visualization
    
    Returns:
    --------
    dbc.Card
        Card containing physics controls
    """
    return dbc.Card([
        dbc.CardHeader(html.H4("Halbleiterphysik Parameter")),
        dbc.CardBody([
            html.Label("Reverse-Bias Spannung (V):"),
            dcc.Slider(
                id='reverse-voltage-slider',
                min=-20,
                max=0,
                step=0.5,
                value=-12,
                marks={i: str(i) for i in range(-20, 1, 5)},
                tooltip={"placement": "bottom", "always_visible": True},
                updatemode='mouseup'  # OPTIMIZED: Update nur beim Loslassen
            ),
            html.Br(),
            
            html.Label("Temperatur (°C):"),
            html.Small("Einfluss auf Breakdown-Spannung", className="text-muted d-block mb-1"),
            dcc.Slider(
                id='temperature-slider',
                min=-20,
                max=90,
                step=5,
                value=25,
                marks={
                    -20: '-20°',
                    0: '0°',
                    25: '25° (STC)',
                    45: '45° (NOCT)',
                    70: '70°',
                    90: '90°'
                },
                tooltip={"placement": "bottom", "always_visible": True},
                updatemode='mouseup'  # OPTIMIZED: Update nur beim Loslassen
            ),
            html.Br(),
            
            html.Label("Dotierungskonzentration (log10 cm⁻³):"),
            dcc.Slider(
                id='doping-slider',
                min=15,
                max=19,
                step=0.5,
                value=16,
                marks={i: f"10^{i}" for i in range(15, 20)},
                tooltip={"placement": "bottom", "always_visible": True},
                updatemode='mouseup'  # OPTIMIZED: Update nur beim Loslassen
            ),
            html.Br(),
            
            dbc.Checklist(
                id='physics-display-options',
                options=[
                    {'label': ' E-Feld anzeigen', 'value': 'show_efield'},
                    {'label': ' Bänderdiagramm anzeigen', 'value': 'show_bands'},
                    {'label': ' Avalanche Animation', 'value': 'show_avalanche'}
                ],
                value=['show_efield'],
                inline=True
            )
        ])
    ], className="mb-3")


def create_info_card(title, content):
    """
    Create information card
    
    Parameters:
    -----------
    title : str
        Card title
    content : str or dash component
        Card content
        
    Returns:
    --------
    dbc.Card
    """
    return dbc.Card([
        dbc.CardHeader(html.H5(title)),
        dbc.CardBody(content)
    ], className="mb-3")

