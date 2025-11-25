#!/usr/bin/env python
"""
Performance Test: LUT vs. Original scipy.optimize

Measures the speedup from using Look-up Tables
"""

import time
import numpy as np
from physics.module_model import PVModule
from physics.cell_model import LUTSolarCell
from physics.lut_cache import initialize_lut


print("="*70)
print("LUT PERFORMANCE TEST")
print("="*70)
print()

# Initialize LUT system
print("Initializing LUT system...")
lut_data, interpolator = initialize_lut(cache_filepath='cache/cell_lut.npz')
LUTSolarCell.set_lut_interpolator(interpolator)
print()

# Test scenarios
scenarios = [
    ('No Shading', None),
    ('Single Cell Shaded', {'string_0': {18: 1.0}}),
    ('Multiple Cells Shaded', {'string_0': {10: 0.5, 18: 1.0, 25: 0.8}}),
]

results = []

for scenario_name, shading_config in scenarios:
    print(f"Testing: {scenario_name}")
    print("-"*70)
    
    # Test WITH LUT (fast)
    print("  With LUT...")
    start = time.time()
    module_lut = PVModule(
        irradiance=1000,
        temperature=25,
        shading_config=shading_config,
        use_lut=True
    )
    mpp_lut = module_lut.find_mpp(fast=True)
    time_lut = time.time() - start
    
    # Test WITHOUT LUT (slow)
    print("  Without LUT (scipy.optimize)...")
    start = time.time()
    module_orig = PVModule(
        irradiance=1000,
        temperature=25,
        shading_config=shading_config,
        use_lut=False
    )
    mpp_orig = module_orig.find_mpp(fast=True)
    time_orig = time.time() - start
    
    # Calculate speedup
    speedup = time_orig / time_lut if time_lut > 0 else 0
    
    # Compare results
    voltage_diff = abs(mpp_lut['voltage'] - mpp_orig['voltage'])
    power_diff = abs(mpp_lut['power'] - mpp_orig['power'])
    
    results.append({
        'scenario': scenario_name,
        'time_lut': time_lut,
        'time_orig': time_orig,
        'speedup': speedup,
        'voltage_lut': mpp_lut['voltage'],
        'voltage_orig': mpp_orig['voltage'],
        'voltage_diff': voltage_diff,
        'power_lut': mpp_lut['power'],
        'power_orig': mpp_orig['power'],
        'power_diff': power_diff
    })
    
    print(f"    LUT:      {time_lut:.3f}s -> {mpp_lut['power']:.1f}W")
    print(f"    Original: {time_orig:.3f}s -> {mpp_orig['power']:.1f}W")
    print(f"    Speedup:  {speedup:.1f}x")
    print(f"    Accuracy: dV={voltage_diff:.3f}V, dP={power_diff:.1f}W")
    print()

# Summary
print("="*70)
print("SUMMARY")
print("="*70)
print()

avg_time_lut = np.mean([r['time_lut'] for r in results])
avg_time_orig = np.mean([r['time_orig'] for r in results])
avg_speedup = np.mean([r['speedup'] for r in results])
max_voltage_diff = max([r['voltage_diff'] for r in results])
max_power_diff = max([r['power_diff'] for r in results])

print(f"Average Time (LUT):       {avg_time_lut:.3f}s")
print(f"Average Time (Original):  {avg_time_orig:.3f}s")
print(f"Average Speedup:          {avg_speedup:.1f}x")
print()
print(f"Max Voltage Difference:   {max_voltage_diff:.3f}V (<{max_voltage_diff/41.58*100:.2f}% of V_oc)")
print(f"Max Power Difference:     {max_power_diff:.1f}W (<{max_power_diff/445*100:.2f}% of P_mpp)")
print()

# Performance rating
if avg_time_lut < 0.5:
    rating = "EXCELLENT [+++]"
elif avg_time_lut < 1.0:
    rating = "GOOD [++]"
elif avg_time_lut < 2.0:
    rating = "ACCEPTABLE [+]"
else:
    rating = "NEEDS IMPROVEMENT [!]"

print(f"Performance Rating: {rating}")
print()

# Accuracy check
if max_voltage_diff < 0.1 and max_power_diff < 5.0:
    print("Accuracy: EXCELLENT [OK] (errors < 0.1V, 5W)")
elif max_voltage_diff < 0.5 and max_power_diff < 20.0:
    print("Accuracy: GOOD [OK] (errors < 0.5V, 20W)")
else:
    print("Accuracy: NEEDS REVIEW [!] (errors too large)")

print()
print("="*70)
print()

# Expected callback time
print("Estimated Callback Performance:")
print(f"  Single MPP search:       ~{avg_time_lut:.2f}s")
print(f"  Full voltage distribution callback: ~{avg_time_lut * 2:.2f}s")
print(f"    (includes circuit diagram, heatmaps, hotspot analysis)")
print()

if avg_time_lut < 0.5:
    print("[OK] Target achieved: <0.5s per callback!")
else:
    print(f"[!] Still needs optimization (target: <0.5s, actual: ~{avg_time_lut:.2f}s)")

print()
print("="*70)

