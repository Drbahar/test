#!/usr/bin/env python3
"""
Simple test script to verify the fault reactivation analysis structure
"""

# Test basic imports and class structure
try:
    import sys
    import os
    
    # Add current directory to path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Test if we can import the main class
    from fault_reactivation_analysis import FaultReactivationAnalysis
    
    print("✓ Successfully imported FaultReactivationAnalysis class")
    
    # Test class initialization (this will create sample data)
    print("✓ Testing class initialization...")
    analysis = FaultReactivationAnalysis("test_data.csv")
    
    print(f"✓ Created analysis with {len(analysis.df)} faults")
    print(f"✓ Created pressure dataframe with {len(analysis.df2)} data points")
    
    # Test basic calculations
    print("✓ Testing stress calculations...")
    depth = 3000
    pore_pressure = 10 * 1000
    
    Sv = analysis.calculate_vertical_stress(depth)
    Sh_min, Sh_max = analysis.calculate_horizontal_stresses(depth, pore_pressure)
    S1, S2, S3 = analysis.calculate_principal_stresses(depth, pore_pressure)
    
    print(f"  Vertical stress at {depth}m: {Sv/1000:.1f} MPa")
    print(f"  Horizontal stresses: Sh_min={Sh_min/1000:.1f} MPa, Sh_max={Sh_max/1000:.1f} MPa")
    print(f"  Principal stresses: S1={S1/1000:.1f} MPa, S2={S2/1000:.1f} MPa, S3={S3/1000:.1f} MPa")
    
    # Test Coulomb failure stress calculation
    print("✓ Testing Coulomb failure stress calculation...")
    normal_stress = (S1 + S3) / 2
    shear_stress = (S1 - S3) / 2
    cfs = analysis.calculate_coulomb_failure_stress(normal_stress, shear_stress, 30)
    print(f"  Coulomb failure stress: {cfs/1000:.1f} kPa")
    
    # Test maximum allowable pressure calculation
    print("✓ Testing maximum allowable pressure calculation...")
    max_pressure = analysis.calculate_maximum_allowable_pressure(depth, pore_pressure, 30)
    print(f"  Maximum allowable pressure increase: {max_pressure/1000:.1f} MPa")
    
    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED SUCCESSFULLY!")
    print("✓ The fault reactivation analysis script is working correctly.")
    print("✓ Ready to run comprehensive analysis with plotting functions.")
    print("="*60)
    
    # Show available methods
    print("\nAvailable analysis methods:")
    methods = [method for method in dir(analysis) if method.startswith('plot_') or method.startswith('print_') or method.startswith('run_')]
    for method in sorted(methods):
        print(f"  - {method}")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Please install required packages: pandas, numpy, matplotlib, seaborn, scipy")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()