"""
Voltage distribution and circuit visualization layout
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
from app_components.components.controls import create_parameter_controls, create_scenario_selector


def create_voltage_distribution_layout():
    """
    Create voltage distribution visualization page
    
    Returns:
    --------
    dbc.Container
    """
    return dbc.Container([
        html.H2("Spannungsverteilung & Hot-Spot Analyse", className="text-center my-4"),
        
        dbc.Row([
            # Controls
            dbc.Col([
                create_scenario_selector(),
                create_parameter_controls(),
                
                dbc.Card([
                    dbc.CardHeader(html.H5("Betriebspunkt")),
                    dbc.CardBody([
                        html.Label("Betriebsstrom (A):"),
                        dcc.Slider(
                            id='operating-current-slider',
                            min=0,
                            max=10,
                            step=0.1,
                            value=5.0,
                            marks={i: str(i) for i in range(0, 11, 2)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                        html.Hr(),
                        html.Div(id='operating-point-info')
                    ])
                ], className="mb-3"),
                
                dbc.Card([
                    dbc.CardHeader(html.H5("Anzeigeoptionen")),
                    dbc.CardBody([
                        dbc.Checklist(
                            id='voltage-display-options',
                            options=[
                                {'label': ' Spannungswerte anzeigen', 'value': 'show_values'},
                                {'label': ' Hot-Spots hervorheben', 'value': 'highlight_hotspots'},
                                {'label': ' Bypass-Status', 'value': 'show_bypass'}
                            ],
                            value=['show_values', 'highlight_hotspots', 'show_bypass'],
                            inline=False
                        )
                    ])
                ])
            ], md=3),
            
            # Visualizations
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Schaltplan mit Spannungsverteilung")),
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-circuit",
                            type="default",
                            children=dcc.Graph(id='circuit-diagram', style={'height': '600px'})
                        )
                    ])
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Spannungs-Heatmap")),
                            dbc.CardBody([
                                dcc.Loading(
                                    id="loading-voltage-heatmap",
                                    type="default",
                                    children=dcc.Graph(id='voltage-heatmap')
                                )
                            ])
                        ])
                    ], md=6),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Leistungsdissipation")),
                            dbc.CardBody([
                                dcc.Loading(
                                    id="loading-power-heatmap",
                                    type="default",
                                    children=dcc.Graph(id='power-dissipation-heatmap')
                                )
                            ])
                        ])
                    ], md=6)
                ], className="mb-3"),
                
                dbc.Card([
                    dbc.CardHeader(html.H5("Hot-Spot Details")),
                    dbc.CardBody([
                        html.Div(id='hotspot-details')
                    ])
                ])
            ], md=9)
        ]),
        
        dcc.Store(id='voltage-data-store')
        
    ], fluid=True)

