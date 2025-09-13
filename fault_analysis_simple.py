#!/usr/bin/env python3
"""
Simplified Fault Geological Reactivation Analysis Script
This version uses only built-in Python libraries for demonstration
"""

import csv
import math
import random
from typing import List, Dict, Tuple

class SimpleFaultAnalysis:
    """
    Simplified fault reactivation analysis using only built-in Python libraries
    """
    
    def __init__(self, csv_file_path: str = None):
        """
        Initialize the analysis
        """
        self.csv_file_path = csv_file_path
        self.faults = []
        self.pressure_data = []
        
        # Analysis parameters
        self.rock_density = 2650  # kg/m³
        self.fluid_density = 1000  # kg/m³
        self.poisson_ratio = 0.25
        self.biot_coeff = 0.8
        self.g = 9.81  # m/s²
        self.mu = 0.6  # Friction factor
        self.cohesion = 0  # Pa
        
        # Load or create data
        if csv_file_path:
            self.load_csv_data()
        else:
            self.create_sample_data()
        
        self.setup_pressure_data()
        
    def create_sample_data(self):
        """
        Create sample fault data for demonstration
        """
        random.seed(42)
        n_faults = 20
        
        for i in range(n_faults):
            fault = {
                'Fault_ID': f'Fault_{i+1:02d}',
                'X_coord': random.uniform(0, 1000),
                'Y_coord': random.uniform(0, 1000),
                'Depth': random.uniform(2000, 4000),
                'Dip': random.uniform(10, 80),
                'Strike': random.uniform(0, 360),
                'Length': random.uniform(100, 2000),
                'Width': random.uniform(50, 500),
                'Friction_Angle': random.uniform(20, 45),
                'Cohesion': random.uniform(0, 50)
            }
            self.faults.append(fault)
        
        print(f"Created sample data with {len(self.faults)} faults")
    
    def load_csv_data(self):
        """
        Load data from CSV file
        """
        try:
            with open(self.csv_file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Convert numeric fields
                    for key in ['X_coord', 'Y_coord', 'Depth', 'Dip', 'Strike', 
                               'Length', 'Width', 'Friction_Angle', 'Cohesion']:
                        if key in row:
                            row[key] = float(row[key])
                    self.faults.append(row)
            print(f"Loaded {len(self.faults)} faults from {self.csv_file_path}")
        except FileNotFoundError:
            print(f"CSV file not found: {self.csv_file_path}")
            print("Creating sample data instead...")
            self.create_sample_data()
    
    def setup_pressure_data(self):
        """
        Setup pressure parameters
        """
        self.pressure_data = [
            {'Depth': 2790, 'Final_Pore_Pressure': 50, 'Depleted_Pore_Pressure': 50, 'Initial_Pore_Pressure': 50},
            {'Depth': 3800, 'Final_Pore_Pressure': 10, 'Depleted_Pore_Pressure': 10, 'Initial_Pore_Pressure': 50},
            {'Depth': 3170, 'Final_Pore_Pressure': 10, 'Depleted_Pore_Pressure': 10, 'Initial_Pore_Pressure': 50}
        ]
        print("Pressure parameters set up")
    
    def calculate_vertical_stress(self, depth: float) -> float:
        """
        Calculate vertical stress (Sv) at given depth
        """
        return self.rock_density * self.g * depth
    
    def calculate_horizontal_stresses(self, depth: float, pore_pressure: float) -> Tuple[float, float]:
        """
        Calculate minimum and maximum horizontal stresses
        """
        Sv = self.calculate_vertical_stress(depth)
        Sv_eff = Sv - pore_pressure
        
        # Minimum horizontal stress (uniaxial strain model)
        Sh_min = (self.poisson_ratio / (1 - self.poisson_ratio)) * Sv_eff + pore_pressure
        
        # Maximum horizontal stress
        Sh_max = 1.2 * Sh_min
        
        return Sh_min, Sh_max
    
    def calculate_principal_stresses(self, depth: float, pore_pressure: float) -> Tuple[float, float, float]:
        """
        Calculate principal stresses S1, S2, S3
        """
        Sv = self.calculate_vertical_stress(depth)
        Sh_min, Sh_max = self.calculate_horizontal_stresses(depth, pore_pressure)
        
        S1 = Sv  # Maximum principal stress (vertical)
        S2 = Sh_max  # Intermediate principal stress
        S3 = Sh_min  # Minimum principal stress
        
        return S1, S2, S3
    
    def calculate_shear_stress(self, normal_stress: float, friction_angle: float) -> float:
        """
        Calculate shear stress using Mohr-Coulomb criterion
        """
        friction_angle_rad = math.radians(friction_angle)
        return normal_stress * math.tan(friction_angle_rad) + self.cohesion
    
    def calculate_coulomb_failure_stress(self, normal_stress: float, shear_stress: float, friction_angle: float) -> float:
        """
        Calculate Coulomb failure stress
        """
        friction_angle_rad = math.radians(friction_angle)
        return shear_stress - (normal_stress * math.tan(friction_angle_rad) + self.cohesion)
    
    def calculate_maximum_allowable_pressure(self, depth: float, initial_pore_pressure: float, friction_angle: float) -> float:
        """
        Calculate maximum allowable pressure increase without fault reactivation
        """
        S1, S2, S3 = self.calculate_principal_stresses(depth, initial_pore_pressure)
        
        S1_eff = S1 - initial_pore_pressure
        S3_eff = S3 - initial_pore_pressure
        
        friction_angle_rad = math.radians(friction_angle)
        max_pressure_increase = (S1_eff - S3_eff) / (2 * math.tan(friction_angle_rad + math.pi/4))
        
        return max_pressure_increase
    
    def analyze_fault_reactivation(self):
        """
        Perform comprehensive fault reactivation analysis
        """
        print("\n" + "="*80)
        print("FAULT REACTIVATION ANALYSIS RESULTS")
        print("="*80)
        
        # Analyze each fault
        for fault in self.faults:
            fault_id = fault['Fault_ID']
            depth = fault['Depth']
            friction_angle = fault['Friction_Angle']
            
            print(f"\nFault ID: {fault_id}")
            print(f"  Depth: {depth:.1f} m")
            print(f"  Friction Angle: {friction_angle:.1f}°")
            print(f"  Dip: {fault['Dip']:.1f}°")
            print(f"  Strike: {fault['Strike']:.1f}°")
            
            # Calculate stresses for different conditions
            conditions = [
                ('Initial', 50 * 1000),
                ('Injected', 50 * 1000),
                ('Depleted', 10 * 1000)
            ]
            
            for condition_name, pore_pressure in conditions:
                S1, S2, S3 = self.calculate_principal_stresses(depth, pore_pressure)
                
                normal_stress = (S1 + S3) / 2
                shear_stress = (S1 - S3) / 2
                
                cfs = self.calculate_coulomb_failure_stress(normal_stress, shear_stress, friction_angle)
                
                print(f"  {condition_name} Condition:")
                print(f"    Principal Stresses: S1={S1/1000:.1f} MPa, S2={S2/1000:.1f} MPa, S3={S3/1000:.1f} MPa")
                print(f"    Normal Stress: {normal_stress/1000:.1f} MPa")
                print(f"    Shear Stress: {shear_stress/1000:.1f} MPa")
                print(f"    Coulomb Failure Stress: {cfs/1000:.1f} kPa")
                
                if cfs > 0:
                    print(f"    Status: REACTIVATED ⚠️")
                else:
                    print(f"    Status: STABLE ✓")
            
            # Calculate maximum allowable pressure increase
            initial_pore_pressure = 50 * 1000
            max_pressure = self.calculate_maximum_allowable_pressure(depth, initial_pore_pressure, friction_angle)
            print(f"  Max Allowable Pressure Increase: {max_pressure/1000:.2f} MPa")
            
            print("-" * 60)
    
    def print_summary_statistics(self):
        """
        Print summary statistics
        """
        print("\n" + "="*80)
        print("SUMMARY STATISTICS")
        print("="*80)
        
        depths = [fault['Depth'] for fault in self.faults]
        friction_angles = [fault['Friction_Angle'] for fault in self.faults]
        dips = [fault['Dip'] for fault in self.faults]
        
        print(f"Total Number of Faults: {len(self.faults)}")
        print(f"Depth Range: {min(depths):.1f} - {max(depths):.1f} m")
        print(f"Average Depth: {sum(depths)/len(depths):.1f} m")
        print(f"Friction Angle Range: {min(friction_angles):.1f}° - {max(friction_angles):.1f}°")
        print(f"Average Friction Angle: {sum(friction_angles)/len(friction_angles):.1f}°")
        print(f"Dip Range: {min(dips):.1f}° - {max(dips):.1f}°")
        print(f"Average Dip: {sum(dips)/len(dips):.1f}°")
        
        # Count reactivated faults in depleted condition
        reactivated_count = 0
        for fault in self.faults:
            depth = fault['Depth']
            friction_angle = fault['Friction_Angle']
            pore_pressure = 10 * 1000  # Depleted condition
            
            S1, S2, S3 = self.calculate_principal_stresses(depth, pore_pressure)
            normal_stress = (S1 + S3) / 2
            shear_stress = (S1 - S3) / 2
            cfs = self.calculate_coulomb_failure_stress(normal_stress, shear_stress, friction_angle)
            
            if cfs > 0:
                reactivated_count += 1
        
        print(f"Reactivated Faults (Depleted): {reactivated_count}/{len(self.faults)} ({reactivated_count/len(self.faults)*100:.1f}%)")
        
        print("="*80)
    
    def export_results_to_csv(self, filename: str = "fault_analysis_results.csv"):
        """
        Export analysis results to CSV file
        """
        with open(filename, 'w', newline='') as file:
            fieldnames = ['Fault_ID', 'Depth', 'Friction_Angle', 'Dip', 'Strike',
                         'Initial_CFS_kPa', 'Injected_CFS_kPa', 'Depleted_CFS_kPa',
                         'Max_Pressure_Increase_MPa', 'Status_Initial', 'Status_Injected', 'Status_Depleted']
            
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            
            for fault in self.faults:
                fault_id = fault['Fault_ID']
                depth = fault['Depth']
                friction_angle = fault['Friction_Angle']
                
                row = {
                    'Fault_ID': fault_id,
                    'Depth': depth,
                    'Friction_Angle': friction_angle,
                    'Dip': fault['Dip'],
                    'Strike': fault['Strike']
                }
                
                # Calculate CFS for each condition
                conditions = [
                    ('Initial', 50 * 1000),
                    ('Injected', 50 * 1000),
                    ('Depleted', 10 * 1000)
                ]
                
                for condition_name, pore_pressure in conditions:
                    S1, S2, S3 = self.calculate_principal_stresses(depth, pore_pressure)
                    normal_stress = (S1 + S3) / 2
                    shear_stress = (S1 - S3) / 2
                    cfs = self.calculate_coulomb_failure_stress(normal_stress, shear_stress, friction_angle)
                    
                    row[f'{condition_name}_CFS_kPa'] = cfs / 1000
                    row[f'Status_{condition_name}'] = 'Reactivated' if cfs > 0 else 'Stable'
                
                # Calculate maximum allowable pressure increase
                initial_pore_pressure = 50 * 1000
                max_pressure = self.calculate_maximum_allowable_pressure(depth, initial_pore_pressure, friction_angle)
                row['Max_Pressure_Increase_MPa'] = max_pressure / 1000
                
                writer.writerow(row)
        
        print(f"Results exported to {filename}")

def main():
    """
    Main function to run the analysis
    """
    print("Fault Geological Reactivation Analysis")
    print("="*50)
    
    # Initialize analysis
    analysis = SimpleFaultAnalysis("fault_data.csv")
    
    # Run analysis
    analysis.analyze_fault_reactivation()
    analysis.print_summary_statistics()
    analysis.export_results_to_csv()
    
    print("\nAnalysis completed successfully!")
    print("Results have been exported to 'fault_analysis_results.csv'")

if __name__ == "__main__":
    main()