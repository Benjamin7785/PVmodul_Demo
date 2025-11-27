"""
Quick test script to verify installation and basic functionality
Run this after installing requirements.txt
"""

import sys

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import dash
        print(f"✓ Dash {dash.__version__}")
    except ImportError as e:
        print(f"✗ Dash import failed: {e}")
        return False
    
    try:
        import plotly
        print(f"✓ Plotly {plotly.__version__}")
    except ImportError as e:
        print(f"✗ Plotly import failed: {e}")
        return False
    
    try:
        import numpy
        print(f"✓ NumPy {numpy.__version__}")
    except ImportError as e:
        print(f"✗ NumPy import failed: {e}")
        return False
    
    try:
        import scipy
        print(f"✓ SciPy {scipy.__version__}")
    except ImportError as e:
        print(f"✗ SciPy import failed: {e}")
        return False
    
    try:
        import pandas
        print(f"✓ Pandas {pandas.__version__}")
    except ImportError as e:
        print(f"✗ Pandas import failed: {e}")
        return False
    
    try:
        import dash_bootstrap_components
        print(f"✓ Dash Bootstrap Components")
    except ImportError as e:
        print(f"✗ Dash Bootstrap Components import failed: {e}")
        return False
    
    return True


def test_physics_models():
    """Test basic physics model functionality"""
    print("\nTesting physics models...")
    
    try:
        from physics import SolarCell, CellString, PVModule
        
        # Test single cell
        cell = SolarCell(irradiance=1000, temperature=25, shading_factor=0.0)
        Isc = cell.get_Isc()
        Voc = cell.get_Voc()
        print(f"✓ SolarCell: Isc={Isc:.2f}A, Voc={Voc:.3f}V")
        
        # Test string
        string = CellString(num_cells=36, irradiance=1000, temperature=25)
        string_data = string.iv_curve()
        print(f"✓ CellString: {len(string_data['currents'])} points")
        
        # Test module
        module = PVModule(irradiance=1000, temperature=25)
        mpp = module.find_mpp()
        print(f"✓ PVModule: MPP={mpp['power']:.2f}W at {mpp['voltage']:.2f}V")
        
        return True
    except Exception as e:
        print(f"✗ Physics models test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visualizations():
    """Test visualization functions"""
    print("\nTesting visualizations...")
    
    try:
        from visualizations.iv_plotter import plot_iv_curve
        import numpy as np
        
        # Create simple test data
        v = np.linspace(0, 40, 100)
        i = np.linspace(10, 0, 100)
        
        fig = plot_iv_curve(v, i, title="Test")
        print("✓ IV plotter works")
        
        return True
    except Exception as e:
        print(f"✗ Visualization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("PV Module Shading Visualization - Installation Test")
    print("=" * 60)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        print("\n⚠️  Some imports failed. Please run: pip install -r requirements.txt")
        all_passed = False
    
    # Test physics models
    if not test_physics_models():
        print("\n⚠️  Physics models test failed.")
        all_passed = False
    
    # Test visualizations
    if not test_visualizations():
        print("\n⚠️  Visualization test failed.")
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! You can now run: python app.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())


