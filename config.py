"""
Configuration file for PV Module Shading Visualization
Physical constants and default parameters
"""

import numpy as np

# Physical constants
BOLTZMANN = 1.380649e-23  # J/K
ELEMENTARY_CHARGE = 1.602176634e-19  # C
STEFAN_BOLTZMANN = 5.670374419e-8  # W/(m²·K⁴)

# Thermal voltage at 25°C
VT_REF = 0.025693  # V (kT/q at 298.15 K)

# Single solar cell parameters
CELL_PARAMS = {
    'Iph_ref': 10.0,      # A, photocurrent at 1000 W/m², 25°C
    'Is': 1e-9,           # A, reverse saturation current
    'n': 1.3,             # Ideality factor
    'Rs': 0.005,          # Ω, series resistance
    'Rsh': 500,           # Ω, shunt resistance (parallel)
    'Vbr_min': 10,        # V, minimum breakdown voltage
    'Vbr_max': 20,        # V, maximum breakdown voltage
    'Vbr_typical': 12,    # V, typical for calculations
    'alpha_Isc': 0.0005,  # A/°C, temperature coefficient for Isc
    'beta_Voc': -0.0023,  # V/°C, temperature coefficient for Voc
    'Voc_ref': 0.65,      # V, open circuit voltage at STC
    'area': 0.02,         # m², approximate area of half-cell
}

# Bypass diode parameters (Schottky)
BYPASS_DIODE = {
    'Vf': 0.4,                  # V, forward voltage drop
    'cells_per_string': 36,     # Number of half-cells per substring
    'Is_diode': 1e-6,          # A, diode saturation current
    'n_diode': 1.05,           # Diode ideality factor
}

# Module structure
MODULE_STRUCTURE = {
    'total_cells': 108,         # Total half-cells in module
    'num_strings': 3,           # Number of substrings
    'bypass_diodes': 3,         # Number of bypass diodes
    'cells_per_string': 36,     # Half-cells per substring
}

# Standard Test Conditions (STC)
STC = {
    'irradiance': 1000,    # W/m²
    'temperature': 25,     # °C
    'air_mass': 1.5,       # AM 1.5 spectrum
}

# Semiconductor physics parameters
SEMICONDUCTOR_PARAMS = {
    'epsilon_si': 11.68 * 8.854187817e-12,  # F/m, Si permittivity
    'Eg': 1.12,                              # eV, bandgap energy at 300K
    'ni': 1e10,                              # cm^-3, intrinsic carrier concentration
    'Na': 1e16,                              # cm^-3, acceptor doping (p-side)
    'Nd': 1e19,                              # cm^-3, donor doping (n-side)
    'mu_n': 1350,                            # cm²/(V·s), electron mobility
    'mu_p': 450,                             # cm²/(V·s), hole mobility
    'alpha_n': 7e-6,                         # cm^-1, electron ionization rate coefficient
    'alpha_p': 5e-6,                         # cm^-1, hole ionization rate coefficient
}

# Visualization defaults
VIZ_PARAMS = {
    'voltage_range': (-15, 50),      # V, for I-V curves
    'voltage_points': 500,           # Number of points for I-V curve
    'color_scale_pos': 'Greens',     # Colorscale for positive voltages
    'color_scale_neg': 'Reds',       # Colorscale for negative voltages (reverse bias)
    'hotspot_threshold': 5.0,        # W, power dissipation threshold for hot-spot
}

# Application settings
APP_CONFIG = {
    'debug': True,
    'host': '127.0.0.1',
    'port': 8050,
    'title': 'PV Module Shading Physics Visualization',
}


