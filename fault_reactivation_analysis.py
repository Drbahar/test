#!/usr/bin/env python3
"""
Comprehensive Fault Geological Reactivation Analysis Script

This script performs comprehensive fault reactivation analysis including:
- Stress calculations (vertical, horizontal, shear)
- Principal stress analysis
- Coulomb failure stress calculations
- 2D and 3D Mohr circle plotting
- Fault stability analysis
- Pressure depletion analysis

Author: AI Assistant
Date: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from scipy.optimize import fsolve
import warnings
warnings.filterwarnings('ignore')

class FaultReactivationAnalysis:
    """
    Main class for fault reactivation analysis
    """
    
    def __init__(self, csv_file_path):
        """
        Initialize the analysis with CSV data
        
        Parameters:
        -----------
        csv_file_path : str
            Path to the CSV file containing fault data
        """
        self.csv_file_path = csv_file_path
        self.df = None
        self.df2 = None
        self.mu = 0.6  # Friction factor
        self.cohesion = 0  # Cohesion (can be modified)
        
        # Load data
        self.load_data()
        self.setup_parameters()
        
    def load_data(self):
        """
        Load CSV file and create dataframes
        """
        try:
            # Read CSV file
            self.df = pd.read_csv(self.csv_file_path)
            print(f"Data loaded successfully. Shape: {self.df.shape}")
            print(f"Columns: {list(self.df.columns)}")
            
            # Create second dataframe with additional parameters
            self.create_dataframe2()
            
        except FileNotFoundError:
            print(f"CSV file not found: {self.csv_file_path}")
            print("Creating sample data for demonstration...")
            self.create_sample_data()
            
    def create_sample_data(self):
        """
        Create sample fault data for demonstration
        """
        np.random.seed(42)
        n_faults = 20
        
        sample_data = {
            'Fault_ID': [f'Fault_{i+1:02d}' for i in range(n_faults)],
            'X_coord': np.random.uniform(0, 1000, n_faults),
            'Y_coord': np.random.uniform(0, 1000, n_faults),
            'Depth': np.random.uniform(2000, 4000, n_faults),
            'Dip': np.random.uniform(10, 80, n_faults),
            'Strike': np.random.uniform(0, 360, n_faults),
            'Length': np.random.uniform(100, 2000, n_faults),
            'Width': np.random.uniform(50, 500, n_faults),
            'Friction_Angle': np.random.uniform(20, 45, n_faults),
            'Cohesion': np.random.uniform(0, 50, n_faults)
        }
        
        self.df = pd.DataFrame(sample_data)
        print("Sample data created for demonstration")
        self.create_dataframe2()
        
    def create_dataframe2(self):
        """
        Create second dataframe with pressure parameters
        """
        pressure_data = {
            'Depth': [2790, 3800, 3170],
            'Final_Pore_Pressure': [50, 10, 10],
            'Depleted_Pore_Pressure': [50, 10, 10],
            'Initial_Pore_Pressure': [50, 50, 50]
        }
        
        self.df2 = pd.DataFrame(pressure_data)
        print("Pressure parameters dataframe created")
        
    def setup_parameters(self):
        """
        Setup analysis parameters
        """
        # Rock density (kg/m³)
        self.rock_density = 2650
        
        # Fluid density (kg/m³)
        self.fluid_density = 1000
        
        # Poisson's ratio
        self.poisson_ratio = 0.25
        
        # Biot's coefficient
        self.biot_coeff = 0.8
        
        # Gravitational acceleration
        self.g = 9.81
        
        print("Analysis parameters set up")
        
    def calculate_vertical_stress(self, depth):
        """
        Calculate vertical stress (Sv) at given depth
        
        Parameters:
        -----------
        depth : float or array
            Depth in meters
            
        Returns:
        --------
        Sv : float or array
            Vertical stress in Pa
        """
        Sv = self.rock_density * self.g * depth
        return Sv
        
    def calculate_horizontal_stresses(self, depth, pore_pressure):
        """
        Calculate minimum and maximum horizontal stresses
        
        Parameters:
        -----------
        depth : float or array
            Depth in meters
        pore_pressure : float or array
            Pore pressure in Pa
            
        Returns:
        --------
        Sh_min : float or array
            Minimum horizontal stress in Pa
        Sh_max : float or array
            Maximum horizontal stress in Pa
        """
        Sv = self.calculate_vertical_stress(depth)
        
        # Effective vertical stress
        Sv_eff = Sv - pore_pressure
        
        # Minimum horizontal stress (using uniaxial strain model)
        Sh_min = (self.poisson_ratio / (1 - self.poisson_ratio)) * Sv_eff + pore_pressure
        
        # Maximum horizontal stress (typically 1.1-1.3 times Sh_min)
        Sh_max = 1.2 * Sh_min
        
        return Sh_min, Sh_max
        
    def calculate_shear_stress(self, normal_stress, friction_angle):
        """
        Calculate shear stress using Mohr-Coulomb criterion
        
        Parameters:
        -----------
        normal_stress : float or array
            Normal stress on fault plane
        friction_angle : float or array
            Friction angle in degrees
            
        Returns:
        --------
        shear_stress : float or array
            Shear stress in Pa
        """
        friction_angle_rad = np.radians(friction_angle)
        shear_stress = normal_stress * np.tan(friction_angle_rad) + self.cohesion
        return shear_stress
        
    def calculate_principal_stresses(self, depth, pore_pressure):
        """
        Calculate principal stresses S1, S2, S3
        
        Parameters:
        -----------
        depth : float or array
            Depth in meters
        pore_pressure : float or array
            Pore pressure in Pa
            
        Returns:
        --------
        S1, S2, S3 : tuple
            Principal stresses (maximum, intermediate, minimum)
        """
        Sv = self.calculate_vertical_stress(depth)
        Sh_min, Sh_max = self.calculate_horizontal_stresses(depth, pore_pressure)
        
        # Principal stresses (assuming vertical is maximum)
        S1 = Sv  # Maximum principal stress (vertical)
        S2 = Sh_max  # Intermediate principal stress
        S3 = Sh_min  # Minimum principal stress
        
        return S1, S2, S3
        
    def calculate_rotation_matrix(self, strike, dip):
        """
        Calculate rotation matrix for fault orientation
        
        Parameters:
        -----------
        strike : float
            Strike angle in degrees
        dip : float
            Dip angle in degrees
            
        Returns:
        --------
        rotation_matrix : numpy array
            3x3 rotation matrix
        """
        strike_rad = np.radians(strike)
        dip_rad = np.radians(dip)
        
        # Rotation matrix for strike
        R_strike = np.array([
            [np.cos(strike_rad), -np.sin(strike_rad), 0],
            [np.sin(strike_rad), np.cos(strike_rad), 0],
            [0, 0, 1]
        ])
        
        # Rotation matrix for dip
        R_dip = np.array([
            [1, 0, 0],
            [0, np.cos(dip_rad), -np.sin(dip_rad)],
            [0, np.sin(dip_rad), np.cos(dip_rad)]
        ])
        
        # Combined rotation matrix
        rotation_matrix = np.dot(R_dip, R_strike)
        
        return rotation_matrix
        
    def calculate_stress_tensor(self, depth, pore_pressure, strike, dip):
        """
        Calculate stress tensor for each fault
        
        Parameters:
        -----------
        depth : float
            Depth in meters
        pore_pressure : float
            Pore pressure in Pa
        strike : float
            Strike angle in degrees
        dip : float
            Dip angle in degrees
            
        Returns:
        --------
        stress_tensor : numpy array
            3x3 stress tensor
        """
        S1, S2, S3 = self.calculate_principal_stresses(depth, pore_pressure)
        
        # Initial stress tensor in principal stress coordinate system
        stress_tensor_principal = np.array([
            [S1, 0, 0],
            [0, S2, 0],
            [0, 0, S3]
        ])
        
        # Get rotation matrix
        R = self.calculate_rotation_matrix(strike, dip)
        
        # Transform stress tensor to fault coordinate system
        stress_tensor = np.dot(np.dot(R.T, stress_tensor_principal), R)
        
        return stress_tensor
        
    def calculate_coulomb_failure_stress(self, normal_stress, shear_stress, friction_angle):
        """
        Calculate Coulomb failure stress
        
        Parameters:
        -----------
        normal_stress : float or array
            Normal stress on fault plane
        shear_stress : float or array
            Shear stress on fault plane
        friction_angle : float or array
            Friction angle in degrees
            
        Returns:
        --------
        CFS : float or array
            Coulomb failure stress
        """
        friction_angle_rad = np.radians(friction_angle)
        CFS = shear_stress - (normal_stress * np.tan(friction_angle_rad) + self.cohesion)
        return CFS
        
    def calculate_maximum_allowable_pressure(self, depth, initial_pore_pressure, friction_angle):
        """
        Calculate maximum allowable pressure increase without fault reactivation
        
        Parameters:
        -----------
        depth : float
            Depth in meters
        initial_pore_pressure : float
            Initial pore pressure in Pa
        friction_angle : float
            Friction angle in degrees
            
        Returns:
        --------
        max_pressure_increase : float
            Maximum allowable pressure increase in Pa
        """
        # Calculate initial stresses
        S1, S2, S3 = self.calculate_principal_stresses(depth, initial_pore_pressure)
        
        # Calculate effective stresses
        S1_eff = S1 - initial_pore_pressure
        S3_eff = S3 - initial_pore_pressure
        
        # Calculate maximum allowable pressure increase
        friction_angle_rad = np.radians(friction_angle)
        max_pressure_increase = (S1_eff - S3_eff) / (2 * np.tan(friction_angle_rad + np.pi/4))
        
        return max_pressure_increase
        
    def plot_faults_2d_topview(self, save_plot=True):
        """
        Plot faults as straight lines in a 2D top view map with Fault IDs
        
        Parameters:
        -----------
        save_plot : bool
            Whether to save the plot
        """
        plt.figure(figsize=(12, 10))
        
        # Plot each fault as a line
        for idx, row in self.df.iterrows():
            x_start = row['X_coord']
            y_start = row['Y_coord']
            
            # Calculate end point based on strike and length
            strike_rad = np.radians(row['Strike'])
            length = row['Length']
            
            x_end = x_start + length * np.cos(strike_rad)
            y_end = y_start + length * np.sin(strike_rad)
            
            # Plot fault line
            plt.plot([x_start, x_end], [y_start, y_end], 'b-', linewidth=2, alpha=0.7)
            
            # Add fault ID label
            plt.text(x_start, y_start, row['Fault_ID'], fontsize=8, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
        
        plt.xlabel('X Coordinate (m)')
        plt.ylabel('Y Coordinate (m)')
        plt.title('Fault Map - 2D Top View')
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        
        if save_plot:
            plt.savefig('fault_map_2d_topview.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
    def plot_2d_coulomb_failure_stress(self, save_plot=True):
        """
        Plot 2D Coulomb failure stress for each condition
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('2D Coulomb Failure Stress Analysis', fontsize=16)
        
        # Calculate CFS for different conditions
        conditions = ['Initial', 'Injected', 'Depleted']
        colors = ['blue', 'red', 'green']
        
        for i, condition in enumerate(conditions):
            ax = axes[i//2, i%2]
            
            # Calculate CFS for each fault
            cfs_values = []
            depths = []
            
            for idx, row in self.df.iterrows():
                depth = row['Depth']
                friction_angle = row['Friction_Angle']
                
                # Get pore pressure based on condition
                if condition == 'Initial':
                    pore_pressure = 50 * 1000  # Convert to Pa
                elif condition == 'Injected':
                    pore_pressure = 50 * 1000
                else:  # Depleted
                    pore_pressure = 10 * 1000
                
                # Calculate stresses
                S1, S2, S3 = self.calculate_principal_stresses(depth, pore_pressure)
                
                # Calculate normal and shear stress on fault plane
                normal_stress = (S1 + S3) / 2
                shear_stress = (S1 - S3) / 2
                
                # Calculate CFS
                cfs = self.calculate_coulomb_failure_stress(normal_stress, shear_stress, friction_angle)
                
                cfs_values.append(cfs / 1000)  # Convert to kPa
                depths.append(depth)
            
            # Plot CFS vs depth
            scatter = ax.scatter(depths, cfs_values, c=cfs_values, cmap='RdYlBu_r', 
                               s=100, alpha=0.7, edgecolors='black')
            ax.set_xlabel('Depth (m)')
            ax.set_ylabel('Coulomb Failure Stress (kPa)')
            ax.set_title(f'CFS - {condition} Condition')
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
            
            # Add colorbar
            plt.colorbar(scatter, ax=ax, label='CFS (kPa)')
        
        # Plot combined CFS comparison
        ax = axes[1, 1]
        for i, condition in enumerate(conditions):
            cfs_values = []
            depths = []
            
            for idx, row in self.df.iterrows():
                depth = row['Depth']
                friction_angle = row['Friction_Angle']
                
                if condition == 'Initial':
                    pore_pressure = 50 * 1000
                elif condition == 'Injected':
                    pore_pressure = 50 * 1000
                else:
                    pore_pressure = 10 * 1000
                
                S1, S2, S3 = self.calculate_principal_stresses(depth, pore_pressure)
                normal_stress = (S1 + S3) / 2
                shear_stress = (S1 - S3) / 2
                cfs = self.calculate_coulomb_failure_stress(normal_stress, shear_stress, friction_angle)
                
                cfs_values.append(cfs / 1000)
                depths.append(depth)
            
            ax.scatter(depths, cfs_values, label=condition, alpha=0.7, s=100)
        
        ax.set_xlabel('Depth (m)')
        ax.set_ylabel('Coulomb Failure Stress (kPa)')
        ax.set_title('CFS Comparison - All Conditions')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        
        if save_plot:
            plt.savefig('coulomb_failure_stress_2d.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
    def plot_coulomb_failure_stress_by_depth(self, save_plot=True):
        """
        Plot Coulomb Failure Stress by Depth
        """
        plt.figure(figsize=(12, 8))
        
        # Calculate CFS for each depth
        depths = np.linspace(2000, 4000, 50)
        cfs_initial = []
        cfs_injected = []
        cfs_depleted = []
        
        for depth in depths:
            # Initial condition
            pore_pressure = 50 * 1000
            S1, S2, S3 = self.calculate_principal_stresses(depth, pore_pressure)
            normal_stress = (S1 + S3) / 2
            shear_stress = (S1 - S3) / 2
            cfs = self.calculate_coulomb_failure_stress(normal_stress, shear_stress, 30)  # Average friction angle
            cfs_initial.append(cfs / 1000)
            
            # Injected condition
            pore_pressure = 50 * 1000
            S1, S2, S3 = self.calculate_principal_stresses(depth, pore_pressure)
            normal_stress = (S1 + S3) / 2
            shear_stress = (S1 - S3) / 2
            cfs = self.calculate_coulomb_failure_stress(normal_stress, shear_stress, 30)
            cfs_injected.append(cfs / 1000)
            
            # Depleted condition
            pore_pressure = 10 * 1000
            S1, S2, S3 = self.calculate_principal_stresses(depth, pore_pressure)
            normal_stress = (S1 + S3) / 2
            shear_stress = (S1 - S3) / 2
            cfs = self.calculate_coulomb_failure_stress(normal_stress, shear_stress, 30)
            cfs_depleted.append(cfs / 1000)
        
        plt.plot(depths, cfs_initial, 'b-', linewidth=2, label='Initial')
        plt.plot(depths, cfs_injected, 'r-', linewidth=2, label='Injected')
        plt.plot(depths, cfs_depleted, 'g-', linewidth=2, label='Depleted')
        
        plt.axhline(y=0, color='red', linestyle='--', alpha=0.5, label='Failure Line')
        plt.xlabel('Depth (m)')
        plt.ylabel('Coulomb Failure Stress (kPa)')
        plt.title('Coulomb Failure Stress vs Depth')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_plot:
            plt.savefig('coulomb_failure_stress_by_depth.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
    def plot_combined_mohr_circle(self, save_plot=True):
        """
        Plot combined Mohr circle and scatter on the same axes with color bar
        """
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Calculate stresses for different conditions
        conditions = ['Initial', 'Injected', 'Depleted']
        colors = ['blue', 'red', 'green']
        
        all_normal_stress = []
        all_shear_stress = []
        all_colors = []
        
        for i, condition in enumerate(conditions):
            normal_stress_ratio = []
            shear_stress_ratio = []
            
            for idx, row in self.df.iterrows():
                depth = row['Depth']
                
                if condition == 'Initial':
                    pore_pressure = 50 * 1000
                elif condition == 'Injected':
                    pore_pressure = 50 * 1000
                else:
                    pore_pressure = 10 * 1000
                
                # Calculate stresses
                Sv = self.calculate_vertical_stress(depth)
                S1, S2, S3 = self.calculate_principal_stresses(depth, pore_pressure)
                
                # Calculate normal and shear stress ratios
                normal_stress = (S1 + S3) / 2
                shear_stress = (S1 - S3) / 2
                
                normal_ratio = normal_stress / Sv
                shear_ratio = shear_stress / Sv
                
                normal_stress_ratio.append(normal_ratio)
                shear_stress_ratio.append(shear_ratio)
                
                all_normal_stress.append(normal_ratio)
                all_shear_stress.append(shear_ratio)
                all_colors.append(i)
            
            # Plot Mohr circle for this condition
            center = np.mean(normal_stress_ratio)
            radius = np.mean(shear_stress_ratio)
            circle = Circle((center, 0), radius, fill=False, color=colors[i], 
                          linewidth=2, label=f'{condition} Mohr Circle')
            ax.add_patch(circle)
            
            # Plot scatter points
            ax.scatter(normal_stress_ratio, shear_stress_ratio, c=colors[i], 
                      s=100, alpha=0.7, label=f'{condition} Data Points')
        
        # Add colorbar
        scatter = ax.scatter(all_normal_stress, all_shear_stress, c=all_colors, 
                           cmap='RdYlBu', s=100, alpha=0.7)
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Condition (0=Initial, 1=Injected, 2=Depleted)')
        
        ax.set_xlabel('Normal Stress / Vertical Stress')
        ax.set_ylabel('Shear Stress / Vertical Stress')
        ax.set_title('Combined Mohr Circle and Scatter Plot')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
        
        if save_plot:
            plt.savefig('combined_mohr_circle.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
    def plot_3d_mohr_circle(self, save_plot=True):
        """
        Plot 3D Mohr's circle and scatter plot considering different pressure conditions
        """
        fig = plt.figure(figsize=(15, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        conditions = ['Initial', 'Injected', 'Depleted']
        colors = ['blue', 'red', 'green']
        markers = ['o', 's', '^']
        
        for i, condition in enumerate(conditions):
            x_coords = []
            y_coords = []
            z_coords = []
            
            for idx, row in self.df.iterrows():
                depth = row['Depth']
                
                if condition == 'Initial':
                    pore_pressure = 50 * 1000
                elif condition == 'Injected':
                    pore_pressure = 50 * 1000
                else:
                    pore_pressure = 10 * 1000
                
                # Calculate principal stresses
                S1, S2, S3 = self.calculate_principal_stresses(depth, pore_pressure)
                
                x_coords.append(S1 / 1000)  # Convert to MPa
                y_coords.append(S2 / 1000)
                z_coords.append(S3 / 1000)
            
            # Plot 3D scatter
            ax.scatter(x_coords, y_coords, z_coords, c=colors[i], 
                      marker=markers[i], s=100, alpha=0.7, label=condition)
            
            # Plot 3D Mohr circles (simplified representation)
            center_x = np.mean(x_coords)
            center_y = np.mean(y_coords)
            center_z = np.mean(z_coords)
            
            # Create sphere representing Mohr circle
            u = np.linspace(0, 2 * np.pi, 20)
            v = np.linspace(0, np.pi, 20)
            radius = np.std([x_coords, y_coords, z_coords])
            
            x_sphere = center_x + radius * np.outer(np.cos(u), np.sin(v))
            y_sphere = center_y + radius * np.outer(np.sin(u), np.sin(v))
            z_sphere = center_z + radius * np.outer(np.ones(np.size(u)), np.cos(v))
            
            ax.plot_surface(x_sphere, y_sphere, z_sphere, alpha=0.1, color=colors[i])
        
        ax.set_xlabel('S1 (MPa)')
        ax.set_ylabel('S2 (MPa)')
        ax.set_zlabel('S3 (MPa)')
        ax.set_title('3D Mohr Circle and Principal Stresses')
        ax.legend()
        
        if save_plot:
            plt.savefig('3d_mohr_circle.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
    def plot_effective_normal_vs_shear_stress(self, save_plot=True):
        """
        Plot effective normal vs shear stress
        """
        plt.figure(figsize=(12, 8))
        
        conditions = ['Initial', 'Injected', 'Depleted']
        colors = ['blue', 'red', 'green']
        
        for i, condition in enumerate(conditions):
            normal_stress_eff = []
            shear_stress = []
            
            for idx, row in self.df.iterrows():
                depth = row['Depth']
                
                if condition == 'Initial':
                    pore_pressure = 50 * 1000
                elif condition == 'Injected':
                    pore_pressure = 50 * 1000
                else:
                    pore_pressure = 10 * 1000
                
                # Calculate stresses
                S1, S2, S3 = self.calculate_principal_stresses(depth, pore_pressure)
                
                # Calculate effective normal and shear stress
                normal_stress = (S1 + S3) / 2
                shear_stress_val = (S1 - S3) / 2
                
                normal_stress_eff.append((normal_stress - pore_pressure) / 1000)  # Convert to MPa
                shear_stress.append(shear_stress_val / 1000)
            
            plt.scatter(normal_stress_eff, shear_stress, c=colors[i], 
                       s=100, alpha=0.7, label=condition)
        
        plt.xlabel('Effective Normal Stress (MPa)')
        plt.ylabel('Shear Stress (MPa)')
        plt.title('Effective Normal Stress vs Shear Stress')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_plot:
            plt.savefig('effective_normal_vs_shear_stress.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
    def plot_coulomb_failure_stress_colormap(self, save_plot=True):
        """
        Plot Coulomb failure stress with color bar for each depth
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create depth and fault arrays
        depths = np.linspace(2000, 4000, 20)
        fault_ids = [f'Fault_{i+1:02d}' for i in range(len(self.df))]
        
        # Create meshgrid
        D, F = np.meshgrid(depths, range(len(fault_ids)))
        CFS = np.zeros_like(D)
        
        for i, depth in enumerate(depths):
            for j, fault_idx in enumerate(range(len(self.df))):
                row = self.df.iloc[fault_idx]
                friction_angle = row['Friction_Angle']
                
                # Calculate CFS for different conditions
                pore_pressure = 10 * 1000  # Depleted condition
                S1, S2, S3 = self.calculate_principal_stresses(depth, pore_pressure)
                
                normal_stress = (S1 + S3) / 2
                shear_stress = (S1 - S3) / 2
                
                cfs = self.calculate_coulomb_failure_stress(normal_stress, shear_stress, friction_angle)
                CFS[j, i] = cfs / 1000  # Convert to kPa
        
        # Plot heatmap
        im = ax.imshow(CFS, cmap='RdYlBu_r', aspect='auto', 
                      extent=[depths.min(), depths.max(), 0, len(fault_ids)])
        
        ax.set_xlabel('Depth (m)')
        ax.set_ylabel('Fault Index')
        ax.set_title('Coulomb Failure Stress by Depth and Fault')
        ax.set_yticks(range(len(fault_ids)))
        ax.set_yticklabels(fault_ids, rotation=0)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Coulomb Failure Stress (kPa)')
        
        if save_plot:
            plt.savefig('coulomb_failure_stress_colormap.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
    def plot_shear_stress_vs_fault_dip(self, save_plot=True):
        """
        Plot shear stress vs fault dip for each depth
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Shear Stress vs Fault Dip Analysis', fontsize=16)
        
        depths = [2500, 3000, 3500, 4000]
        
        for i, depth in enumerate(depths):
            ax = axes[i//2, i%2]
            
            dips = np.linspace(10, 80, 20)
            shear_stresses = []
            
            for dip in dips:
                # Calculate shear stress for this dip
                pore_pressure = 10 * 1000  # Depleted condition
                S1, S2, S3 = self.calculate_principal_stresses(depth, pore_pressure)
                
                # Calculate shear stress on fault plane
                dip_rad = np.radians(dip)
                normal_stress = S1 * np.cos(dip_rad)**2 + S3 * np.sin(dip_rad)**2
                shear_stress = (S1 - S3) * np.sin(dip_rad) * np.cos(dip_rad)
                
                shear_stresses.append(shear_stress / 1000)  # Convert to MPa
            
            ax.plot(dips, shear_stresses, 'b-', linewidth=2, marker='o', markersize=4)
            ax.set_xlabel('Fault Dip (degrees)')
            ax.set_ylabel('Shear Stress (MPa)')
            ax.set_title(f'Depth: {depth} m')
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_plot:
            plt.savefig('shear_stress_vs_fault_dip.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
    def plot_shear_stress_fault_plane(self, save_plot=True):
        """
        Plot shear stress on a fault plane for different fault dips and induced shear stress values
        """
        fig = plt.figure(figsize=(15, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Create arrays for fault dips and induced shear stress
        dips = np.linspace(10, 80, 20)
        induced_shear = np.linspace(0, 50, 20)  # MPa
        
        D, S = np.meshgrid(dips, induced_shear)
        Z = np.zeros_like(D)
        
        depth = 3000  # Fixed depth
        pore_pressure = 10 * 1000
        
        for i, dip in enumerate(dips):
            for j, shear_val in enumerate(induced_shear):
                # Calculate total shear stress
                S1, S2, S3 = self.calculate_principal_stresses(depth, pore_pressure)
                dip_rad = np.radians(dip)
                
                # Natural shear stress
                natural_shear = (S1 - S3) * np.sin(dip_rad) * np.cos(dip_rad)
                
                # Total shear stress (natural + induced)
                total_shear = natural_shear + shear_val * 1000  # Convert to Pa
                
                Z[j, i] = total_shear / 1000  # Convert to MPa
        
        # Plot 3D surface
        surf = ax.plot_surface(D, S, Z, cmap='viridis', alpha=0.8)
        
        ax.set_xlabel('Fault Dip (degrees)')
        ax.set_ylabel('Induced Shear Stress (MPa)')
        ax.set_zlabel('Total Shear Stress (MPa)')
        ax.set_title('Shear Stress on Fault Plane')
        
        # Add colorbar
        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
        
        if save_plot:
            plt.savefig('shear_stress_fault_plane_3d.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
    def plot_coulomb_stability_friction_angles(self, save_plot=True):
        """
        Plot Coulomb stability for various fault friction angles for each depth
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Coulomb Stability vs Friction Angles', fontsize=16)
        
        depths = [2500, 3000, 3500, 4000]
        friction_angles = np.linspace(15, 45, 20)
        
        for i, depth in enumerate(depths):
            ax = axes[i//2, i%2]
            
            stability_values = []
            
            for friction_angle in friction_angles:
                pore_pressure = 10 * 1000  # Depleted condition
                S1, S2, S3 = self.calculate_principal_stresses(depth, pore_pressure)
                
                # Calculate stability (negative CFS means stable)
                normal_stress = (S1 + S3) / 2
                shear_stress = (S1 - S3) / 2
                
                cfs = self.calculate_coulomb_failure_stress(normal_stress, shear_stress, friction_angle)
                stability = -cfs / 1000  # Negative CFS for stability
                
                stability_values.append(stability)
            
            ax.plot(friction_angles, stability_values, 'b-', linewidth=2, marker='o', markersize=4)
            ax.axhline(y=0, color='red', linestyle='--', alpha=0.5, label='Stability Line')
            ax.set_xlabel('Friction Angle (degrees)')
            ax.set_ylabel('Stability (kPa)')
            ax.set_title(f'Depth: {depth} m')
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        plt.tight_layout()
        
        if save_plot:
            plt.savefig('coulomb_stability_friction_angles.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
    def plot_reservoir_depletion_pressure(self, save_plot=True):
        """
        Plot reservoir depletion pressure for fault reactivation for each depth
        """
        plt.figure(figsize=(12, 8))
        
        depths = np.linspace(2000, 4000, 50)
        critical_pressures = []
        
        for depth in depths:
            # Calculate critical depletion pressure
            initial_pore_pressure = 50 * 1000  # Pa
            S1, S2, S3 = self.calculate_principal_stresses(depth, initial_pore_pressure)
            
            # Calculate critical pressure for reactivation
            friction_angle = 30  # Average friction angle
            friction_angle_rad = np.radians(friction_angle)
            
            # Critical pressure calculation
            S1_eff = S1 - initial_pore_pressure
            S3_eff = S3 - initial_pore_pressure
            
            critical_pressure = initial_pore_pressure - (S1_eff - S3_eff) / (2 * np.tan(friction_angle_rad + np.pi/4))
            critical_pressures.append(critical_pressure / 1000)  # Convert to MPa
        
        plt.plot(depths, critical_pressures, 'b-', linewidth=2, label='Critical Depletion Pressure')
        plt.axhline(y=10, color='red', linestyle='--', alpha=0.5, label='Current Depleted Pressure')
        
        plt.xlabel('Depth (m)')
        plt.ylabel('Critical Depletion Pressure (MPa)')
        plt.title('Reservoir Depletion Pressure for Fault Reactivation')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_plot:
            plt.savefig('reservoir_depletion_pressure.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
    def plot_3d_mohr_circle_cohesion(self, save_plot=True):
        """
        Plot 3D Mohr's circle and scatter by considering cohesion factors
        """
        fig = plt.figure(figsize=(15, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        cohesion_factors = [35, 45, 55, 60]  # degrees
        conditions = ['Initial', 'Injected', 'Depleted']
        colors = ['blue', 'red', 'green']
        markers = ['o', 's', '^']
        
        for i, condition in enumerate(conditions):
            for j, cohesion_angle in enumerate(cohesion_factors):
                x_coords = []
                y_coords = []
                z_coords = []
                
                for idx, row in self.df.iterrows():
                    depth = row['Depth']
                    
                    if condition == 'Initial':
                        pore_pressure = 50 * 1000
                    elif condition == 'Injected':
                        pore_pressure = 50 * 1000
                    else:
                        pore_pressure = 10 * 1000
                    
                    # Calculate principal stresses
                    S1, S2, S3 = self.calculate_principal_stresses(depth, pore_pressure)
                    
                    # Apply cohesion factor
                    cohesion_rad = np.radians(cohesion_angle)
                    S1_cohesion = S1 + self.cohesion * np.cos(cohesion_rad)
                    S3_cohesion = S3 + self.cohesion * np.sin(cohesion_rad)
                    
                    x_coords.append(S1_cohesion / 1000)  # Convert to MPa
                    y_coords.append(S2 / 1000)
                    z_coords.append(S3_cohesion / 1000)
                
                # Plot 3D scatter with different colors for cohesion
                color_intensity = j / len(cohesion_factors)
                ax.scatter(x_coords, y_coords, z_coords, 
                          c=[colors[i]], s=50, alpha=0.6, 
                          label=f'{condition} - Cohesion {cohesion_angle}°')
        
        ax.set_xlabel('S1 (MPa)')
        ax.set_ylabel('S2 (MPa)')
        ax.set_zlabel('S3 (MPa)')
        ax.set_title('3D Mohr Circle with Cohesion Factors')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        if save_plot:
            plt.savefig('3d_mohr_circle_cohesion.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
    def plot_critical_friction_angle_horizontal_path(self, save_plot=True):
        """
        Plot critical friction angle vs horizontal path for each depth
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Critical Friction Angle vs Horizontal Path', fontsize=16)
        
        depths = [2500, 3000, 3500, 4000]
        horizontal_paths = np.linspace(0, 1000, 20)  # meters
        
        for i, depth in enumerate(depths):
            ax = axes[i//2, i%2]
            
            critical_friction_angles = []
            
            for path in horizontal_paths:
                pore_pressure = 10 * 1000  # Depleted condition
                S1, S2, S3 = self.calculate_principal_stresses(depth, pore_pressure)
                
                # Calculate critical friction angle
                normal_stress = (S1 + S3) / 2
                shear_stress = (S1 - S3) / 2
                
                # Critical friction angle calculation
                if normal_stress > 0:
                    critical_friction_angle = np.degrees(np.arctan(shear_stress / normal_stress))
                else:
                    critical_friction_angle = 0
                
                critical_friction_angles.append(critical_friction_angle)
            
            ax.plot(horizontal_paths, critical_friction_angles, 'b-', linewidth=2, marker='o', markersize=4)
            ax.set_xlabel('Horizontal Path (m)')
            ax.set_ylabel('Critical Friction Angle (degrees)')
            ax.set_title(f'Depth: {depth} m')
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_plot:
            plt.savefig('critical_friction_angle_horizontal_path.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
    def plot_critical_depletion_pressure_reactivation(self, save_plot=True):
        """
        Plot critical depletion pressure for fault reactivation for each depth
        """
        plt.figure(figsize=(12, 8))
        
        depths = np.linspace(2000, 4000, 50)
        critical_depletion_pressures = []
        
        for depth in depths:
            # Calculate critical depletion pressure for reactivation
            initial_pore_pressure = 50 * 1000  # Pa
            S1, S2, S3 = self.calculate_principal_stresses(depth, initial_pore_pressure)
            
            # Calculate critical pressure for reactivation
            friction_angle = 30  # Average friction angle
            friction_angle_rad = np.radians(friction_angle)
            
            # Critical depletion pressure calculation
            S1_eff = S1 - initial_pore_pressure
            S3_eff = S3 - initial_pore_pressure
            
            critical_depletion = initial_pore_pressure - (S1_eff - S3_eff) / (2 * np.tan(friction_angle_rad + np.pi/4))
            critical_depletion_pressures.append(critical_depletion / 1000)  # Convert to MPa
        
        plt.plot(depths, critical_depletion_pressures, 'b-', linewidth=2, 
                label='Critical Depletion Pressure')
        plt.axhline(y=10, color='red', linestyle='--', alpha=0.5, 
                   label='Current Depleted Pressure (10 MPa)')
        
        plt.xlabel('Depth (m)')
        plt.ylabel('Critical Depletion Pressure (MPa)')
        plt.title('Critical Depletion Pressure for Fault Reactivation')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_plot:
            plt.savefig('critical_depletion_pressure_reactivation.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
    def plot_coulomb_failure_function_stress_path(self, save_plot=True):
        """
        Plot Coulomb failure function with stress path for each depth
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Coulomb Failure Function with Stress Path', fontsize=16)
        
        depths = [2500, 3000, 3500, 4000]
        
        for i, depth in enumerate(depths):
            ax = axes[i//2, i%2]
            
            # Define stress path (from initial to depleted)
            pore_pressures = np.linspace(50, 10, 20) * 1000  # Pa
            cfs_values = []
            
            for pore_pressure in pore_pressures:
                S1, S2, S3 = self.calculate_principal_stresses(depth, pore_pressure)
                
                normal_stress = (S1 + S3) / 2
                shear_stress = (S1 - S3) / 2
                
                cfs = self.calculate_coulomb_failure_stress(normal_stress, shear_stress, 30)
                cfs_values.append(cfs / 1000)  # Convert to kPa
            
            # Plot stress path
            ax.plot(pore_pressures / 1000, cfs_values, 'b-', linewidth=2, marker='o', markersize=4)
            ax.axhline(y=0, color='red', linestyle='--', alpha=0.5, label='Failure Line')
            
            ax.set_xlabel('Pore Pressure (MPa)')
            ax.set_ylabel('Coulomb Failure Stress (kPa)')
            ax.set_title(f'Depth: {depth} m')
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        plt.tight_layout()
        
        if save_plot:
            plt.savefig('coulomb_failure_function_stress_path.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
    def plot_critical_depletion_pressure_different_depths(self, save_plot=True):
        """
        Plot Critical Depletion Pressure for Fault Reactivation in different depths
        """
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        depths = np.linspace(2000, 4000, 20)
        friction_angles = np.linspace(20, 45, 20)
        
        D, F = np.meshgrid(depths, friction_angles)
        Z = np.zeros_like(D)
        
        for i, depth in enumerate(depths):
            for j, friction_angle in enumerate(friction_angles):
                initial_pore_pressure = 50 * 1000  # Pa
                S1, S2, S3 = self.calculate_principal_stresses(depth, initial_pore_pressure)
                
                friction_angle_rad = np.radians(friction_angle)
                S1_eff = S1 - initial_pore_pressure
                S3_eff = S3 - initial_pore_pressure
                
                critical_depletion = initial_pore_pressure - (S1_eff - S3_eff) / (2 * np.tan(friction_angle_rad + np.pi/4))
                Z[j, i] = critical_depletion / 1000  # Convert to MPa
        
        # Plot 3D surface
        surf = ax.plot_surface(D, F, Z, cmap='viridis', alpha=0.8)
        
        ax.set_xlabel('Depth (m)')
        ax.set_ylabel('Friction Angle (degrees)')
        ax.set_zlabel('Critical Depletion Pressure (MPa)')
        ax.set_title('Critical Depletion Pressure for Fault Reactivation')
        
        # Add colorbar
        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
        
        if save_plot:
            plt.savefig('critical_depletion_pressure_different_depths.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
    def plot_combined_mohr_circle_sigma_ratios(self, save_plot=True):
        """
        Plot combined Mohr Circle and scatter plot of sigma normal/sigma vertical versus shear stress / sigma vertical
        """
        fig, ax = plt.subplots(figsize=(12, 10))
        
        conditions = ['Initial', 'Injected', 'Depleted']
        colors = ['blue', 'red', 'green']
        
        all_sigma_normal_ratio = []
        all_shear_ratio = []
        all_colors = []
        
        for i, condition in enumerate(conditions):
            sigma_normal_ratio = []
            shear_ratio = []
            
            for idx, row in self.df.iterrows():
                depth = row['Depth']
                
                if condition == 'Initial':
                    pore_pressure = 50 * 1000
                elif condition == 'Injected':
                    pore_pressure = 50 * 1000
                else:
                    pore_pressure = 10 * 1000
                
                # Calculate stresses
                Sv = self.calculate_vertical_stress(depth)
                S1, S2, S3 = self.calculate_principal_stresses(depth, pore_pressure)
                
                # Calculate normal and shear stress ratios
                sigma_normal = (S1 + S3) / 2
                shear_stress = (S1 - S3) / 2
                
                sigma_normal_ratio_val = sigma_normal / Sv
                shear_ratio_val = shear_stress / Sv
                
                sigma_normal_ratio.append(sigma_normal_ratio_val)
                shear_ratio.append(shear_ratio_val)
                
                all_sigma_normal_ratio.append(sigma_normal_ratio_val)
                all_shear_ratio.append(shear_ratio_val)
                all_colors.append(i)
            
            # Plot Mohr circle for this condition
            center = np.mean(sigma_normal_ratio)
            radius = np.mean(shear_ratio)
            circle = Circle((center, 0), radius, fill=False, color=colors[i], 
                          linewidth=2, label=f'{condition} Mohr Circle')
            ax.add_patch(circle)
            
            # Plot scatter points
            ax.scatter(sigma_normal_ratio, shear_ratio, c=colors[i], 
                      s=100, alpha=0.7, label=f'{condition} Data Points')
        
        # Add colorbar
        scatter = ax.scatter(all_sigma_normal_ratio, all_shear_ratio, c=all_colors, 
                           cmap='RdYlBu', s=100, alpha=0.7)
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Condition (0=Initial, 1=Injected, 2=Depleted)')
        
        ax.set_xlabel('Sigma Normal / Sigma Vertical')
        ax.set_ylabel('Shear Stress / Sigma Vertical')
        ax.set_title('Combined Mohr Circle - Sigma Ratios')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
        
        if save_plot:
            plt.savefig('combined_mohr_circle_sigma_ratios.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
    def print_maximum_allowable_pressure_increase(self):
        """
        Print maximum allowable pressure increase for each fault
        """
        print("\n" + "="*80)
        print("MAXIMUM ALLOWABLE PRESSURE INCREASE FOR EACH FAULT")
        print("="*80)
        
        for idx, row in self.df.iterrows():
            fault_id = row['Fault_ID']
            depth = row['Depth']
            friction_angle = row['Friction_Angle']
            
            # Calculate maximum allowable pressure increase
            initial_pore_pressure = 50 * 1000  # Pa
            max_pressure = self.calculate_maximum_allowable_pressure(
                depth, initial_pore_pressure, friction_angle
            )
            
            print(f"Fault ID: {fault_id}")
            print(f"  Depth: {depth:.1f} m")
            print(f"  Friction Angle: {friction_angle:.1f}°")
            print(f"  Max Allowable Pressure Increase: {max_pressure/1000:.2f} MPa")
            print("-" * 40)
        
    def plot_faults_2d_reactivation_status(self, save_plot=True):
        """
        Plot faults 2D top view by considering reactivation of each fault at different stress status
        """
        plt.figure(figsize=(15, 12))
        
        # Calculate reactivation status for each fault
        reactivation_status = []
        
        for idx, row in self.df.iterrows():
            depth = row['Depth']
            friction_angle = row['Friction_Angle']
            
            # Check reactivation for depleted condition
            pore_pressure = 10 * 1000  # Depleted condition
            S1, S2, S3 = self.calculate_principal_stresses(depth, pore_pressure)
            
            normal_stress = (S1 + S3) / 2
            shear_stress = (S1 - S3) / 2
            
            cfs = self.calculate_coulomb_failure_stress(normal_stress, shear_stress, friction_angle)
            
            if cfs > 0:
                reactivation_status.append('Reactivated')
            else:
                reactivation_status.append('Stable')
        
        # Plot each fault with different colors based on reactivation status
        for idx, row in self.df.iterrows():
            x_start = row['X_coord']
            y_start = row['Y_coord']
            
            # Calculate end point based on strike and length
            strike_rad = np.radians(row['Strike'])
            length = row['Length']
            
            x_end = x_start + length * np.cos(strike_rad)
            y_end = y_start + length * np.sin(strike_rad)
            
            # Choose color based on reactivation status
            if reactivation_status[idx] == 'Reactivated':
                color = 'red'
                linewidth = 3
            else:
                color = 'green'
                linewidth = 2
            
            # Plot fault line
            plt.plot([x_start, x_end], [y_start, y_end], color=color, 
                    linewidth=linewidth, alpha=0.8)
            
            # Add fault ID label
            plt.text(x_start, y_start, row['Fault_ID'], fontsize=8, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
        
        # Add legend
        plt.plot([], [], 'r-', linewidth=3, label='Reactivated Faults')
        plt.plot([], [], 'g-', linewidth=2, label='Stable Faults')
        
        plt.xlabel('X Coordinate (m)')
        plt.ylabel('Y Coordinate (m)')
        plt.title('Fault Map - Reactivation Status (Depleted Condition)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        
        if save_plot:
            plt.savefig('fault_map_reactivation_status.png', dpi=300, bbox_inches='tight')
        
        plt.show()
        
    def run_comprehensive_analysis(self):
        """
        Run comprehensive fault reactivation analysis
        """
        print("Starting Comprehensive Fault Reactivation Analysis...")
        print("="*60)
        
        # Basic plots
        print("\n1. Plotting 2D fault map...")
        self.plot_faults_2d_topview()
        
        print("\n2. Plotting Coulomb failure stress analysis...")
        self.plot_2d_coulomb_failure_stress()
        self.plot_coulomb_failure_stress_by_depth()
        
        print("\n3. Plotting Mohr circle analysis...")
        self.plot_combined_mohr_circle()
        self.plot_3d_mohr_circle()
        
        print("\n4. Plotting effective stress analysis...")
        self.plot_effective_normal_vs_shear_stress()
        
        print("\n5. Plotting Coulomb failure stress colormap...")
        self.plot_coulomb_failure_stress_colormap()
        
        print("\n6. Plotting shear stress analysis...")
        self.plot_shear_stress_vs_fault_dip()
        self.plot_shear_stress_fault_plane()
        
        print("\n7. Plotting stability analysis...")
        self.plot_coulomb_stability_friction_angles()
        
        print("\n8. Plotting pressure analysis...")
        self.plot_reservoir_depletion_pressure()
        self.plot_critical_depletion_pressure_reactivation()
        
        print("\n9. Plotting advanced Mohr circle analysis...")
        self.plot_3d_mohr_circle_cohesion()
        self.plot_combined_mohr_circle_sigma_ratios()
        
        print("\n10. Plotting critical analysis...")
        self.plot_critical_friction_angle_horizontal_path()
        self.plot_coulomb_failure_function_stress_path()
        self.plot_critical_depletion_pressure_different_depths()
        
        print("\n11. Plotting reactivation status...")
        self.plot_faults_2d_reactivation_status()
        
        print("\n12. Printing maximum allowable pressure increases...")
        self.print_maximum_allowable_pressure_increase()
        
        print("\n" + "="*60)
        print("Comprehensive analysis completed!")
        print("All plots have been saved as PNG files.")
        print("="*60)

if __name__ == "__main__":
    # Initialize analysis
    analysis = FaultReactivationAnalysis("fault_data.csv")
    
    print("Fault Reactivation Analysis initialized successfully!")
    print(f"Number of faults: {len(analysis.df)}")
    print(f"Pressure data points: {len(analysis.df2)}")
    
    # Run comprehensive analysis
    analysis.run_comprehensive_analysis()