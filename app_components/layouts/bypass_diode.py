"""
Bypass diode behavior analysis layout
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
from app_components.components.controls import create_scenario_selector, create_parameter_controls


def create_bypass_diode_layout():
    """
    Create bypass diode analysis page
    
    Returns:
    --------
    dbc.Container
    """
    return dbc.Container([
        html.H2("Bypass-Dioden Analyse", className="text-center my-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Bypass-Diode Funktion"),
                        html.P([
                            "Bypass-Dioden schützen Teilstrings vor Überlastung. ",
                            "Sie leiten, wenn die Teilstring-Spannung negativ wird ",
                            "(typisch < -0.4 V für Schottky-Dioden)."
                        ]),
                        html.Hr(),
                        html.H6("Aktivierungsbedingung:"),
                        html.P([
                            "V_substring < -V_f (≈ -0.4 V)",
                            html.Br(),
                            "Dies tritt auf bei starker Verschattung mehrerer Zellen."
                        ])
                    ])
                ], className="mb-3")
            ], md=12)
        ]),
        
        dbc.Row([
            # Controls
            dbc.Col([
                create_scenario_selector(),
                
                dbc.Card([
                    dbc.CardHeader(html.H5("Test-Parameter")),
                    dbc.CardBody([
                        html.Label("Anzahl verschatteter Zellen (String 1):"),
                        dcc.Slider(
                            id='bypass-test-num-cells',
                            min=0,
                            max=15,
                            step=1,
                            value=2,
                            marks={i: str(i) for i in range(0, 16, 3)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                        html.Br(),
                        
                        html.Label("Verschattungsintensität:"),
                        dcc.Slider(
                            id='bypass-test-intensity',
                            min=0,
                            max=1,
                            step=0.1,
                            value=1.0,
                            marks={i/10: f"{i*10}%" for i in range(0, 11, 2)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                        html.Br(),
                        
                        html.Label("Betriebsstrom (A):"),
                        dcc.Slider(
                            id='bypass-test-current',
                            min=0,
                            max=10,
                            step=0.5,
                            value=5.0,
                            marks={i: str(i) for i in range(0, 11, 2)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ])
                ], className="mb-3"),
                
                dbc.Card([
                    dbc.CardHeader(html.H5("Bypass Status")),
                    dbc.CardBody([
                        html.Div(id='bypass-status-display')
                    ])
                ])
            ], md=3),
            
            # Visualizations
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("String-Spannungen")),
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-string-voltages",
                            type="default",
                            children=dcc.Graph(id='string-voltage-chart')
                        )
                    ])
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Aktivierungsschwelle")),
                            dbc.CardBody([
                                dcc.Loading(
                                    id="loading-threshold-chart",
                                    type="default",
                                    children=dcc.Graph(id='bypass-threshold-chart')
                                )
                            ])
                        ])
                    ], md=6),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Zellanzahl vs. Bypass")),
                            dbc.CardBody([
                                html.Div(id='bypass-cell-count-analysis')
                            ])
                        ])
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Card([
                    dbc.CardHeader(html.H4("Szenario Vergleich")),
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-bypass-comparison",
                            type="default",
                            children=dcc.Graph(id='bypass-scenario-comparison')
                        )
                    ])
                ])
            ], md=9)
        ]),
        
        dcc.Store(id='bypass-data-store')
        
    ], fluid=True)

