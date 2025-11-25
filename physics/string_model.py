"""
Cell string model with bypass diode logic
"""

import numpy as np
from .cell_model import SolarCell, LUTSolarCell
from config import BYPASS_DIODE, MODULE_STRUCTURE


class CellString:
    """
    Models a string of solar cells in series with a bypass diode
    """
    
    def __init__(self, num_cells=36, irradiance=1000, temperature=25, shading_pattern=None, use_lut=True):
        """
        Initialize cell string
        
        Parameters:
        -----------
        num_cells : int
            Number of cells in string (default 36 half-cells)
        irradiance : float
            Base solar irradiance in W/m²
        temperature : float
            Cell temperature in °C
        shading_pattern : dict or None
            Dictionary mapping cell index to shading factor
            e.g., {5: 0.8, 6: 1.0} means cell 5 is 80% shaded, cell 6 is 100% shaded
        use_lut : bool
            Use LUT-based cells for speed (default True)
        """
        self.num_cells = num_cells
        self.irradiance = irradiance
        self.temperature = temperature
        self.use_lut = use_lut
        
        # Create cells (LUT-based if available, otherwise standard)
        CellClass = LUTSolarCell if use_lut else SolarCell
        
        # Initialize cells
        self.cells = []
        for i in range(num_cells):
            # Check if this cell is shaded
            shading_factor = 0.0
            if shading_pattern and i in shading_pattern:
                shading_factor = shading_pattern[i]
            
            cell = CellClass(
                irradiance=irradiance,
                temperature=temperature,
                shading_factor=shading_factor
            )
            self.cells.append(cell)
        
        # Bypass diode parameters
        self.bypass_Vf = BYPASS_DIODE['Vf']
        self.bypass_Is = BYPASS_DIODE['Is_diode']
        self.bypass_n = BYPASS_DIODE['n_diode']
        
    def string_current_at_voltage(self, voltage, current_guess=None):
        """
        Calculate string current when string voltage is fixed
        (More complex - requires iteration)
        
        Parameters:
        -----------
        voltage : float
            Total string voltage
        current_guess : float
            Initial guess for current
            
        Returns:
        --------
        dict
            {'current': I, 'cell_voltages': [...], 'bypass_active': bool}
        """
        from scipy.optimize import fsolve
        
        if current_guess is None:
            current_guess = self.cells[0].get_Isc() * 0.5
        
        def objective(I):
            # Sum of all cell voltages must equal total voltage
            cell_voltages = [cell.find_operating_point(I) for cell in self.cells]
            return sum(cell_voltages) - voltage
        
        try:
            current = fsolve(objective, current_guess)[0]
            cell_voltages = [cell.find_operating_point(current) for cell in self.cells]
            
            # Check if bypass should activate
            string_voltage = sum(cell_voltages)
            bypass_active = string_voltage < -self.bypass_Vf
            
            return {
                'current': current,
                'cell_voltages': cell_voltages,
                'bypass_active': bypass_active,
                'string_voltage': string_voltage
            }
        except:
            return {
                'current': 0.0,
                'cell_voltages': [0.0] * self.num_cells,
                'bypass_active': False,
                'string_voltage': 0.0
            }
    
    def string_voltage_at_current(self, current):
        """
        Calculate string voltage when current is fixed (series constraint)
        
        Parameters:
        -----------
        current : float
            String current in A
            
        Returns:
        --------
        dict
            {
                'voltage': total string voltage,
                'cell_voltages': list of individual cell voltages,
                'bypass_active': bool indicating if bypass diode conducts,
                'bypass_current': current through bypass diode
            }
        """
        # Calculate voltage across each cell for this current
        cell_voltages = []
        for cell in self.cells:
            V_cell = cell.find_operating_point(current)
            cell_voltages.append(V_cell)
        
        # Total string voltage (sum of series cells)
        string_voltage = sum(cell_voltages)
        
        # Check if bypass diode activates
        # Bypass diode is in parallel with string, conducts when string voltage < -Vf
        bypass_active = string_voltage < -self.bypass_Vf
        
        if bypass_active:
            # Bypass diode conducts - voltage is clamped to -Vf
            effective_voltage = -self.bypass_Vf
            # Calculate how much current flows through bypass
            # (In real scenario, current redistributes, but for this model, 
            # we assume most flows through bypass)
            bypass_current = current * 0.9  # Approximation
        else:
            effective_voltage = string_voltage
            bypass_current = 0.0
        
        return {
            'voltage': effective_voltage,
            'cell_voltages': cell_voltages,
            'bypass_active': bypass_active,
            'bypass_current': bypass_current,
            'raw_string_voltage': string_voltage  # Before bypass clamping
        }
    
    def iv_curve(self, current_range=None, points=200):
        """
        Generate I-V curve for the string
        
        Parameters:
        -----------
        current_range : tuple or None
            (I_min, I_max) range for current sweep
        points : int
            Number of points
            
        Returns:
        --------
        dict
            {
                'currents': array,
                'voltages': array,
                'bypass_states': array of bools
            }
        """
        if current_range is None:
            # Default range: 0 to slightly above Isc
            Isc_max = max([cell.get_Isc() for cell in self.cells])
            current_range = (0, Isc_max * 1.1)
        
        currents = np.linspace(current_range[0], current_range[1], points)
        voltages = []
        bypass_states = []
        
        for I in currents:
            result = self.string_voltage_at_current(I)
            voltages.append(result['voltage'])
            bypass_states.append(result['bypass_active'])
        
        return {
            'currents': currents,
            'voltages': np.array(voltages),
            'bypass_states': np.array(bypass_states),
            'powers': currents * np.array(voltages)
        }
    
    def find_mpp(self, fast=True):
        """
        Find maximum power point of string
        
        Parameters:
        -----------
        fast : bool
            If True, uses fewer points for faster calculation
        """
        # OPTIMIZED: VERY few points for speed
        if fast:
            iv_data = self.iv_curve(points=30)  # 30 points: minimum for accuracy
        else:
            iv_data = self.iv_curve(points=100)
        
        powers = iv_data['powers']
        idx_mpp = np.argmax(powers)
        
        return {
            'voltage': iv_data['voltages'][idx_mpp],
            'current': iv_data['currents'][idx_mpp],
            'power': powers[idx_mpp]
        }
    
    def analyze_shading(self, current):
        """
        Detailed analysis of shading effects at given operating current
        
        Parameters:
        -----------
        current : float
            Operating current in A
            
        Returns:
        --------
        dict
            Detailed information about cell voltages, hot-spots, etc.
        """
        result = self.string_voltage_at_current(current)
        
        # Identify cells in reverse bias (hot-spots)
        hotspot_cells = []
        total_hotspot_power = 0.0
        
        for i, V_cell in enumerate(result['cell_voltages']):
            if V_cell < 0:
                power_dissipated = -V_cell * current
                hotspot_cells.append({
                    'index': i,
                    'voltage': V_cell,
                    'power': power_dissipated,
                    'shading_factor': self.cells[i].shading_factor
                })
                total_hotspot_power += power_dissipated
        
        return {
            **result,
            'hotspot_cells': hotspot_cells,
            'total_hotspot_power': total_hotspot_power,
            'num_cells_in_reverse': len(hotspot_cells)
        }
    
    def get_num_shaded_cells(self):
        """Count number of shaded cells in string"""
        return sum(1 for cell in self.cells if cell.shading_factor > 0.01)
    
    def get_bypass_activation_threshold(self):
        """
        Calculate how many shaded cells needed to activate bypass
        
        Returns:
        --------
        dict
            Information about bypass activation
        """
        # For a given string current, determine when bypass activates
        # This depends on: number of shaded cells, their reverse voltage
        
        # Estimate: Bypass activates when sum of reverse voltages > Vf
        # Typical reverse voltage per shaded cell: ~6-12V
        
        avg_reverse_V = 8.0  # V per heavily shaded cell
        min_shaded_cells = int(np.ceil(self.bypass_Vf / avg_reverse_V))
        
        return {
            'bypass_threshold_voltage': -self.bypass_Vf,
            'estimated_min_shaded_cells': max(1, min_shaded_cells),
            'actual_shaded_cells': self.get_num_shaded_cells()
        }

