"""
Main Dash application for PV Module Shading Visualization
"""

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback
import plotly.graph_objects as go
import numpy as np

# Import physics models
from physics import PVModule, SolarCell, SemiconductorPhysics

# Import visualization functions
from visualizations.iv_plotter import plot_iv_curve, plot_iv_comparison, plot_power_curve, plot_cell_iv_with_breakdown
from visualizations.circuit_visualizer import create_module_circuit_diagram
from visualizations.heatmap_generator import (
    create_power_dissipation_heatmap, create_voltage_heatmap, 
    create_temperature_distribution_3d, create_shading_pattern_heatmap
)
from visualizations.semiconductor_3d import (
    plot_pn_junction_3d, plot_avalanche_animation, plot_electric_field_3d,
    plot_band_diagram, plot_depletion_width_vs_voltage
)

# Import layouts
from app_components.layouts.overview import create_overview_layout
from app_components.layouts.iv_curves import create_iv_curves_layout
from app_components.layouts.voltage_distribution import create_voltage_distribution_layout
from app_components.layouts.bypass_diode import create_bypass_diode_layout
from app_components.layouts.breakdown_physics import create_breakdown_physics_layout
from app_components.layouts.scenarios import create_scenarios_layout

# Import utilities
from utils import (
    get_scenario_by_id, convert_scenario_to_shading_config,
    create_shading_config_from_counts, format_power, format_voltage, format_current
)

from config import APP_CONFIG

# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title=APP_CONFIG['title']
)

# Navigation bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Übersicht", href="/")),
        dbc.NavItem(dbc.NavLink("I-V Kennlinien", href="/iv-curves")),
        dbc.NavItem(dbc.NavLink("Spannungsverteilung", href="/voltage-dist")),
        dbc.NavItem(dbc.NavLink("Bypass-Analyse", href="/bypass")),
        dbc.NavItem(dbc.NavLink("Halbleiterphysik", href="/physics")),
        dbc.NavItem(dbc.NavLink("Szenarien", href="/scenarios")),
    ],
    brand="PV Modul Verschattung",
    brand_href="/",
    color="primary",
    dark=True,
    className="mb-3"
)

# App layout with routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])


# Routing callback
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    """Route to appropriate page"""
    if pathname == '/iv-curves':
        return create_iv_curves_layout()
    elif pathname == '/voltage-dist':
        return create_voltage_distribution_layout()
    elif pathname == '/bypass':
        return create_bypass_diode_layout()
    elif pathname == '/physics':
        return create_breakdown_physics_layout()
    elif pathname == '/scenarios':
        return create_scenarios_layout()
    else:
        return create_overview_layout()


# ============================================================================
# I-V CURVES PAGE CALLBACKS
# ============================================================================

@app.callback(
    [Output('module-iv-curve', 'figure'),
     Output('power-curve', 'figure'),
     Output('mpp-info-display', 'children'),
     Output('loss-analysis', 'children')],
    [Input('scenario-dropdown', 'value'),
     Input('irradiance-slider', 'value'),
     Input('temperature-slider', 'value'),
     Input('iv-display-options', 'value')]
)
def update_iv_curves(scenario_id, irradiance, temperature, display_options):
    """Update I-V curve visualizations"""
    
    # Get shading configuration
    if scenario_id == 'none':
        shading_config = None
    else:
        scenario = get_scenario_by_id(scenario_id)
        shading_config = convert_scenario_to_shading_config(scenario)
    
    # Create module
    module = PVModule(
        irradiance=irradiance,
        temperature=temperature,
        shading_config=shading_config
    )
    
    # Generate I-V curve
    iv_data = module.iv_curve(points=400)
    
    # Find MPP
    mpp = module.find_mpp()
    
    # Create figures
    show_power = 'show_power' in (display_options or [])
    show_mpp = 'show_mpp' in (display_options or [])
    show_ref = 'show_reference' in (display_options or [])
    
    # I-V curve
    iv_fig = plot_iv_curve(
        iv_data['voltages'],
        iv_data['currents'],
        iv_data['powers'],
        title=f"Modul I-V Kennlinie (G={irradiance} W/m², T={temperature}°C)",
        mpp=mpp if show_mpp else None,
        show_power=show_power
    )
    
    # Add reference curve if requested
    if show_ref:
        ref_module = PVModule(irradiance=irradiance, temperature=temperature, shading_config=None)
        ref_iv = ref_module.iv_curve(points=400)
        iv_fig.add_trace(
            go.Scatter(
                x=ref_iv['voltages'],
                y=ref_iv['currents'],
                name="Referenz (unverschattet)",
                line=dict(color='gray', dash='dash', width=1),
                mode='lines'
            ),
            secondary_y=False
        )
    
    # Power curve
    power_fig = plot_power_curve(
        iv_data['voltages'],
        iv_data['powers'],
        mpp=mpp if show_mpp else None,
        title="Leistungskurve"
    )
    
    # MPP info
    mpp_info = html.Div([
        html.P([html.Strong("Maximum Power Point:")]),
        html.P(f"Spannung: {format_voltage(mpp['voltage'])}"),
        html.P(f"Strom: {format_current(mpp['current'])}"),
        html.P(f"Leistung: {format_power(mpp['power'])}", className="text-success"),
        html.Hr(),
        html.P([html.Strong("Bypass Status:")]),
        html.P(f"Aktive Bypässe: {mpp['details']['num_bypassed_strings']} von 3")
    ])
    
    # Loss analysis
    if shading_config is not None:
        comparison = module.compare_with_unshaded()
        loss_info = html.Div([
            html.P([html.Strong("Verlustanalyse:")]),
            html.P(f"Unverschattet: {format_power(comparison['unshaded_mpp']['power'])}"),
            html.P(f"Verschattet: {format_power(comparison['shaded_mpp']['power'])}"),
            html.P([
                html.Span("Verlust: ", className="text-danger"),
                html.Span(f"{format_power(comparison['power_loss'])} ({comparison['power_loss_percent']:.1f}%)", 
                         className="text-danger fw-bold")
            ]),
            html.Hr(),
            html.P(f"ΔV: {comparison['voltage_change']:.2f} V"),
            html.P(f"ΔI: {comparison['current_change']:.2f} A")
        ])
    else:
        loss_info = html.P("Keine Verschattung - kein Verlust")
    
    return iv_fig, power_fig, mpp_info, loss_info


@app.callback(
    Output('scenario-description', 'children'),
    Input('scenario-dropdown', 'value')
)
def update_scenario_description(scenario_id):
    """Update scenario description text"""
    if scenario_id == 'none':
        return "Keine Verschattung - Referenzzustand"
    
    scenario = get_scenario_by_id(scenario_id)
    if scenario:
        return html.P([
            html.Strong(scenario['name']),
            html.Br(),
            scenario['description']
        ])
    return ""


# ============================================================================
# VOLTAGE DISTRIBUTION PAGE CALLBACKS
# ============================================================================

@app.callback(
    [Output('circuit-diagram', 'figure'),
     Output('voltage-heatmap', 'figure'),
     Output('power-dissipation-heatmap', 'figure'),
     Output('hotspot-details', 'children'),
     Output('operating-point-info', 'children')],
    [Input('scenario-dropdown', 'value'),
     Input('irradiance-slider', 'value'),
     Input('temperature-slider', 'value'),
     Input('operating-current-slider', 'value'),
     Input('voltage-display-options', 'value')]
)
def update_voltage_distribution(scenario_id, irradiance, temperature, current, display_options):
    """Update voltage distribution visualizations"""
    
    # Get shading configuration
    if scenario_id == 'none':
        shading_config = None
    else:
        scenario = get_scenario_by_id(scenario_id)
        shading_config = convert_scenario_to_shading_config(scenario)
    
    # Create module
    module = PVModule(
        irradiance=irradiance,
        temperature=temperature,
        shading_config=shading_config
    )
    
    # Get voltage map
    show_values = 'show_values' in (display_options or [])
    
    # Create visualizations
    circuit_fig = create_module_circuit_diagram(module, current, show_voltages=show_values)
    voltage_heatmap_fig = create_voltage_heatmap(module, current)
    power_heatmap_fig = create_power_dissipation_heatmap(module, current)
    
    # Hot-spot analysis
    hotspot_analysis = module.analyze_hotspots(current)
    
    if hotspot_analysis['num_hotspots'] > 0:
        hotspot_info = html.Div([
            html.H5(f"⚠️ {hotspot_analysis['num_hotspots']} Hot-Spots erkannt", className="text-danger"),
            html.P(f"Gesamte Hot-Spot-Leistung: {format_power(hotspot_analysis['total_hotspot_power'])}"),
            html.Hr(),
            html.P([html.Strong("Details:")]),
            html.Ul([
                html.Li(f"String {hs['string']+1}, Zelle {hs['cell']}: {format_voltage(hs['voltage'])}, {format_power(hs['power'])}")
                for hs in hotspot_analysis['hotspots'][:10]  # Limit to first 10
            ])
        ])
    else:
        hotspot_info = html.P("✓ Keine Hot-Spots detektiert", className="text-success")
    
    # Operating point info
    result = module.module_voltage_at_current(current)
    op_info = html.Div([
        html.P(f"Modulspannung: {format_voltage(result['voltage'])}"),
        html.P(f"Modulleistung: {format_power(result['total_power'])}"),
        html.P(f"Aktive Bypässe: {result['num_bypassed_strings']}")
    ])
    
    return circuit_fig, voltage_heatmap_fig, power_heatmap_fig, hotspot_info, op_info


# ============================================================================
# BYPASS DIODE PAGE CALLBACKS
# ============================================================================

@app.callback(
    [Output('string-voltage-chart', 'figure'),
     Output('bypass-threshold-chart', 'figure'),
     Output('bypass-status-display', 'children'),
     Output('bypass-cell-count-analysis', 'children')],
    [Input('bypass-test-num-cells', 'value'),
     Input('bypass-test-intensity', 'value'),
     Input('bypass-test-current', 'value')]
)
def update_bypass_analysis(num_cells, intensity, current):
    """Update bypass diode analysis"""
    
    # Create shading config for string 1
    shading_config = {
        'string_0': {i: intensity for i in range(int(num_cells))},
        'string_1': {},
        'string_2': {}
    }
    
    module = PVModule(irradiance=1000, temperature=25, shading_config=shading_config)
    
    result = module.module_voltage_at_current(current)
    
    # String voltage chart
    string_voltages = [sr['raw_string_voltage'] for sr in result['string_results']]
    bypass_states = result['bypass_states']
    
    colors = ['red' if bs else 'green' for bs in bypass_states]
    
    string_fig = go.Figure(data=[
        go.Bar(
            x=[f"String {i+1}" for i in range(3)],
            y=string_voltages,
            marker_color=colors,
            text=[f"{v:.2f}V" for v in string_voltages],
            textposition='auto'
        )
    ])
    string_fig.add_hline(y=-0.4, line_dash="dash", line_color="red", 
                         annotation_text="Bypass Schwelle (-0.4V)")
    string_fig.update_layout(
        title="String-Spannungen",
        yaxis_title="Spannung (V)",
        height=400
    )
    
    # Threshold analysis - vary number of cells
    cell_counts = list(range(0, 16))
    threshold_voltages = []
    bypass_active = []
    
    for n_cells in cell_counts:
        test_config = {
            'string_0': {i: intensity for i in range(n_cells)},
            'string_1': {},
            'string_2': {}
        }
        test_module = PVModule(irradiance=1000, temperature=25, shading_config=test_config)
        test_result = test_module.module_voltage_at_current(current)
        threshold_voltages.append(test_result['string_results'][0]['raw_string_voltage'])
        bypass_active.append(test_result['bypass_states'][0])
    
    threshold_fig = go.Figure()
    threshold_fig.add_trace(go.Scatter(
        x=cell_counts,
        y=threshold_voltages,
        mode='lines+markers',
        name='String-Spannung',
        line=dict(color='blue', width=2)
    ))
    threshold_fig.add_hline(y=-0.4, line_dash="dash", line_color="red",
                           annotation_text="Bypass aktiviert")
    threshold_fig.update_layout(
        title="Bypass-Aktivierung vs. Anzahl verschatteter Zellen",
        xaxis_title="Anzahl verschatteter Zellen",
        yaxis_title="String-Spannung (V)",
        height=400
    )
    
    # Bypass status
    if bypass_states[0]:
        status = html.Div([
            html.H5("🔴 Bypass EIN", className="text-danger"),
            html.P(f"String 1 Spannung: {format_voltage(string_voltages[0])}"),
            html.P(f"Unterhalb Schwelle von -0.4V"),
            html.P(f"{num_cells} Zellen verschattet bei {intensity*100:.0f}%")
        ])
    else:
        status = html.Div([
            html.H5("🟢 Bypass AUS", className="text-success"),
            html.P(f"String 1 Spannung: {format_voltage(string_voltages[0])}"),
            html.P(f"Oberhalb Schwelle von -0.4V"),
            html.P(f"{num_cells} Zellen verschattet - nicht ausreichend für Bypass-Aktivierung")
        ])
    
    # Cell count analysis
    activation_idx = next((i for i, active in enumerate(bypass_active) if active), None)
    if activation_idx is not None:
        cell_analysis = html.Div([
            html.P([
                html.Strong("Kritische Zellanzahl: "),
                f"{activation_idx} Zellen"
            ]),
            html.P(f"Bei {intensity*100:.0f}% Verschattung und {format_current(current)} Betriebsstrom"),
            html.P("Ab dieser Zellanzahl aktiviert der Bypass.")
        ])
    else:
        cell_analysis = html.P("Bypass aktiviert nicht im getesteten Bereich")
    
    return string_fig, threshold_fig, status, cell_analysis


# ============================================================================
# SEMICONDUCTOR PHYSICS PAGE CALLBACKS
# ============================================================================

@app.callback(
    Output('physics-tab-content', 'children'),
    [Input('physics-tabs', 'active_tab'),
     Input('reverse-voltage-slider', 'value'),
     Input('temperature-slider', 'value')]
)
def update_physics_tab(active_tab, reverse_voltage, temperature):
    """Update physics visualization based on selected tab"""
    
    physics = SemiconductorPhysics(temperature=temperature)
    
    if active_tab == 'tab-efield':
        # E-field profile
        E_profile = physics.electric_field_profile(reverse_voltage, points=200)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=E_profile['x'],
            y=E_profile['E'],
            mode='lines',
            line=dict(color='red', width=2),
            name='E-Feld'
        ))
        fig.update_layout(
            title=f"Elektrisches Feld im pn-Übergang (V = {reverse_voltage:.1f} V)",
            xaxis_title="Position (μm)",
            yaxis_title="E-Feld (V/cm)",
            height=500
        )
        
        return dbc.Card([
            dbc.CardBody([
                dcc.Graph(figure=fig),
                html.P(f"Maximale Feldstärke: {E_profile['E_max']:.2e} V/cm"),
                html.P(f"Sperrschichtweite: {E_profile['depletion_width']['W_total']:.2f} μm")
            ])
        ])
    
    elif active_tab == 'tab-bands':
        # Band diagram
        fig = plot_band_diagram(physics, reverse_voltage)
        
        return dbc.Card([
            dbc.CardBody([
                dcc.Graph(figure=fig),
                html.P("Energiebänder unter Reverse-Bias. Die Bandverbiegung zeigt das Potential über den Übergang.")
            ])
        ])
    
    elif active_tab == 'tab-pn-3d':
        # 3D pn-junction
        fig = plot_pn_junction_3d(physics, reverse_voltage, show_depletion=True)
        
        return dbc.Card([
            dbc.CardBody([
                dcc.Graph(figure=fig),
                html.P("3D Darstellung des pn-Übergangs mit Sperrschicht (gelb)")
            ])
        ])
    
    elif active_tab == 'tab-avalanche':
        # Avalanche animation
        if reverse_voltage < -10:
            fig = plot_avalanche_animation(physics, reverse_voltage, num_frames=20)
            message = "Avalanche-Durchbruch aktiv! Lawinenmultiplikation von Ladungsträgern."
        else:
            fig = plot_pn_junction_3d(physics, reverse_voltage)
            message = "Spannung zu niedrig für Avalanche-Durchbruch. Erhöhen Sie die Reverse-Spannung."
        
        return dbc.Card([
            dbc.CardBody([
                dcc.Graph(figure=fig),
                html.P(message)
            ])
        ])
    
    return html.P("Tab nicht implementiert")


@app.callback(
    [Output('physics-calculated-values', 'children'),
     Output('depletion-width-chart', 'figure'),
     Output('temperature-dependence-chart', 'figure')],
    [Input('reverse-voltage-slider', 'value'),
     Input('temperature-slider', 'value')]
)
def update_physics_calculations(reverse_voltage, temperature):
    """Update calculated physics values"""
    
    physics = SemiconductorPhysics(temperature=temperature)
    
    depl = physics.depletion_width(reverse_voltage)
    M = physics.avalanche_multiplication_factor(reverse_voltage)
    Vbr = physics.breakdown_voltage()
    E_profile = physics.electric_field_profile(reverse_voltage)
    
    values_display = html.Div([
        html.P(f"Sperrschichtweite: {depl['W_total']:.2f} μm"),
        html.P(f"Max. E-Feld: {E_profile['E_max']:.2e} V/cm"),
        html.P(f"Breakdown-Spannung: {Vbr:.2f} V"),
        html.P(f"Multiplikationsfaktor: {M:.2f}"),
        html.Hr(),
        html.Small(f"T = {temperature}°C")
    ])
    
    # Depletion width chart
    depl_fig = plot_depletion_width_vs_voltage(physics, V_range=(-20, 1))
    
    # Temperature dependence
    temp_data = physics.temperature_dependence_breakdown(temp_range=(-40, 85))
    temp_fig = go.Figure()
    temp_fig.add_trace(go.Scatter(
        x=temp_data['temperatures'],
        y=temp_data['breakdown_voltages'],
        mode='lines',
        line=dict(color='purple', width=2)
    ))
    temp_fig.update_layout(
        title="Breakdown-Spannung vs. Temperatur",
        xaxis_title="Temperatur (°C)",
        yaxis_title="Breakdown-Spannung (V)",
        height=400
    )
    
    return values_display, depl_fig, temp_fig


# ============================================================================
# SCENARIOS COMPARISON PAGE CALLBACKS
# ============================================================================

@app.callback(
    [Output('scenario-iv-comparison', 'figure'),
     Output('scenario-power-comparison', 'figure'),
     Output('scenario-comparison-table', 'children'),
     Output('scenario-hotspot-comparison', 'children')],
    [Input('update-comparison-btn', 'n_clicks')],
    [State('scenario-1-dropdown', 'value'),
     State('scenario-2-dropdown', 'value'),
     State('scenario-3-dropdown', 'value')]
)
def update_scenario_comparison(n_clicks, scenario_1, scenario_2, scenario_3):
    """Update scenario comparison visualizations"""
    
    scenarios_to_compare = [scenario_1, scenario_2]
    if scenario_3 != 'off':
        scenarios_to_compare.append(scenario_3)
    
    modules = []
    labels = []
    
    for scenario_id in scenarios_to_compare:
        if scenario_id == 'none':
            shading_config = None
            label = "Keine Verschattung"
        else:
            scenario = get_scenario_by_id(scenario_id)
            shading_config = convert_scenario_to_shading_config(scenario)
            label = scenario['name'] if scenario else scenario_id
        
        module = PVModule(irradiance=1000, temperature=25, shading_config=shading_config)
        modules.append(module)
        labels.append(label)
    
    # Generate I-V curves
    iv_fig = go.Figure()
    colors = ['blue', 'red', 'green', 'orange']
    
    for idx, (module, label) in enumerate(zip(modules, labels)):
        iv_data = module.iv_curve(points=300)
        iv_fig.add_trace(go.Scatter(
            x=iv_data['voltages'],
            y=iv_data['currents'],
            name=label,
            line=dict(color=colors[idx], width=2),
            mode='lines'
        ))
    
    iv_fig.update_layout(
        title="I-V Kennlinien Vergleich",
        xaxis_title="Spannung (V)",
        yaxis_title="Strom (A)",
        height=500,
        hovermode='x unified'
    )
    
    # Power comparison
    power_fig = go.Figure()
    
    for idx, (module, label) in enumerate(zip(modules, labels)):
        iv_data = module.iv_curve(points=300)
        power_fig.add_trace(go.Scatter(
            x=iv_data['voltages'],
            y=iv_data['powers'],
            name=label,
            line=dict(color=colors[idx], width=2),
            mode='lines'
        ))
    
    power_fig.update_layout(
        title="Leistungskurven Vergleich",
        xaxis_title="Spannung (V)",
        yaxis_title="Leistung (W)",
        height=400,
        hovermode='x unified'
    )
    
    # Comparison table
    mpp_data = []
    for module, label in zip(modules, labels):
        mpp = module.find_mpp()
        mpp_data.append({
            'Szenario': label,
            'V_mpp': mpp['voltage'],
            'I_mpp': mpp['current'],
            'P_mpp': mpp['power'],
            'Bypässe': mpp['details']['num_bypassed_strings']
        })
    
    table = dbc.Table([
        html.Thead(html.Tr([
            html.Th("Szenario"),
            html.Th("V_MPP (V)"),
            html.Th("I_MPP (A)"),
            html.Th("P_MPP (W)"),
            html.Th("Aktive Bypässe")
        ])),
        html.Tbody([
            html.Tr([
                html.Td(d['Szenario']),
                html.Td(f"{d['V_mpp']:.2f}"),
                html.Td(f"{d['I_mpp']:.2f}"),
                html.Td(f"{d['P_mpp']:.2f}", className="fw-bold"),
                html.Td(f"{d['Bypässe']}/3")
            ]) for d in mpp_data
        ])
    ], bordered=True, hover=True, striped=True)
    
    # Hot-spot comparison
    hotspot_rows = []
    for module, label in zip(modules, labels):
        mpp = module.find_mpp()
        current = mpp['current']
        hotspot_analysis = module.analyze_hotspots(current)
        
        hotspot_rows.append(html.Tr([
            html.Td(label),
            html.Td(str(hotspot_analysis['num_hotspots'])),
            html.Td(f"{hotspot_analysis['total_hotspot_power']:.2f} W")
        ]))
    
    hotspot_table = dbc.Table([
        html.Thead(html.Tr([
            html.Th("Szenario"),
            html.Th("Anzahl Hot-Spots"),
            html.Th("Gesamte Hot-Spot-Leistung")
        ])),
        html.Tbody(hotspot_rows)
    ], bordered=True, hover=True, striped=True)
    
    return iv_fig, power_fig, table, hotspot_table


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == '__main__':
    app.run(
        debug=APP_CONFIG['debug'],
        host=APP_CONFIG['host'],
        port=APP_CONFIG['port']
    )

