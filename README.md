# Fault Geological Reactivation Analysis

A comprehensive Python script for analyzing fault geological reactivation based on stress calculations, Coulomb failure criteria, and Mohr circle analysis.

## Features

This script provides a complete fault reactivation analysis including:

### 1. Data Processing
- CSV file reading with automatic column detection
- Sample data generation for demonstration
- Pressure parameter management (initial, injected, depleted conditions)

### 2. Stress Calculations
- Vertical stress (Sv) calculation
- Minimum and maximum horizontal stress (Sh_min, Sh_max)
- Principal stress calculations (S1, S2, S3)
- Shear stress calculations using Mohr-Coulomb criterion
- Stress tensor calculations for each fault

### 3. Advanced Analysis
- Rotation matrix calculations for fault orientation
- Coulomb failure stress (CFS) calculations
- Maximum allowable pressure increase calculations
- Critical depletion pressure analysis
- Stability analysis for various friction angles

### 4. Comprehensive Plotting (30+ plots)
- 2D fault map with fault IDs
- 2D and 3D Mohr circles with scatter plots
- Coulomb failure stress analysis
- Effective normal vs shear stress plots
- Shear stress vs fault dip analysis
- 3D fault plane stress analysis
- Stability analysis plots
- Pressure depletion analysis
- Critical friction angle analysis
- Stress path analysis
- Reactivation status mapping

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```python
from fault_reactivation_analysis import FaultReactivationAnalysis

# Initialize analysis (will create sample data if CSV not found)
analysis = FaultReactivationAnalysis("your_fault_data.csv")

# Run comprehensive analysis
analysis.run_comprehensive_analysis()
```

### Custom CSV Data Format
Your CSV file should contain the following columns:
- `Fault_ID`: Unique identifier for each fault
- `X_coord`: X coordinate (meters)
- `Y_coord`: Y coordinate (meters)
- `Depth`: Depth (meters)
- `Dip`: Fault dip angle (degrees)
- `Strike`: Fault strike angle (degrees)
- `Length`: Fault length (meters)
- `Width`: Fault width (meters)
- `Friction_Angle`: Friction angle (degrees)
- `Cohesion`: Cohesion value (Pa)

### Parameters
The script uses the following default parameters:
- Final pore pressure: 50 MPa at 2790 m depth
- Depleted pore pressure: 10 MPa at 3800 m and 3170 m depths
- Friction factor (μ): 0.6
- Rock density: 2650 kg/m³
- Poisson's ratio: 0.25
- Biot's coefficient: 0.8

## Output

The script generates:
1. **30+ high-quality plots** saved as PNG files
2. **Console output** with maximum allowable pressure increases for each fault
3. **Comprehensive analysis** covering all aspects of fault reactivation

### Key Output Files
- `fault_map_2d_topview.png`: 2D fault map
- `coulomb_failure_stress_2d.png`: CFS analysis
- `combined_mohr_circle.png`: Mohr circle analysis
- `3d_mohr_circle.png`: 3D stress visualization
- `fault_map_reactivation_status.png`: Reactivation status map
- And many more specialized analysis plots

## Analysis Components

### 1. Stress Analysis
- Vertical stress calculation using lithostatic pressure
- Horizontal stress calculation using uniaxial strain model
- Principal stress determination
- Effective stress calculations

### 2. Fault Analysis
- Fault orientation using strike and dip
- Stress tensor transformation
- Normal and shear stress on fault planes
- Coulomb failure criterion application

### 3. Pressure Analysis
- Initial reservoir pressure conditions
- Injected pressure scenarios
- Depleted pressure analysis
- Critical pressure calculations

### 4. Stability Assessment
- Coulomb failure stress calculations
- Stability factor determination
- Critical friction angle analysis
- Reactivation probability assessment

## Customization

You can modify the following parameters in the script:
- Rock properties (density, Poisson's ratio)
- Fluid properties
- Friction coefficients
- Pressure conditions
- Analysis depth ranges

## Example Results

The script provides:
- **Fault reactivation status** for each fault under different conditions
- **Maximum allowable pressure increases** before reactivation
- **Critical depletion pressures** for fault reactivation
- **Stability maps** showing safe operating conditions
- **3D visualizations** of stress states and Mohr circles

## Technical Details

- **Stress Units**: All stresses calculated in Pa, displayed in MPa/kPa
- **Coordinate System**: Right-handed coordinate system
- **Fault Orientation**: Strike and dip following geological conventions
- **Failure Criterion**: Mohr-Coulomb failure criterion
- **Plotting**: High-resolution plots (300 DPI) with professional styling

## Requirements

- Python 3.7+
- pandas
- numpy
- matplotlib
- seaborn
- scipy

## License

This script is provided for educational and research purposes. Please cite appropriately if used in academic work.

## Contact

For questions or improvements, please refer to the code documentation and comments.