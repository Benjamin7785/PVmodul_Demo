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

# Single solar cell parameters (based on Luxor Eco Line HJT GG, M108, 445 Wp)
# Source: https://www.luxor.solar/files/luxor/download/datasheets/LX_EL_HJT_GG_BW_EST_M108_430-450W_182_EN.pdf
# Module specs at STC: Pmpp=445W, Vmpp=33.89V, Impp=13.14A, Isc=13.98A, Voc=41.58V, η=23.12%
CELL_PARAMS = {
    'Iph_ref': 13.98,     # A, photocurrent at 1000 W/m², 25°C (= Isc from datasheet)
    'Is': 8e-11,          # A, reverse saturation current (HJT: lower, calibrated to Voc)
    'n': 0.92,            # Ideality factor (HJT: FINE-TUNED for FF = 0.764)
    'Rs': 0.0008,         # Ω, series resistance (HJT: ULTRA-LOW for maximum Impp)
    'Rsh': 5000,          # Ω, shunt resistance (HJT: VERY HIGH quality)
    # Breakdown voltage (HJT-specific: higher than p-Type due to n-Type and better quality)
    'Vbr_min': 18,        # V, minimum breakdown voltage (HJT: higher than standard)
    'Vbr_max': 28,        # V, maximum breakdown voltage (HJT: can be very high)
    'Vbr_typical': 22,    # V, typical for HJT calculations (conservative: 20-25V range)
    # Temperature coefficients (typical for HJT technology)
    'alpha_Isc': 0.000140, # A/°C, temp coeff for Isc (+0.01%/K → +0.14 mA/°C for 13.98A)
    'beta_Voc': -0.001000, # V/°C, temp coeff for Voc per module (-0.24%/K → -100 mV/°C for 41.58V)
    'beta_Voc_cell': -0.000926, # V/°C, temp coeff per cell (-100mV/°C / 108 = -0.926 mV/°C)
    'gamma_Pmpp': -0.0026,  # /°C, temp coeff for power (-0.26%/K, typical HJT)
    'Voc_ref': 0.385,     # V, open circuit voltage at STC (41.58V / 108 cells = 0.385V)
    'Vmpp_ref': 0.314,    # V, voltage at MPP (33.89V / 108 cells = 0.314V)
    'Impp_ref': 13.14,    # A, current at MPP per cell (series → same for all)
    'Isc_ref': 13.98,     # A, short circuit current per cell (series → same for all)
    'area': 0.0244,       # m², approximate area of half-cell (M10: 182mm wafer → half ≈156×78mm)
    'FF': 0.764,          # Fill Factor = (Vmpp * Impp) / (Voc * Isc) = 0.764
}

# Bypass diode parameters (Schottky)
BYPASS_DIODE = {
    'Vf': 0.4,                  # V, forward voltage drop
    'cells_per_string': 36,     # Number of half-cells per substring
    'Is_diode': 1e-6,          # A, diode saturation current
    'n_diode': 1.05,           # Diode ideality factor
}

# Module structure (Luxor Eco Line HJT GG, M108, 445 Wp)
# Source: https://www.luxor.solar/files/luxor/download/datasheets/LX_EL_HJT_GG_BW_EST_M108_430-450W_182_EN.pdf
MODULE_STRUCTURE = {
    'total_cells': 108,         # Total half-cells in module
    'num_strings': 3,           # Number of substrings
    'bypass_diodes': 3,         # Number of bypass diodes (3× Schottky)
    'cells_per_string': 36,     # Half-cells per substring (108 / 3 = 36)
    'module_name': 'Luxor Eco Line HJT Glass-Glass Bifacial M108',
    'module_type': 'LX-445M/182-108+ GG',
    'technology': 'N-Type Heterojunction (HJT)',
    'module_specs_stc': {
        # STC (Standard Test Conditions): 1000 W/m², 25°C, AM 1.5
        'Pmpp': 445,            # W, rated power at STC
        'Pmpp_range_to': 451.49, # W, power range upper limit
        'Vmpp': 33.89,          # V, voltage at MPP
        'Impp': 13.14,          # A, current at MPP
        'Voc': 41.58,           # V, open circuit voltage (EXACT from datasheet)
        'Isc': 13.98,           # A, short circuit current (EXACT from datasheet)
        'efficiency': 23.12,    # %, module efficiency (EXACT from datasheet)
        'efficiency_200': 22.58, # %, efficiency at 200 W/m²
    },
    'module_specs_noct': {
        # NOCT: 800 W/m², wind 1m/s, ambient 20°C, cell temp 45±2°C
        'Pmpp': 338.91,         # W, power at NOCT
        'Vmpp': 31.97,          # V, voltage at MPP
        'Impp': 10.60,          # A, current at MPP
        'Voc': 38.42,           # V, open circuit voltage at NOCT
        'Isc': 11.27,           # A, short circuit current at NOCT
    },
    'bifacial': {
        'bifaciality_factor': 0.85,  # 85% ± 3%
        'backside_gain_typical': 66, # W, typical backside power gain
    },
    'dimensions': {
        'length': 1722,         # mm (estimated for M10 module)
        'width': 1134,          # mm (estimated for M10 module)
        'height': 30,           # mm (estimated glass-glass)
        'weight': 22.5,         # kg (estimated for glass-glass)
    },
    'limiting_values': {
        'max_system_voltage': 1500, # V DC
        'operating_temp_min': -40,  # °C
        'operating_temp_max': 85,   # °C
        'max_pressure_load': 5400,  # Pa
        'max_tensile_load': 5400,   # Pa
    }
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


