"""
I-V Curves page layout
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
from app_components.components.controls import create_parameter_controls, create_scenario_selector


def create_iv_curves_layout():
    """
    Create I-V curves visualization page
    
    Returns:
    --------
    dbc.Container
    """
    return dbc.Container([
        html.H2("I-V Kennlinien Analyse", className="text-center my-4"),
        
        dbc.Row([
            # Controls column
            dbc.Col([
                create_scenario_selector(),
                create_parameter_controls(),
                
                dbc.Card([
                    dbc.CardHeader(html.H5("MPP Information")),
                    dbc.CardBody([
                        html.Div(id='mpp-info-display')
                    ])
                ], className="mb-3"),
                
                dbc.Card([
                    dbc.CardHeader(html.H5("Optionen")),
                    dbc.CardBody([
                        dbc.Checklist(
                            id='iv-display-options',
                            options=[
                                {'label': ' Leistungskurve anzeigen', 'value': 'show_power'},
                                {'label': ' Referenz (unverschattet)', 'value': 'show_reference'},
                                {'label': ' MPP markieren', 'value': 'show_mpp'}
                            ],
                            value=['show_power', 'show_mpp'],
                            inline=False
                        )
                    ])
                ])
            ], md=3),
            
            # Visualization column
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Modul I-V Kennlinie")),
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-iv-curve",
                            type="default",
                            children=dcc.Graph(id='module-iv-curve')
                        )
                    ])
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Leistungskurve")),
                            dbc.CardBody([
                                dcc.Loading(
                                    id="loading-power-curve",
                                    type="default",
                                    children=dcc.Graph(id='power-curve')
                                )
                            ])
                        ])
                    ], md=6),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(html.H5("Verlustanalyse")),
                            dbc.CardBody([
                                html.Div(id='loss-analysis')
                            ])
                        ])
                    ], md=6)
                ])
            ], md=9)
        ]),
        
        # Store for data
        dcc.Store(id='module-data-store')
        
    ], fluid=True)

