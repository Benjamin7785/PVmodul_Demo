"""
Single solar cell electrical model with reverse-bias breakdown
"""

import numpy as np
from config import CELL_PARAMS, VT_REF, ELEMENTARY_CHARGE, BOLTZMANN


class SolarCell:
    """
    Models a single solar cell including:
    - Forward bias (normal operation)
    - Reverse bias (shading condition)
    - Avalanche breakdown
    """
    
    def __init__(self, irradiance=1000, temperature=25, shading_factor=0.0):
        """
        Initialize solar cell
        
        Parameters:
        -----------
        irradiance : float
            Solar irradiance in W/m² (default 1000 W/m²)
        temperature : float
            Cell temperature in °C (default 25°C)
        shading_factor : float
            Fraction of cell that is shaded (0.0 = no shade, 1.0 = full shade)
        """
        self.irradiance = irradiance
        self.temperature = temperature
        self.shading_factor = np.clip(shading_factor, 0.0, 1.0)
        
        # Load parameters
        self.Iph_ref = CELL_PARAMS['Iph_ref']
        self.Is = CELL_PARAMS['Is']
        self.n = CELL_PARAMS['n']
        self.Rs = CELL_PARAMS['Rs']
        self.Rsh = CELL_PARAMS['Rsh']
        self.Vbr = CELL_PARAMS['Vbr_typical']
        self.alpha_Isc = CELL_PARAMS['alpha_Isc']
        self.beta_Voc = CELL_PARAMS['beta_Voc']
        
        # Calculate thermal voltage at actual temperature
        T_kelvin = temperature + 273.15
        self.Vt = (BOLTZMANN * T_kelvin) / ELEMENTARY_CHARGE
        
        # Calculate photocurrent based on irradiance and shading
        self._calculate_photocurrent()
        
    def _calculate_photocurrent(self):
        """Calculate photocurrent based on irradiance, temperature, and shading"""
        # Scale with irradiance (linear approximation)
        Iph_base = self.Iph_ref * (self.irradiance / 1000.0)
        
        # Temperature correction
        dT = self.temperature - 25
        Iph_base = Iph_base * (1 + self.alpha_Isc * dT)
        
        # Apply shading: reduce photocurrent
        self.Iph = Iph_base * (1 - self.shading_factor)
        
    def current(self, voltage):
        """
        Calculate cell current at given voltage using single-diode model
        
        Parameters:
        -----------
        voltage : float or np.ndarray
            Cell voltage in V
            
        Returns:
        --------
        float or np.ndarray
            Cell current in A
        """
        voltage = np.asarray(voltage)
        
        # Initialize current array
        I = np.zeros_like(voltage, dtype=float)
        
        # Forward and slightly reverse bias (normal diode equation)
        mask_forward = voltage > -self.Vbr * 0.95
        
        if np.any(mask_forward):
            V_fwd = voltage[mask_forward]
            
            # Single-diode equation: I = Iph - Is*[exp((V+I*Rs)/(n*Vt)) - 1] - (V+I*Rs)/Rsh
            # Initialize with approximate solution
            I[mask_forward] = self.Iph
            
            # Iterative solution with better convergence
            for _ in range(10):  # More iterations for better accuracy
                V_diode = V_fwd + I[mask_forward] * self.Rs
                # Protect against overflow in exp
                exp_arg = np.clip(V_diode / (self.n * self.Vt), -50, 50)
                I_diode = self.Is * (np.exp(exp_arg) - 1)
                I_shunt = V_diode / self.Rsh
                I_new = self.Iph - I_diode - I_shunt
                # Use relaxation for stability
                I[mask_forward] = 0.5 * I[mask_forward] + 0.5 * I_new
        
        # Deep reverse bias (breakdown region)
        mask_breakdown = voltage <= -self.Vbr * 0.95
        
        if np.any(mask_breakdown):
            V_rev = voltage[mask_breakdown]
            
            # Avalanche breakdown model
            # Current increases rapidly once breakdown voltage is exceeded
            breakdown_current = self._avalanche_current(V_rev)
            I[mask_breakdown] = breakdown_current
            
        return I if voltage.shape else float(I)
    
    def _avalanche_current(self, voltage):
        """
        Calculate current in avalanche breakdown region
        
        Parameters:
        -----------
        voltage : np.ndarray
            Negative voltage values
            
        Returns:
        --------
        np.ndarray
            Current in avalanche breakdown (negative, indicating reverse flow)
        """
        # Avalanche breakdown model: exponential increase
        # I = -Is * exp(-(|V| - Vbr) / Va)
        # where Va is avalanche voltage scale factor
        
        Va = 0.5  # V, avalanche characteristic voltage
        V_excess = np.abs(voltage) - self.Vbr
        
        # Base reverse current (leakage)
        I_leak = -self.Is * 100  # Small leakage current
        
        # Avalanche component (only when |V| > Vbr)
        I_avalanche = np.where(
            V_excess > 0,
            I_leak * np.exp(V_excess / Va),
            I_leak + V_excess / self.Rsh  # Linear region before breakdown
        )
        
        return I_avalanche
    
    def power(self, voltage):
        """
        Calculate power dissipation/generation at given voltage
        
        Parameters:
        -----------
        voltage : float or np.ndarray
            Cell voltage in V
            
        Returns:
        --------
        float or np.ndarray
            Power in W (positive = generation, negative = dissipation)
        """
        I = self.current(voltage)
        return voltage * I
    
    def iv_curve(self, v_min=-15, v_max=1.0, points=500):
        """
        Generate complete I-V curve
        
        Parameters:
        -----------
        v_min : float
            Minimum voltage (default -15V for breakdown region)
        v_max : float
            Maximum voltage (default 1.0V, above Voc)
        points : int
            Number of points in curve
            
        Returns:
        --------
        tuple of np.ndarray
            (voltages, currents)
        """
        voltages = np.linspace(v_min, v_max, points)
        currents = self.current(voltages)
        return voltages, currents
    
    def find_operating_point(self, target_current):
        """
        Find voltage for a given current (operating point in series string)
        
        Parameters:
        -----------
        target_current : float
            Desired current in A
            
        Returns:
        --------
        float
            Cell voltage at this current
        """
        from scipy.optimize import brentq
        
        def objective(v):
            return self.current(v) - target_current
        
        # For normal operation (positive current), search in forward bias first
        if target_current >= 0:
            try:
                # Normal operating range: 0V to slightly above Voc (~0.7V)
                voltage = brentq(objective, -0.1, 0.8, xtol=1e-6)
                return voltage
            except (ValueError, RuntimeError):
                # If not found in normal range, might be in breakdown
                pass
        
        # For negative current or if normal range failed, search broader range
        try:
            # Search from deep reverse bias to above Voc
            voltage = brentq(objective, -20, 1.0, xtol=1e-6)
            return voltage
        except (ValueError, RuntimeError):
            # If all fails, estimate based on rough I-V characteristics
            # For normal forward operation
            if target_current > 0 and target_current <= self.Iph:
                # Rough estimate: V ≈ Voc * (1 - I/Isc)
                Voc_est = 0.65  # Typical Voc for Si cell
                Isc_est = self.Iph
                if Isc_est > 0:
                    return Voc_est * (1 - target_current / Isc_est) * 0.8
                return 0.5
            # For reverse bias (shaded cell forced to conduct)
            elif target_current > self.Iph:
                # Cell must be in reverse bias
                return -12.0  # Typical breakdown voltage
            else:
                return 0.0
    
    def get_Voc(self):
        """Get open circuit voltage"""
        return self.find_operating_point(0.0)
    
    def get_Isc(self):
        """Get short circuit current"""
        return self.current(0.0)
    
    def get_mpp(self):
        """
        Find maximum power point
        
        Returns:
        --------
        dict
            {'voltage': V_mpp, 'current': I_mpp, 'power': P_mpp}
        """
        v, i = self.iv_curve(v_min=0, v_max=self.get_Voc() * 1.1, points=200)
        p = v * i
        idx_mpp = np.argmax(p)
        
        return {
            'voltage': v[idx_mpp],
            'current': i[idx_mpp],
            'power': p[idx_mpp]
        }
    
    def is_in_breakdown(self, voltage):
        """Check if cell is operating in breakdown region"""
        return voltage < -self.Vbr * 0.9
    
    def hotspot_power(self, current):
        """
        Calculate hot-spot power dissipation when cell is forced to carry current
        
        Parameters:
        -----------
        current : float
            String current forced through shaded cell
            
        Returns:
        --------
        float
            Power dissipated in cell (positive value indicates heating)
        """
        voltage = self.find_operating_point(current)
        
        if voltage < 0:
            # Reverse bias - cell is dissipating power
            return -voltage * current  # Absolute power dissipation
        else:
            return 0.0  # No hot-spot in forward bias

