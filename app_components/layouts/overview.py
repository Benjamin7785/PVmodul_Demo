"""
Overview/landing page layout
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


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
                    dbc.CardHeader(html.H4("Modulkonfiguration")),
                    dbc.CardBody([
                        html.P([
                            html.Strong("Typisches Modul (dieser Simulation):"),
                            html.Br(),
                            "• 108 Halbzellen in Serie",
                            html.Br(),
                            "• 3 Substrings à 36 Halbzellen",
                            html.Br(),
                            "• 3 Bypass-Dioden (eine pro Substring)",
                            html.Br(),
                            "• Nennleistung: ~350-400 Wp (bei STC)"
                        ]),
                        html.Hr(),
                        html.H5("Wichtige Parameter:"),
                        html.Ul([
                            html.Li([html.Strong("I_sc"), ": Kurzschlussstrom ~10 A"]),
                            html.Li([html.Strong("V_oc"), ": Leerlaufspannung ~40-45 V"]),
                            html.Li([html.Strong("V_br"), ": Breakdown-Spannung ~12 V pro Zelle"]),
                            html.Li([html.Strong("V_f,BD"), ": Bypass-Durchlassspannung ~0.4 V"])
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

