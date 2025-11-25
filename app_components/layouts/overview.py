"""
Overview/landing page layout
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
from config import MODULE_STRUCTURE


def create_overview_layout():
    """
    Create overview page with introduction to the application
    
    Returns:
    --------
    dbc.Container
    """
    return dbc.Container([
        html.H1("PV-Modul Verschattungs-Visualisierung", className="text-center my-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H3("Willkommen")),
                    dbc.CardBody([
                        html.P([
                            "Diese interaktive Anwendung visualisiert das elektrische Verhalten von ",
                            "Photovoltaikmodulen unter Verschattung und erklärt die physikalischen Prinzipien ",
                            "hinter Spannungseinbrüchen und Reverse-Bias Breakthrough."
                        ]),
                        html.Hr(),
                        html.H5("Hauptfunktionen:"),
                        html.Ul([
                            html.Li("Interaktive I-V Kennlinien mit Parameterkontrolle"),
                            html.Li("Spannungsverteilung und Hot-Spot Analyse"),
                            html.Li("Bypass-Dioden Verhalten und Schwellwertanalyse"),
                            html.Li("3D Halbleiterphysik-Visualisierung (pn-Übergang, Avalanche-Effekt)"),
                            html.Li("Vordefinierte Verschattungsszenarien"),
                            html.Li("Vergleich verschiedener Betriebszustände")
                        ])
                    ])
                ], className="mb-4")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Theoretische Grundlagen")),
                    dbc.CardBody([
                        html.H5("Verschattungseffekte auf Solarzellen"),
                        html.P([
                            "Wenn eine Solarzelle verschattet wird, kann sie keinen Photostrom generieren. ",
                            "In einer Serienschaltung wird sie durch den Strom der anderen Zellen gezwungen, ",
                            "diesen Strom zu führen. Dies geschieht über Reverse-Bias (Sperrrichtung)."
                        ]),
                        
                        html.H5("Reverse-Bias Breakdown", className="mt-3"),
                        html.P([
                            "Bei hoher Reverse-Spannung (~10-20V) tritt Avalanche-Durchbruch auf. ",
                            "Elektronen gewinnen genug Energie, um durch Stoßionisation weitere ",
                            "Ladungsträger zu erzeugen (Lawinenmultiplikation). Dies führt zu:",
                        ]),
                        html.Ul([
                            html.Li("Stark erhöhter Stromfluss"),
                            html.Li("Lokaler Leistungsdissipation (Hot-Spot)"),
                            html.Li("Potentieller Zellschädigung")
                        ]),
                        
                        html.H5("Bypass-Dioden", className="mt-3"),
                        html.P([
                            "Bypass-Dioden (typisch Schottky) schützen Teilstrings. ",
                            "Sie leiten bei V_string < -0.4V und ermöglichen dem Strom, ",
                            "verschattete Bereiche zu umgehen."
                        ])
                    ])
                ], className="mb-4")
            ], md=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Modulkonfiguration", className="text-primary")),
                    dbc.CardBody([
                        html.Div([
                            html.H5(MODULE_STRUCTURE['module_name'], className="text-center text-success mb-3"),
                            html.P([
                                html.Strong(MODULE_STRUCTURE['technology']),
                                " - Hocheffizientes Bifazial Glass-Glass Modul"
                            ], className="text-center text-muted"),
                            html.P([
                                html.Small(f"Typ: {MODULE_STRUCTURE['module_type']}")
                            ], className="text-center text-muted"),
                        ]),
                        html.Hr(),
                        html.H6("Elektrische Daten (STC: 1000 W/m², 25°C, AM 1.5):"),
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.Strong("P_mpp:"),
                                    html.Span(f" {MODULE_STRUCTURE['module_specs_stc']['Pmpp']} W", className="text-primary")
                                ]),
                                html.Div([
                                    html.Strong("V_mpp:"),
                                    html.Span(f" {MODULE_STRUCTURE['module_specs_stc']['Vmpp']} V", className="text-primary")
                                ]),
                                html.Div([
                                    html.Strong("I_mpp:"),
                                    html.Span(f" {MODULE_STRUCTURE['module_specs_stc']['Impp']} A", className="text-primary")
                                ]),
                            ], md=6),
                            dbc.Col([
                                html.Div([
                                    html.Strong("V_oc:"),
                                    html.Span(f" {MODULE_STRUCTURE['module_specs_stc']['Voc']} V", className="text-info")
                                ]),
                                html.Div([
                                    html.Strong("I_sc:"),
                                    html.Span(f" {MODULE_STRUCTURE['module_specs_stc']['Isc']} A", className="text-info")
                                ]),
                                html.Div([
                                    html.Strong("η:"),
                                    html.Span(f" {MODULE_STRUCTURE['module_specs_stc']['efficiency']}%", className="text-success")
                                ]),
                            ], md=6)
                        ]),
                        html.Hr(),
                        html.H6("Besondere Merkmale:"),
                        html.Ul([
                            html.Li([
                                "Bifazialität: ",
                                html.Strong(f"{int(MODULE_STRUCTURE['bifacial']['bifaciality_factor']*100)}%"),
                                f" (bis zu +{MODULE_STRUCTURE['bifacial']['backside_gain_typical']}W Rückseitengewinn)"
                            ]),
                            html.Li([
                                "Temperaturkoeffizient: ",
                                html.Strong("-0.26%/K"),
                                " (besser als konventionelle Module)"
                            ]),
                        ]),
                        html.Hr(),
                        html.H6("Modulaufbau:"),
                        html.Ul([
                            html.Li(f"{MODULE_STRUCTURE['total_cells']} Halbzellen (6 × 18 Layout)"),
                            html.Li(f"{MODULE_STRUCTURE['num_strings']} Substrings à {MODULE_STRUCTURE['cells_per_string']} Zellen"),
                            html.Li(f"{MODULE_STRUCTURE['bypass_diodes']} Schottky-Bypass-Dioden"),
                            html.Li("V_f,BD ≈ 0,4 V (Bypass-Durchlassspannung)")
                        ])
                    ])
                ], className="mb-4")
            ], md=6)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.Hr(),
                html.H4("Navigation", className="text-center mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Button("I-V Kennlinien", href="/iv-curves", color="primary", className="w-100 mb-2")
                    ], md=3),
                    dbc.Col([
                        dbc.Button("Spannungsverteilung", href="/voltage-dist", color="primary", className="w-100 mb-2")
                    ], md=3),
                    dbc.Col([
                        dbc.Button("Bypass-Analyse", href="/bypass", color="primary", className="w-100 mb-2")
                    ], md=3),
                    dbc.Col([
                        dbc.Button("Halbleiterphysik", href="/physics", color="primary", className="w-100 mb-2")
                    ], md=3)
                ], justify="center")
            ])
        ]),
        
    ], fluid=True)

