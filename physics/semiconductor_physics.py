"""
Semiconductor physics engine for visualizing breakdown mechanisms
Includes depletion region, electric field, and avalanche multiplication
"""

import numpy as np
from config import SEMICONDUCTOR_PARAMS, ELEMENTARY_CHARGE, BOLTZMANN


class SemiconductorPhysics:
    """
    Models semiconductor physics of pn-junction under reverse bias
    """
    
    def __init__(self, temperature=25):
        """
        Initialize semiconductor physics model
        
        Parameters:
        -----------
        temperature : float
            Temperature in °C
        """
        self.temperature = temperature
        self.T_kelvin = temperature + 273.15
        
        # Load parameters
        self.epsilon = SEMICONDUCTOR_PARAMS['epsilon_si']
        self.Eg = SEMICONDUCTOR_PARAMS['Eg']
        self.ni = SEMICONDUCTOR_PARAMS['ni']
        self.Na = SEMICONDUCTOR_PARAMS['Na']  # p-side acceptor concentration
        self.Nd = SEMICONDUCTOR_PARAMS['Nd']  # n-side donor concentration
        self.mu_n = SEMICONDUCTOR_PARAMS['mu_n']
        self.mu_p = SEMICONDUCTOR_PARAMS['mu_p']
        self.alpha_n = SEMICONDUCTOR_PARAMS['alpha_n']
        self.alpha_p = SEMICONDUCTOR_PARAMS['alpha_p']
        
        # Calculate built-in potential
        self.Vbi = self._calculate_builtin_potential()
        
    def _calculate_builtin_potential(self):
        """Calculate built-in potential of pn-junction"""
        Vt = (BOLTZMANN * self.T_kelvin) / ELEMENTARY_CHARGE
        Vbi = Vt * np.log((self.Na * self.Nd) / (self.ni ** 2))
        return Vbi
    
    def depletion_width(self, V_applied=0):
        """
        Calculate depletion region width under applied voltage
        
        Parameters:
        -----------
        V_applied : float
            Applied voltage (negative for reverse bias)
            
        Returns:
        --------
        dict
            {
                'W_total': total depletion width in cm,
                'xn': width in n-region,
                'xp': width in p-region
            }
        """
        # Total potential across junction
        V_total = self.Vbi - V_applied  # For reverse bias, V_applied < 0, so V_total increases
        
        # Depletion width (one-sided abrupt junction approximation)
        W_total = np.sqrt((2 * self.epsilon * V_total) / ELEMENTARY_CHARGE * 
                          (self.Na + self.Nd) / (self.Na * self.Nd))
        
        # Width extends more into lightly doped side
        xn = W_total * self.Na / (self.Na + self.Nd)  # n-side
        xp = W_total * self.Nd / (self.Na + self.Nd)  # p-side
        
        return {
            'W_total': W_total * 1e4,  # Convert to μm
            'xn': xn * 1e4,  # μm
            'xp': xp * 1e4,  # μm
            'V_total': V_total
        }
    
    def electric_field_profile(self, V_applied=0, points=100):
        """
        Calculate electric field distribution in depletion region
        
        Parameters:
        -----------
        V_applied : float
            Applied voltage
        points : int
            Number of spatial points
            
        Returns:
        --------
        dict
            {
                'x': position array (μm),
                'E': electric field array (V/cm),
                'E_max': maximum electric field
            }
        """
        depl = self.depletion_width(V_applied)
        
        # Maximum electric field at junction (x=0)
        E_max = (2 * depl['V_total']) / (depl['W_total'] * 1e-4)  # V/cm
        
        # Position array: -xp to +xn
        x = np.linspace(-depl['xp'], depl['xn'], points)
        
        # Electric field: triangular profile, max at x=0
        E = np.zeros_like(x)
        
        # p-side (-xp to 0)
        mask_p = x < 0
        E[mask_p] = E_max * (1 + x[mask_p] / depl['xp'])
        
        # n-side (0 to xn)
        mask_n = x >= 0
        E[mask_n] = E_max * (1 - x[mask_n] / depl['xn'])
        
        return {
            'x': x,  # μm
            'E': E,  # V/cm
            'E_max': E_max,  # V/cm
            'depletion_width': depl
        }
    
    def breakdown_voltage(self):
        """
        Estimate avalanche breakdown voltage
        
        Returns:
        --------
        float
            Breakdown voltage in V
        """
        # Critical electric field for Si (approximate)
        E_crit = 3e5  # V/cm for Si (varies with doping)
        
        # Adjust for doping concentration (higher doping -> lower breakdown voltage)
        # Empirical relationship
        N_doping = min(self.Na, self.Nd)  # Limiting concentration
        E_crit_adjusted = E_crit * (N_doping / 1e16) ** 0.25
        
        # Breakdown voltage
        Vbr = (E_crit_adjusted ** 2) * self.epsilon / (2 * ELEMENTARY_CHARGE * N_doping)
        
        return Vbr
    
    def avalanche_multiplication_factor(self, V_applied):
        """
        Calculate avalanche multiplication factor M
        
        Parameters:
        -----------
        V_applied : float
            Applied reverse voltage (negative)
            
        Returns:
        --------
        float
            Multiplication factor M (M >> 1 near breakdown)
        """
        Vbr = self.breakdown_voltage()
        
        # Empirical multiplication factor model
        # M = 1 / (1 - (V/Vbr)^n)
        n = 3  # Empirical exponent
        
        V_reverse = abs(V_applied)
        
        if V_reverse < Vbr * 0.95:
            M = 1 / (1 - (V_reverse / Vbr) ** n)
        else:
            # Near breakdown, M increases very rapidly
            M = 1000 * np.exp((V_reverse - Vbr * 0.95) / (Vbr * 0.05))
        
        return M
    
    def impact_ionization_rate(self, E_field):
        """
        Calculate impact ionization rate at given electric field
        
        Parameters:
        -----------
        E_field : float or array
            Electric field in V/cm
            
        Returns:
        --------
        dict
            {
                'alpha_n': electron ionization rate (1/cm),
                'alpha_p': hole ionization rate (1/cm)
            }
        """
        # Chynoweth's law: alpha = A * exp(-B/E)
        # For Si at room temperature (approximate)
        A_n = 7e5  # 1/cm
        B_n = 1.23e6  # V/cm
        A_p = 1.6e6  # 1/cm
        B_p = 2e6  # V/cm
        
        E_field = np.abs(E_field)
        
        alpha_n = A_n * np.exp(-B_n / E_field)
        alpha_p = A_p * np.exp(-B_p / E_field)
        
        return {
            'alpha_n': alpha_n,
            'alpha_p': alpha_p,
            'alpha_total': alpha_n + alpha_p
        }
    
    def carrier_generation_profile(self, V_applied=0, points=100):
        """
        Calculate carrier generation rate due to avalanche
        
        Parameters:
        -----------
        V_applied : float
            Applied reverse voltage
        points : int
            Spatial resolution
            
        Returns:
        --------
        dict
            Position-dependent generation rate
        """
        E_profile = self.electric_field_profile(V_applied, points)
        
        # Ionization rates
        ionization = self.impact_ionization_rate(E_profile['E'])
        
        # Generation rate proportional to ionization rate and carrier density
        # Simplified: G(x) ~ alpha(x) * carrier_density
        # Near breakdown, this increases exponentially
        
        M = self.avalanche_multiplication_factor(V_applied)
        generation_rate = ionization['alpha_total'] * M * 1e10  # carriers/(cm³·s)
        
        return {
            'x': E_profile['x'],
            'generation_rate': generation_rate,
            'E_field': E_profile['E'],
            'multiplication_factor': M
        }
    
    def band_diagram(self, V_applied=0, points=100):
        """
        Calculate energy band diagram under bias
        
        Parameters:
        -----------
        V_applied : float
            Applied voltage
        points : int
            Spatial points
            
        Returns:
        --------
        dict
            Band edges Ec, Ev, Ef vs position
        """
        depl = self.depletion_width(V_applied)
        
        # Position array
        x = np.linspace(-depl['xp'], depl['xn'], points)
        
        # Potential profile (integrate electric field)
        E_profile = self.electric_field_profile(V_applied, points)
        
        # Potential: integrate -E
        dx = x[1] - x[0] if len(x) > 1 else 1
        potential = -np.cumsum(E_profile['E']) * dx * 1e-4  # Convert to V
        potential = potential - potential[0]  # Reference to p-side
        
        # Band edges
        # Conduction band
        Ec = -ELEMENTARY_CHARGE * potential
        
        # Valence band
        Ev = Ec - self.Eg * ELEMENTARY_CHARGE
        
        # Fermi level (flat in equilibrium, split under bias)
        Ef = np.zeros_like(x)
        
        return {
            'x': x,  # μm
            'Ec': Ec,  # eV
            'Ev': Ev,  # eV
            'Ef': Ef,  # eV
            'potential': potential  # V
        }
    
    def generate_avalanche_particles(self, V_applied, num_particles=100):
        """
        Generate particle positions for avalanche visualization
        Simulates carrier multiplication cascade
        
        Parameters:
        -----------
        V_applied : float
            Applied reverse voltage
        num_particles : int
            Number of particles to generate
            
        Returns:
        --------
        dict
            Particle positions and velocities for animation
        """
        E_profile = self.electric_field_profile(V_applied)
        M = self.avalanche_multiplication_factor(V_applied)
        
        # Generate particles in high-field region
        # Density increases where E-field is high
        
        x_positions = []
        y_positions = []
        z_positions = []
        particle_types = []  # 'electron' or 'hole'
        
        # Start with some seed particles
        for i in range(num_particles):
            # Position weighted by E-field
            x = np.random.normal(0, E_profile['depletion_width']['W_total'] / 4)
            y = np.random.uniform(-1, 1)
            z = np.random.uniform(-1, 1)
            
            x_positions.append(x)
            y_positions.append(y)
            z_positions.append(z)
            
            # Alternate between electrons and holes
            particle_types.append('electron' if i % 2 == 0 else 'hole')
        
        return {
            'x': np.array(x_positions),
            'y': np.array(y_positions),
            'z': np.array(z_positions),
            'types': particle_types,
            'multiplication_factor': M,
            'E_max': E_profile['E_max']
        }
    
    def temperature_dependence_breakdown(self, temp_range=None):
        """
        Calculate how breakdown voltage varies with temperature
        
        Parameters:
        -----------
        temp_range : tuple or None
            (T_min, T_max) in °C
            
        Returns:
        --------
        dict
            Temperature vs breakdown voltage
        """
        if temp_range is None:
            temp_range = (-40, 85)  # Typical operating range
        
        temps = np.linspace(temp_range[0], temp_range[1], 50)
        Vbr_values = []
        
        for T in temps:
            # Create temporary physics object at this temperature
            physics_temp = SemiconductorPhysics(temperature=T)
            Vbr = physics_temp.breakdown_voltage()
            Vbr_values.append(Vbr)
        
        return {
            'temperatures': temps,  # °C
            'breakdown_voltages': np.array(Vbr_values),  # V
            'temp_coefficient': np.mean(np.gradient(Vbr_values, temps))  # V/°C
        }


