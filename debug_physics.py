"""
Debug script to test the physics calculations
"""

from physics import SolarCell, CellString, PVModule
import numpy as np

print("=" * 60)
print("PHYSICS DEBUG TEST")
print("=" * 60)

# Test 1: Single cell without shading
print("\n1. Single unshaded cell:")
cell = SolarCell(irradiance=1000, temperature=25, shading_factor=0.0)

print(f"   Iph = {cell.Iph:.3f} A")
print(f"   Testing current at different voltages:")
for v in [0.0, 0.3, 0.5, 0.6, 0.7]:
    i = cell.current(v)
    print(f"   V = {v:.2f} V  ->  I = {i:.3f} A")

print(f"\n   Finding operating points:")
for target_i in [9.0, 7.0, 5.0, 3.0, 1.0]:
    v = cell.find_operating_point(target_i)
    i_check = cell.current(v)
    print(f"   Target I = {target_i:.1f} A  ->  V = {v:.3f} V  (check: I = {i_check:.3f} A)")

# Test 2: Single shaded cell
print("\n2. Single shaded cell (100%):")
shaded_cell = SolarCell(irradiance=1000, temperature=25, shading_factor=1.0)
print(f"   Iph = {shaded_cell.Iph:.3f} A (should be ~0)")

v_at_5a = shaded_cell.find_operating_point(5.0)
print(f"   At I = 5.0 A: V = {v_at_5a:.3f} V (should be negative!)")

# Test 3: String without shading
print("\n3. String (36 cells) without shading:")
string = CellString(num_cells=36, irradiance=1000, temperature=25, shading_pattern=None)

result = string.string_voltage_at_current(5.0)
print(f"   String voltage: {result['voltage']:.2f} V")
print(f"   Bypass active: {result['bypass_active']}")
print(f"   First 3 cell voltages: {result['cell_voltages'][:3]}")

# Test 4: Module without shading
print("\n4. Complete module (108 cells, no shading):")
module = PVModule(irradiance=1000, temperature=25, shading_config=None)

result = module.module_voltage_at_current(5.0)
print(f"   Module voltage: {result['voltage']:.2f} V")
print(f"   Module power: {result['total_power']:.2f} W")
print(f"   Bypass states: {result['bypass_states']}")
print(f"   Number of bypassed strings: {result['num_bypassed_strings']}")

# Test 5: MPP
print("\n5. Module MPP (no shading):")
mpp = module.find_mpp()
print(f"   V_mpp: {mpp['voltage']:.2f} V")
print(f"   I_mpp: {mpp['current']:.2f} A")
print(f"   P_mpp: {mpp['power']:.2f} W")

print("\n" + "=" * 60)
print("Test completed!")
print("=" * 60)

