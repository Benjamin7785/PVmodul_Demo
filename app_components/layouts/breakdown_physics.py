"""
Semiconductor physics and breakdown visualization layout
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
from app_components.components.controls import create_physics_controls


def create_breakdown_physics_layout():
    """
    Create semiconductor physics visualization page
    
    Returns:
    --------
    dbc.Container
    """
    return dbc.Container([
        html.H2("Halbleiterphysik: Reverse-Bias Breakdown", className="text-center my-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Physikalische Grundlagen"),
                        html.P([
                            "Unter Reverse-Bias wird die Sperrschicht breiter und das elektrische ",
                            "Feld stärker. Bei hohen Spannungen tritt Avalanche-Durchbruch auf."
                        ]),
                        html.Hr(),
                        html.H6("Avalanche-Mechanismus:"),
                        html.Ol([
                            html.Li("Elektronen gewinnen Energie im E-Feld"),
                            html.Li("Stoßionisation erzeugt Elektron-Loch-Paare"),
                            html.Li("Lawinenartiger Anstieg der Ladungsträger"),
                            html.Li("Stark erhöhter Strom (M >> 1)")
                        ])
                    ])
                ], className="mb-3")
            ], md=12)
        ]),
        
        dbc.Row([
            # Controls
            dbc.Col([
                create_physics_controls(),
                
                dbc.Card([
                    dbc.CardHeader(html.H5("Berechnete Werte")),
                    dbc.CardBody([
                        html.Div(id='physics-calculated-values')
                    ])
                ], className="mb-3"),
                
                dbc.Card([
                    dbc.CardHeader(html.H5("Erklärungen")),
                    dbc.CardBody([
                        html.Small([
                            html.Strong("Sperrschichtweite (W): "),
                            "Breite der ladungsträgerfreien Zone",
                            html.Br(),
                            html.Strong("E-Feld (E_max): "),
                            "Maximale elektrische Feldstärke",
                            html.Br(),
                            html.Strong("Multiplikationsfaktor (M): "),
                            "Lawinenverstärkung (M >> 1 bei Breakdown)"
                        ])
                    ])
                ])
            ], md=3),
            
            # Visualizations
            dbc.Col([
                dbc.Tabs([
                    dbc.Tab(label="E-Feld Profil", tab_id="tab-efield"),
                    dbc.Tab(label="Bänderdiagramm", tab_id="tab-bands"),
                    dbc.Tab(label="3D pn-Übergang", tab_id="tab-pn-3d"),
                    dbc.Tab(label="Avalanche Animation", tab_id="tab-avalanche"),
                ], id="physics-tabs", active_tab="tab-efield"),
                
                html.Div(id='physics-tab-content', className="mt-3")
            ], md=9)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Zusätzliche Analysen")),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H6("Sperrschichtweite vs. Spannung"),
                                dcc.Loading(
                                    id="loading-depletion-width",
                                    type="default",
                                    children=dcc.Graph(id='depletion-width-chart')
                                )
                            ], md=6),
                            
                            dbc.Col([
                                html.H6("Temperaturabhängigkeit"),
                                dcc.Loading(
                                    id="loading-temp-dependence",
                                    type="default",
                                    children=dcc.Graph(id='temperature-dependence-chart')
                                )
                            ], md=6)
                        ])
                    ])
                ])
            ])
        ], className="mt-3"),
        
        dcc.Store(id='physics-data-store')
        
    ], fluid=True)


