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
                        html.Label("Verschattungsgrad (%):"),
                        html.Small([
                            "Wie stark sind die im Szenario definierten Zellen verschattet?",
                            html.Br(),
                            "0% = volle Sonne | 50% = halbe Bedeckung | 100% = vollständig verschattet"
                        ], className="text-muted d-block mb-2"),
                        dcc.Slider(
                            id='operating-current-slider',  # Keep ID for compatibility
                            min=0,
                            max=100,  # Verschattungsgrad in %
                            step=5,
                            value=100,  # Default: vollständige Verschattung
                            marks={
                                0: '0%',
                                25: '25%',
                                50: '50%',
                                75: '75%',
                                100: '100%'
                            },
                            tooltip={"placement": "bottom", "always_visible": True},
                            updatemode='drag'  # OPTIMIZED: Update während Drag (smoother)
                        ),
                        html.Div(id='shading-intensity-info', className="mt-2 alert alert-info", style={'fontSize': '0.85em', 'padding': '8px'}),
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
                ], className="mb-3"),
                
                dbc.Card([
                    dbc.CardHeader(html.H5("ℹ️ Verschattungsgrad-Steuerung")),
                    dbc.CardBody([
                        html.P([
                            html.Strong("Wie funktioniert es?"),
                            html.Br(),
                            "1. ", html.Strong("Szenario wählen"), ": Definiert WO verschattet wird",
                            html.Br(),
                            "2. ", html.Strong("Verschattungsgrad"), ": Definiert WIE STARK verschattet wird",
                        ]),
                        html.Hr(),
                        html.P([
                            html.Strong("Beispiel: "), "\"Einzelne verschattete Zelle\"",
                            html.Br(),
                            "• 0%: Zelle voll belichtet (keine Verschattung)",
                            html.Br(),
                            "• 50%: Zelle halb bedeckt (kleines Blatt)",
                            html.Br(),
                            "• 100%: Zelle komplett bedeckt (vollständiger Schatten)"
                        ]),
                        html.Hr(),
                        html.Small([
                            html.Strong("Betriebspunkt: "),
                            "Wird automatisch am MPP berechnet.",
                            html.Br(),
                            html.Strong("Farbcodierung: "),
                            "🟢 Normal | 🟠 Kritisch | 🔴 Bypass aktiv"
                        ], className="text-muted")
                    ])
                ], className="mb-3"),
                
                dbc.Card([
                    dbc.CardHeader(html.H5("ℹ️ String-Spannungen")),
                    dbc.CardBody([
                        html.P([
                            html.Strong("Farbcodierung:"),
                            html.Br(),
                            "🟢 ", html.Span("Normal", className="text-success"), " (V > 0)",
                            html.Br(),
                            "🟠 ", html.Span("Kritisch", className="text-warning"), " (-0,4V < V < 0)",
                            html.Br(),
                            "🔴 ", html.Span("Bypass aktiv", className="text-danger"), " (V < -0,4V)",
                        ], style={'fontSize': '0.9em'}),
                        html.Hr(),
                        html.Small([
                            html.Strong("Bypass-Schwelle: "),
                            "Die Bypass-Diode schaltet, wenn die ",
                            html.Strong("String-Spannung unter -0,4V"),
                            " fällt. Dies passiert, wenn verschattete Zellen in Reverse-Bias ",
                            "(negative Spannung) gehen."
                        ], className="text-muted")
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

