"""
Complete PV module model with 108 half-cells and 3 bypass diodes
"""

import numpy as np
from .string_model import CellString
from config import MODULE_STRUCTURE


class PVModule:
    """
    Models a complete PV module with multiple strings and bypass diodes
    Typical configuration: 108 half-cells divided into 3 strings of 36 cells each
    """
    
    def __init__(self, irradiance=1000, temperature=25, shading_config=None, use_lut=True):
        """
        Initialize PV module
        
        Parameters:
        -----------
        irradiance : float
            Solar irradiance in W/m²
        temperature : float
            Module temperature in °C
        shading_config : dict or None
            Dictionary with shading information for each string
            Format: {
                'string_0': {cell_index: shading_factor, ...},
                'string_1': {cell_index: shading_factor, ...},
                'string_2': {cell_index: shading_factor, ...}
            }
        use_lut : bool
            Use LUT-based cells for speed (default True)
        """
        self.irradiance = irradiance
        self.temperature = temperature
        self.num_strings = MODULE_STRUCTURE['num_strings']
        self.cells_per_string = MODULE_STRUCTURE['cells_per_string']
        self.total_cells = MODULE_STRUCTURE['total_cells']
        self.use_lut = use_lut
        
        # Initialize shading configuration
        if shading_config is None:
            shading_config = {f'string_{i}': {} for i in range(self.num_strings)}
        
        # Create cell strings
        self.strings = []
        for i in range(self.num_strings):
            string_key = f'string_{i}'
            shading_pattern = shading_config.get(string_key, {})
            
            string = CellString(
                num_cells=self.cells_per_string,
                irradiance=irradiance,
                temperature=temperature,
                shading_pattern=shading_pattern,
                use_lut=use_lut
            )
            self.strings.append(string)
    
    def module_voltage_at_current(self, current):
        """
        Calculate module voltage at given current
        All strings are in series, so same current flows through all
        
        Parameters:
        -----------
        current : float
            Module current in A
            
        Returns:
        --------
        dict
            {
                'voltage': total module voltage,
                'string_results': list of results for each string,
                'total_power': module power,
                'bypass_states': list of bypass states
            }
        """
        string_results = []
        total_voltage = 0.0
        bypass_states = []
        
        for string in self.strings:
            result = string.string_voltage_at_current(current)
            string_results.append(result)
            total_voltage += result['voltage']
            bypass_states.append(result['bypass_active'])
        
        return {
            'voltage': total_voltage,
            'current': current,
            'total_power': total_voltage * current,
            'string_results': string_results,
            'bypass_states': bypass_states,
            'num_bypassed_strings': sum(bypass_states)
        }
    
    def iv_curve(self, current_range=None, points=300):
        """
        Generate module I-V curve
        
        Parameters:
        -----------
        current_range : tuple or None
            (I_min, I_max) range
        points : int
            Number of points
            
        Returns:
        --------
        dict
            {
                'currents': array,
                'voltages': array,
                'powers': array,
                'bypass_states': array showing which strings have bypass active
            }
        """
        if current_range is None:
            # Default: 0 to Isc (should not exceed module Isc!)
            # Module Isc is determined by the MINIMUM string Isc (series connection)
            Isc_values = []
            for string in self.strings:
                # Get Isc of string (minimum of all cells in string)
                Isc = min([cell.get_Isc() for cell in string.cells])
                Isc_values.append(Isc)
            # FIXED: Use MINIMUM Isc (series constraint), not maximum!
            I_max = min(Isc_values) * 1.05  # Small margin for safety
            current_range = (0, I_max)
        
        currents = np.linspace(current_range[0], current_range[1], points)
        voltages = []
        powers = []
        bypass_states_all = []
        
        for I in currents:
            result = self.module_voltage_at_current(I)
            voltages.append(result['voltage'])
            powers.append(result['total_power'])
            bypass_states_all.append(result['bypass_states'])
        
        return {
            'currents': currents,
            'voltages': np.array(voltages),
            'powers': np.array(powers),
            'bypass_states': np.array(bypass_states_all)
        }
    
    def find_mpp(self, fast=True):
        """
        Find maximum power point
        
        Parameters:
        -----------
        fast : bool
            If True, uses fast method with fewer points (default)
            If False, uses accurate method with more points
        
        Returns:
        --------
        dict
            {'voltage': V_mpp, 'current': I_mpp, 'power': P_mpp, 'details': ...}
        """
        # OPTIMIZED: VERY few points for speed
        if fast:
            iv_data = self.iv_curve(points=30)  # 30 points: minimum for accuracy
        else:
            iv_data = self.iv_curve(points=100)
        
        # Find MPP
        idx_mpp = np.argmax(iv_data['powers'])
        
        # Get detailed state at MPP
        mpp_current = iv_data['currents'][idx_mpp]
        mpp_details = self.module_voltage_at_current(mpp_current)
        
        return {
            'voltage': iv_data['voltages'][idx_mpp],
            'current': mpp_current,
            'power': iv_data['powers'][idx_mpp],
            'details': mpp_details
        }
    
    def get_cell_voltage_map(self, current):
        """
        Get voltage of every cell in the module
        
        Parameters:
        -----------
        current : float
            Operating current
            
        Returns:
        --------
        dict
            {
                'voltages': 2D array [string_index][cell_index],
                'string_voltages': array of string voltages,
                'bypass_states': array of bypass states
            }
        """
        result = self.module_voltage_at_current(current)
        
        voltage_map = []
        string_voltages = []
        
        for string_result in result['string_results']:
            voltage_map.append(string_result['cell_voltages'])
            string_voltages.append(string_result['voltage'])
        
        return {
            'cell_voltages': voltage_map,
            'string_voltages': string_voltages,
            'bypass_states': result['bypass_states'],
            'module_voltage': result['voltage']
        }
    
    def analyze_hotspots(self, current):
        """
        Identify and analyze all hot-spot cells in module
        
        Parameters:
        -----------
        current : float
            Operating current
            
        Returns:
        --------
        dict
            Detailed hot-spot analysis
        """
        result = self.module_voltage_at_current(current)
        
        all_hotspots = []
        total_hotspot_power = 0.0
        
        for string_idx, string_result in enumerate(result['string_results']):
            for cell_idx, V_cell in enumerate(string_result['cell_voltages']):
                if V_cell < 0:
                    # Cell in reverse bias - hot-spot
                    power = -V_cell * current
                    all_hotspots.append({
                        'string': string_idx,
                        'cell': cell_idx,
                        'voltage': V_cell,
                        'power': power,
                        'shading_factor': self.strings[string_idx].cells[cell_idx].shading_factor
                    })
                    total_hotspot_power += power
        
        return {
            'hotspots': all_hotspots,
            'total_hotspot_power': total_hotspot_power,
            'num_hotspots': len(all_hotspots),
            'bypass_states': result['bypass_states']
        }
    
    def compare_with_unshaded(self):
        """
        Compare this module with an unshaded reference
        
        Returns:
        --------
        dict
            Comparison metrics
        """
        # Create unshaded reference module
        ref_module = PVModule(
            irradiance=self.irradiance,
            temperature=self.temperature,
            shading_config=None
        )
        
        # Get MPP for both
        shaded_mpp = self.find_mpp()
        unshaded_mpp = ref_module.find_mpp()
        
        # Calculate losses
        power_loss = unshaded_mpp['power'] - shaded_mpp['power']
        power_loss_percent = (power_loss / unshaded_mpp['power']) * 100
        
        return {
            'unshaded_mpp': unshaded_mpp,
            'shaded_mpp': shaded_mpp,
            'power_loss': power_loss,
            'power_loss_percent': power_loss_percent,
            'voltage_change': shaded_mpp['voltage'] - unshaded_mpp['voltage'],
            'current_change': shaded_mpp['current'] - unshaded_mpp['current']
        }
    
    def get_shading_summary(self):
        """
        Get summary of shading configuration
        
        Returns:
        --------
        dict
            Summary statistics
        """
        summary = {
            'total_cells': self.total_cells,
            'strings': []
        }
        
        for string_idx, string in enumerate(self.strings):
            num_shaded = string.get_num_shaded_cells()
            shading_factors = [cell.shading_factor for cell in string.cells]
            
            summary['strings'].append({
                'index': string_idx,
                'total_cells': string.num_cells,
                'shaded_cells': num_shaded,
                'shading_factors': shading_factors,
                'avg_shading': np.mean(shading_factors) if shading_factors else 0.0
            })
        
        # Module-level summary
        total_shaded = sum(s['shaded_cells'] for s in summary['strings'])
        summary['total_shaded_cells'] = total_shaded
        summary['shading_percentage'] = (total_shaded / self.total_cells) * 100
        
        return summary
    
    def simulate_scenarios(self, current_points=None):
        """
        Simulate multiple operating points
        
        Parameters:
        -----------
        current_points : list or None
            Specific current values to simulate
            
        Returns:
        --------
        list of dict
            Results at each operating point
        """
        if current_points is None:
            # Use MPP and a few other points
            mpp = self.find_mpp()
            I_mpp = mpp['current']
            current_points = [0, I_mpp * 0.5, I_mpp, I_mpp * 1.2]
        
        results = []
        for I in current_points:
            result = self.module_voltage_at_current(I)
            hotspot_analysis = self.analyze_hotspots(I)
            
            results.append({
                'current': I,
                'module_result': result,
                'hotspot_analysis': hotspot_analysis
            })
        
        return results

