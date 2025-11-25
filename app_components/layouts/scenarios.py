"""
Scenarios comparison layout
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


def create_scenarios_layout():
    """
    Create scenarios comparison page
    
    Returns:
    --------
    dbc.Container
    """
    return dbc.Container([
        html.H2("Verschattungsszenarien Vergleich", className="text-center my-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Szenario Auswahl")),
                    dbc.CardBody([
                        html.Label("Szenario 1:"),
                        dcc.Dropdown(
                            id='scenario-1-dropdown',
                            options=[
                                {'label': 'Keine Verschattung', 'value': 'none'},
                                {'label': 'Einzelne Zelle', 'value': 'single_cell'},
                                {'label': 'Zwei Zellen', 'value': 'two_cells_same_string'},
                                {'label': 'Drei Zellen', 'value': 'three_cells_critical'},
                                {'label': 'Kaminschatten', 'value': 'chimney_shadow'},
                                {'label': 'Baumzweig', 'value': 'tree_branch'},
                                {'label': 'Teilweise Reihe', 'value': 'partial_row'},
                                {'label': 'Kompletter String', 'value': 'full_string'},
                                {'label': 'Stufenverschattung', 'value': 'gradient_shading'}
                            ],
                            value='none'
                        ),
                        html.Br(),
                        
                        html.Label("Szenario 2:"),
                        dcc.Dropdown(
                            id='scenario-2-dropdown',
                            options=[
                                {'label': 'Keine Verschattung', 'value': 'none'},
                                {'label': 'Einzelne Zelle', 'value': 'single_cell'},
                                {'label': 'Zwei Zellen', 'value': 'two_cells_same_string'},
                                {'label': 'Drei Zellen', 'value': 'three_cells_critical'},
                                {'label': 'Kaminschatten', 'value': 'chimney_shadow'},
                                {'label': 'Baumzweig', 'value': 'tree_branch'},
                                {'label': 'Teilweise Reihe', 'value': 'partial_row'},
                                {'label': 'Kompletter String', 'value': 'full_string'},
                                {'label': 'Stufenverschattung', 'value': 'gradient_shading'}
                            ],
                            value='single_cell'
                        ),
                        html.Br(),
                        
                        html.Label("Szenario 3 (optional):"),
                        dcc.Dropdown(
                            id='scenario-3-dropdown',
                            options=[
                                {'label': 'Nicht anzeigen', 'value': 'off'},
                                {'label': 'Keine Verschattung', 'value': 'none'},
                                {'label': 'Einzelne Zelle', 'value': 'single_cell'},
                                {'label': 'Zwei Zellen', 'value': 'two_cells_same_string'},
                                {'label': 'Drei Zellen', 'value': 'three_cells_critical'},
                                {'label': 'Kaminschatten', 'value': 'chimney_shadow'},
                                {'label': 'Baumzweig', 'value': 'tree_branch'},
                            ],
                            value='off'
                        ),
                        html.Hr(),
                        
                        dbc.Button("Vergleich aktualisieren", id="update-comparison-btn", color="primary", className="w-100")
                    ])
                ], className="mb-3")
            ], md=3),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("I-V Kennlinien Vergleich")),
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-scenario-iv-comparison",
                            type="default",
                            children=dcc.Graph(id='scenario-iv-comparison', style={'height': '500px'})
                        )
                    ])
                ], className="mb-3"),
                
                dbc.Card([
                    dbc.CardHeader(html.H4("Leistungsvergleich")),
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-scenario-power-comparison",
                            type="default",
                            children=dcc.Graph(id='scenario-power-comparison', style={'height': '400px'})
                        )
                    ])
                ])
            ], md=9)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Vergleichstabelle")),
                    dbc.CardBody([
                        html.Div(id='scenario-comparison-table')
                    ])
                ])
            ])
        ], className="mt-3"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Hot-Spot Vergleich")),
                    dbc.CardBody([
                        html.Div(id='scenario-hotspot-comparison')
                    ])
                ])
            ])
        ], className="mt-3"),
        
        dcc.Store(id='scenarios-comparison-store')
        
    ], fluid=True)

