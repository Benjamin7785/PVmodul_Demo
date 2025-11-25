"""
Utility functions for the application
"""

import json
import numpy as np


def load_scenarios():
    """
    Load predefined scenarios from JSON file
    
    Returns:
    --------
    dict
        Scenarios data
    """
    try:
        with open('data/scenarios.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return {'scenarios': []}


def get_scenario_by_id(scenario_id):
    """
    Get specific scenario configuration
    
    Parameters:
    -----------
    scenario_id : str
        Scenario identifier
        
    Returns:
    --------
    dict or None
        Scenario configuration
    """
    scenarios_data = load_scenarios()
    
    for scenario in scenarios_data['scenarios']:
        if scenario['id'] == scenario_id:
            return scenario
    
    return None


def convert_scenario_to_shading_config(scenario, intensity_override=None):
    """
    Convert scenario format to shading configuration for module
    
    Parameters:
    -----------
    scenario : dict
        Scenario data (defines WHICH cells are shaded)
    intensity_override : float or None
        If provided, overrides the scenario's default intensity (0.0-1.0)
        Allows dynamic control of HOW MUCH cells are shaded
        
    Returns:
    --------
    dict
        Shading configuration {string_0: {cell_idx: factor}, ...}
    """
    if scenario is None:
        return None
    
    shading_pattern = scenario['shading_pattern']
    
    # Use override if provided, otherwise use scenario's default intensity
    if intensity_override is not None:
        shading_intensity = intensity_override
    else:
        shading_intensity = scenario.get('shading_intensity', 1.0)
    
    # Convert list indices to dict with intensity
    config = {}
    for string_key, cell_list in shading_pattern.items():
        cell_dict = {cell_idx: shading_intensity for cell_idx in cell_list}
        config[string_key] = cell_dict
    
    return config


def create_shading_config_from_counts(num_cells_s1, num_cells_s2, num_cells_s3, intensity=1.0):
    """
    Create shading config from number of shaded cells per string
    
    Parameters:
    -----------
    num_cells_s1, num_cells_s2, num_cells_s3 : int
        Number of shaded cells in each string
    intensity : float
        Shading intensity (0-1)
        
    Returns:
    --------
    dict
        Shading configuration
    """
    config = {
        'string_0': {i: intensity for i in range(int(num_cells_s1))},
        'string_1': {i: intensity for i in range(int(num_cells_s2))},
        'string_2': {i: intensity for i in range(int(num_cells_s3))}
    }
    return config


def format_power(watts):
    """Format power value with appropriate unit"""
    if watts >= 1000:
        return f"{watts/1000:.2f} kW"
    else:
        return f"{watts:.2f} W"


def format_voltage(volts):
    """Format voltage value"""
    return f"{volts:.2f} V"


def format_current(amps):
    """Format current value"""
    return f"{amps:.2f} A"


def format_percentage(value):
    """Format percentage value"""
    return f"{value:.1f}%"

