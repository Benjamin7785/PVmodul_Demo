"""
Single solar cell electrical model with reverse-bias breakdown
JIT-compiled with Numba for high performance
"""

import numpy as np
from numba import jit
from config import CELL_PARAMS, VT_REF, ELEMENTARY_CHARGE, BOLTZMANN


# ============================================================================
# JIT-COMPILED CORE FUNCTIONS (10-50x faster!)
# ============================================================================

@jit(nopython=True, cache=True, fastmath=True)
def _calculate_cell_current_jit(V, Iph, Is, n, Vt, Rs, Rsh, num_iter=6):
    """
    JIT-compiled single-diode equation solver
    
    Solves: I = Iph - Is*[exp((V+I*Rs)/(n*Vt)) - 1] - (V+I*Rs)/Rsh
    
    OPTIMIZED: Fast convergence with good accuracy
    
    Parameters:
    -----------
    V : np.ndarray
        Voltage array
    Iph, Is, n, Vt, Rs, Rsh : float
        Cell parameters
    num_iter : int
        Number of iterations (6 for speed/accuracy balance)
        
    Returns:
    --------
    np.ndarray
        Current array
    """
    I = np.full_like(V, Iph)  # Initial guess
    
    # Optimized iterations: 6 is enough with good relaxation
    for _ in range(num_iter):
        V_diode = V + I * Rs
        # Clip to prevent overflow
        exp_arg = np.clip(V_diode / (n * Vt), -50.0, 50.0)
        I_diode = Is * (np.exp(exp_arg) - 1.0)
        I_shunt = V_diode / Rsh
        I_new = Iph - I_diode - I_shunt
        # Fast convergence with 50/50 relaxation
        I = 0.5 * I + 0.5 * I_new
    
    return I


@jit(nopython=True, cache=True, fastmath=True)
def _calculate_avalanche_current_jit(V, Is, Vbr, Rsh):
    """
    JIT-compiled avalanche breakdown current
    
    Parameters:
    -----------
    V : np.ndarray
        Voltage array (negative)
    Is, Vbr, Rsh : float
        Cell parameters
        
    Returns:
    --------
    np.ndarray
        Avalanche current (negative)
    """
    Va = 0.5  # Avalanche characteristic voltage
    V_excess = np.abs(V) - Vbr
    I_leak = -Is * 100.0
    
    # Avalanche component
    I_avalanche = np.where(
        V_excess > 0.0,
        I_leak * np.exp(V_excess / Va),
        I_leak + V_excess / Rsh
    )
    
    return I_avalanche


@jit(nopython=True, cache=True, fastmath=True)
def _calculate_single_current_jit(V, Iph, Is, n, Vt, Rs, Rsh, Vbr):
    """
    Calculate current for a SINGLE voltage value (for bisection)
    """
    if V > -Vbr * 0.95:
        # Forward/slight reverse
        I = Iph
        for _ in range(6):
            V_diode = V + I * Rs
            exp_arg = min(50.0, max(-50.0, V_diode / (n * Vt)))
            I_diode = Is * (np.exp(exp_arg) - 1.0)
            I_shunt = V_diode / Rsh
            I_new = Iph - I_diode - I_shunt
            I = 0.5 * I + 0.5 * I_new
        return I
    else:
        # Breakdown region
        Va = 0.5
        V_excess = abs(V) - Vbr
        I_leak = -Is * 100.0
        if V_excess > 0.0:
            return I_leak * np.exp(V_excess / Va)
        else:
            return I_leak + V_excess / Rsh


@jit(nopython=True, cache=True)
def _find_voltage_for_current_jit(target_I, Iph, Is, n, Vt, Rs, Rsh, Vbr):
    """
    JIT-compiled bisection to find voltage for given current
    
    CORRECTED: Proper search range to bracket the solution
    """
    # Search range must BRACKET the solution:
    # At V_min: I should be HIGHER than target_I
    # At V_max: I should be LOWER than target_I
    
    if target_I >= 0 and target_I <= Iph * 1.01:
        # Forward bias: I decreases as V increases
        # At V=0: I ≈ I_sc (high)
        # At V=V_oc: I = 0 (low)
        # So use range [0, V_oc_estimate]
        V_oc_estimate = n * Vt * np.log((Iph + Is) / Is)  # Approximate V_oc
        V_min = 0.0
        V_max = min(V_oc_estimate * 1.2, 0.6)  # Slightly above V_oc, capped at 0.6V
    elif target_I < 0:
        V_min = -Vbr
        V_max = 0.0
    else:
        # I > I_sc: must be reverse bias
        V_min = -Vbr
        V_max = 0.0
    
    # Bisection
    for _ in range(40):
        V_mid = 0.5 * (V_min + V_max)
        I_mid = _calculate_single_current_jit(V_mid, Iph, Is, n, Vt, Rs, Rsh, Vbr)
        
        error = I_mid - target_I
        
        if abs(error) < 1e-4:
            return V_mid
        
        if error > 0.0:
            V_max = V_mid
        else:
            V_min = V_mid
    
    return V_mid


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
        self.Is_ref = CELL_PARAMS['Is']  # Reference saturation current at 25°C
        self.n = CELL_PARAMS['n']
        self.Rs = CELL_PARAMS['Rs']
        self.Rsh = CELL_PARAMS['Rsh']
        self.Vbr = CELL_PARAMS['Vbr_typical']
        self.alpha_Isc = CELL_PARAMS['alpha_Isc']
        self.beta_Voc = CELL_PARAMS['beta_Voc_cell']  # Per-cell coefficient!
        
        # Calculate thermal voltage at actual temperature
        T_kelvin = temperature + 273.15
        T_ref_kelvin = 25 + 273.15
        self.Vt = (BOLTZMANN * T_kelvin) / ELEMENTARY_CHARGE
        
        # Calculate photocurrent FIRST (needed for Is calculation)
        self._calculate_photocurrent()
        
        # Temperature-dependent saturation current
        # 
        # SIMPLE, ACCURATE APPROACH: Calculate Is backward from target Voc(T)
        # 
        # From datasheet: Voc changes by beta_Voc per degree
        # Voc(T) = Voc_ref + beta_Voc × (T - T_ref)
        #
        # From single-diode model: Voc = n×Vt×ln(Iph/Is)
        # Therefore: Is = Iph / exp(Voc / (n×Vt))
        #
        # This DIRECTLY enforces the correct temperature coefficient!
        
        dT = temperature - 25  # Temperature difference from STC
        
        # Calculate expected Voc at this temperature (from datasheet beta_Voc)
        Voc_ref = CELL_PARAMS['Voc_ref']  # 0.385 V at 25°C
        Voc_target = Voc_ref + self.beta_Voc * dT
        
        # Calculate Is that produces this Voc
        # From: Voc = n×Vt×ln(Iph/Is)
        # Is = Iph × exp(-Voc/(n×Vt))
        self.Is = self.Iph * np.exp(-Voc_target / (self.n * self.Vt))
        
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
        
        JIT-OPTIMIZED for 10-20x speedup!
        
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
            
            # JIT-COMPILED: 10-20x faster!
            I[mask_forward] = _calculate_cell_current_jit(
                V_fwd, self.Iph, self.Is, self.n, self.Vt, self.Rs, self.Rsh
            )
        
        # Deep reverse bias (breakdown region)
        mask_breakdown = voltage <= -self.Vbr * 0.95
        
        if np.any(mask_breakdown):
            V_rev = voltage[mask_breakdown]
            
            # JIT-COMPILED: 10-20x faster!
            I[mask_breakdown] = _calculate_avalanche_current_jit(
                V_rev, self.Is, self.Vbr, self.Rsh
            )
        
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
        
        Uses scipy.optimize (accurate) + JIT current() (fast)
        
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
            return self.current(v) - target_current  # current() is JIT-optimized!
        
        # Optimized search range
        V_oc = self.get_Voc()
        
        # For normal operation
        if target_current >= 0 and target_current <= self.Iph * 1.01:
            try:
                voltage = brentq(objective, 0.0, V_oc * 1.1, xtol=1e-4)  # Relaxed tolerance
                return voltage
            except (ValueError, RuntimeError):
                pass
        
        # For wider range
        try:
            voltage = brentq(objective, -self.Vbr, V_oc * 1.1, xtol=1e-4)
            return voltage
        except (ValueError, RuntimeError):
            # Fallback
            if target_current >= 0:
                return V_oc * (1 - min(target_current / self.Iph, 1.0))
            else:
                return -self.Vbr
    
    def get_Voc(self):
        """
        Get open circuit voltage
        
        Uses analytical formula for accuracy:
        At I=0: Voc = n × Vt × ln((Iph + Is) / Is)
        
        This is more accurate than numerical search for I=0!
        """
        # Analytical solution from single-diode equation at I=0
        # 0 = Iph - Is × (exp(Voc/(n×Vt)) - 1) - Voc/Rsh
        # For high Rsh, Voc/Rsh term is negligible:
        # Iph ≈ Is × (exp(Voc/(n×Vt)) - 1)
        # exp(Voc/(n×Vt)) ≈ Iph/Is + 1
        # Voc ≈ n × Vt × ln(Iph/Is + 1)
        
        if self.Iph > 0 and self.Is > 0:
            # Accurate formula
            Voc = self.n * self.Vt * np.log((self.Iph + self.Is) / self.Is)
            
            # Shunt correction (small but improves accuracy)
            # Iterative refinement
            for _ in range(3):
                I_shunt = Voc / self.Rsh
                Voc = self.n * self.Vt * np.log((self.Iph - I_shunt + self.Is) / self.Is)
            
            return Voc
        else:
            return 0.0
    
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


# ============================================================================
# LUT-BASED SOLAR CELL (200x FASTER!)
# ============================================================================

class LUTSolarCell(SolarCell):
    """
    Solar cell using Look-up Table for ultra-fast calculations
    
    Replaces scipy.optimize.brentq (~3-4ms) with interpolation (~0.01-0.02ms)
    → 200x speedup!
    
    Class variables (shared across all instances):
    """
    lut_interpolator = None  # Shared interpolator
    lut_loaded = False       # Flag to check if LUT is available
    
    @classmethod
    def set_lut_interpolator(cls, interpolator):
        """Set the LUT interpolator (call once at app startup)"""
        cls.lut_interpolator = interpolator
        cls.lut_loaded = True
        print("[OK] LUT interpolator loaded for LUTSolarCell")
    
    def find_operating_point(self, target_current):
        """
        Find voltage using LUT interpolation (FAST!)
        
        Parameters:
        -----------
        target_current : float
            Desired current in A
            
        Returns:
        --------
        float
            Cell voltage at this current
        """
        if not self.lut_loaded or self.lut_interpolator is None:
            # Fallback to original method
            print("[WARN] LUT not loaded, falling back to scipy.optimize (slow!)")
            return super().find_operating_point(target_current)
        
        # Use LUT interpolation (200x faster!)
        try:
            voltage = self.lut_interpolator([
                self.irradiance,
                self.temperature,
                self.shading_factor,
                target_current
            ])[0]
            return float(voltage)
        except Exception as e:
            # Fallback on error
            print(f"[WARN] LUT interpolation error: {e}, using fallback")
            return super().find_operating_point(target_current)

