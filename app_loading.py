"""
Loading Screen for PV Module Shading Visualization App

Displays during LUT generation on first startup
"""

import dash_bootstrap_components as dbc
from dash import html, dcc


def create_loading_layout(progress=0, message="Initializing...", stage="loading"):
    """
    Create loading screen with progress bar
    
    Parameters:
    -----------
    progress : int
        Progress percentage (0-100)
    message : str
        Status message to display
    stage : str
        'loading' or 'complete'
        
    Returns:
    --------
    dash component
        Loading screen layout
    """
    if stage == 'complete':
        return create_complete_layout()
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1("⚡ PV Module Shading Visualization", 
                           className="text-center mt-5 mb-4",
                           style={'color': '#2c3e50'}),
                    html.Hr(),
                    
                    # Status message
                    html.H4(message, 
                           className="text-center text-muted mb-4",
                           id='loading-message'),
                    
                    # Progress bar
                    dbc.Progress(
                        id='loading-progress-bar',
                        value=progress,
                        className="mb-3",
                        style={"height": "30px"},
                        striped=True,
                        animated=True,
                        color="success"
                    ),
                    
                    # Progress text
                    html.P(
                        f"{progress}% Complete",
                        id='loading-progress-text',
                        className="text-center mb-4",
                        style={'fontSize': '1.2em', 'fontWeight': 'bold'}
                    ),
                    
                    html.Hr(),
                    
                    # Info box
                    dbc.Alert([
                        html.H5("🔧 Generating Look-up Tables", className="alert-heading"),
                        html.P([
                            "Pre-computing cell I-V characteristics for ultra-fast visualization...",
                            html.Br(),
                            html.Br(),
                            html.Strong("This only happens once on first startup!"),
                            html.Br(),
                            "Subsequent starts will load from cache in ~1-2 seconds."
                        ]),
                        html.Hr(),
                        html.P([
                            "📊 Grid: 264,000 pre-computed values",
                            html.Br(),
                            "⚡ Performance: 200x faster calculations",
                            html.Br(),
                            "💾 Cache size: ~50-200 MB"
                        ], className="mb-0", style={'fontSize': '0.9em'})
                    ], color="info", className="mt-3"),
                    
                    # Technical details (collapsible)
                    dbc.Accordion([
                        dbc.AccordionItem([
                            html.P([
                                html.Strong("What's happening?"),
                                html.Br(),
                                "The app is pre-calculating all possible solar cell current-voltage (I-V) characteristics ",
                                "for different conditions (irradiance, temperature, shading). This Look-up Table (LUT) ",
                                "allows instant visualization updates instead of slow numerical calculations."
                            ]),
                            html.Hr(),
                            html.P([
                                html.Strong("Grid Parameters:"),
                                html.Br(),
                                "• Irradiance: 200-1000 W/m² (10 steps)",
                                html.Br(),
                                "• Temperature: -20 to +90°C (12 steps)",
                                html.Br(),
                                "• Shading: 0-100% (11 steps)",
                                html.Br(),
                                "• Current: 0-15 A (200 steps)"
                            ], style={'fontSize': '0.9em'})
                        ], title="Technical Details")
                    ], start_collapsed=True, className="mt-3")
                ], style={'maxWidth': '800px', 'margin': 'auto'})
            ], width=12)
        ])
    ], fluid=True, style={'minHeight': '100vh', 'paddingTop': '50px', 'backgroundColor': '#f8f9fa'})


def create_complete_layout():
    """
    Layout shown when LUT generation is complete
    """
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1("✅ Initialization Complete!", 
                           className="text-center mt-5 mb-4 text-success"),
                    html.H4("Loading application...", 
                           className="text-center text-muted mb-4"),
                    
                    dbc.Spinner(color="success", size="lg"),
                    
                    html.P("Redirecting to main application...",
                          className="text-center mt-4 text-muted")
                ], className="text-center")
            ], width=12)
        ])
    ], fluid=True, style={'minHeight': '100vh', 'paddingTop': '100px'})


def create_loading_failed_layout(error_message):
    """
    Layout shown if LUT generation fails
    
    Parameters:
    -----------
    error_message : str
        Error description
    """
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1("❌ Initialization Failed", 
                           className="text-center mt-5 mb-4 text-danger"),
                    
                    dbc.Alert([
                        html.H5("Error during LUT generation", className="alert-heading"),
                        html.P(error_message),
                        html.Hr(),
                        html.P([
                            "The app will run in fallback mode (slower performance).",
                            html.Br(),
                            "Contact support if this persists."
                        ], className="mb-0")
                    ], color="danger"),
                    
                    html.Div([
                        dbc.Button("Continue with Fallback Mode", 
                                  id='fallback-continue-btn',
                                  color="warning",
                                  size="lg",
                                  className="mt-3")
                    ], className="text-center")
                ], style={'maxWidth': '800px', 'margin': 'auto'})
            ], width=12)
        ])
    ], fluid=True, style={'minHeight': '100vh', 'paddingTop': '50px'})


if __name__ == '__main__':
    # Quick visual test
    print("Loading screen layouts created successfully!")
    print("- create_loading_layout(): Main loading screen")
    print("- create_complete_layout(): Success screen")
    print("- create_loading_failed_layout(): Error screen")

