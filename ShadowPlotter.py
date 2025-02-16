"""
Plotting and animation utilities for the shadow calculator.
Handles visualization of wall shadows and shadow movement over time.
"""

import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for interactive plotting
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, Polygon
from matplotlib.animation import FuncAnimation
from datetime import datetime
from typing import List, Tuple, Optional

class ShadowPlotter:
    """Handles plotting and animation of wall shadows."""
    
    @staticmethod
    def create_wall_patch(wall_width: float, wall_angle: float) -> Rectangle:
        """
        Create a rectangle patch representing the wall.
        Wall angle is measured clockwise from north.
        """
        # Convert to matplotlib angle (counterclockwise from east)
        plot_angle = 90 - wall_angle
        
        # Create wall rectangle
        wall = Rectangle(
            (-wall_width/2, 0),  # (x,y) of lower left corner
            wall_width,          # width
            0.2,                # thickness
            angle=plot_angle,    # rotation angle
            color='black',
            zorder=2
        )
        return wall
    
    @staticmethod
    def create_shadow_patch(wall_width: float, shadow_length: float, 
                          shadow_width: float, shadow_angle: float) -> Polygon:
        """
        Create a polygon patch representing the shadow.
        Shadow angle is the direction the shadow is cast (solar azimuth + 180°).
        """
        # Convert angles to matplotlib coordinates (counterclockwise from east)
        wall_angle = (shadow_angle + 180) % 360  # Wall faces opposite to shadow
        wall_rad = np.radians(90 - wall_angle)
        shadow_rad = np.radians(90 - shadow_angle)
        
        # Calculate wall endpoints
        wall_left = np.array([-wall_width/2, 0])
        wall_right = np.array([wall_width/2, 0])
        
        # Rotate wall points
        rotation_matrix = np.array([
            [np.cos(wall_rad), -np.sin(wall_rad)],
            [np.sin(wall_rad), np.cos(wall_rad)]
        ])
        wall_left = rotation_matrix @ wall_left
        wall_right = rotation_matrix @ wall_right
        
        # Calculate shadow offset
        shadow_offset = np.array([
            shadow_length * np.cos(shadow_rad),
            shadow_length * np.sin(shadow_rad)
        ])
        
        # Calculate shadow width offset (perpendicular to shadow direction)
        shadow_width_rad = shadow_rad + np.pi/2
        shadow_width_offset = np.array([
            (shadow_width - wall_width)/2 * np.cos(shadow_width_rad),
            (shadow_width - wall_width)/2 * np.sin(shadow_width_rad)
        ])
        
        # Define vertices for shadow polygon
        vertices = [
            wall_left,                              # Left wall point
            wall_right,                             # Right wall point
            wall_right + shadow_offset + shadow_width_offset,  # Right shadow end
            wall_left + shadow_offset - shadow_width_offset    # Left shadow end
        ]
        
        return Polygon(vertices, color='gray', alpha=0.3, zorder=1)
    
    @classmethod
    def plot_shadow(cls, wall_width: float, wall_angle: float, shadow_length: float, 
                   shadow_width: float, shadow_angle: float, time: Optional[datetime] = None,
                   ax: Optional[plt.Axes] = None, show: bool = True) -> plt.Axes:
        """Plot the wall and its shadow."""
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 10))
            
        # Clear previous content
        ax.clear()
        
        # Add wall and shadow patches
        wall = cls.create_wall_patch(wall_width, wall_angle)
        shadow = cls.create_shadow_patch(wall_width, shadow_length, shadow_width, shadow_angle)
        
        ax.add_patch(wall)
        ax.add_patch(shadow)
        
        # Add compass directions at fixed positions
        compass_radius = max(shadow_length, wall_width) * 1.2
        compass_points = {
            'N': (0, compass_radius),
            'S': (0, -compass_radius),
            'E': (compass_radius, 0),
            'W': (-compass_radius, 0)
        }
        
        for direction, (x, y) in compass_points.items():
            ax.text(x, y, direction, ha='center', va='center')
            
        # Set title if time provided
        if time:
            ax.set_title(f"Shadow at {time.strftime('%Y-%m-%d %H:%M')}")
            
        # Set equal aspect ratio and limits
        ax.set_aspect('equal')
        limit = max(shadow_length, wall_width) * 1.5
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.3)
        
        # Add axes labels
        ax.set_xlabel('Distance (meters)')
        ax.set_ylabel('Distance (meters)')
        
        if show:
            plt.show(block=True)
            
        return ax
    
    @classmethod
    def create_shadow_animation(cls, results: List[Tuple], wall_width: float, 
                              wall_angle: float, output_file: Optional[str] = None) -> None:
        """
        Create an animation of shadow movement over time.
        
        Args:
            results: List of (time, length, width, angle, area) tuples
            wall_width: Width of the wall in meters
            wall_angle: Wall angle in degrees from true north
            output_file: Optional file to save animation to (must end in .gif or .mp4)
        """
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 10))
        
        def update(frame):
            """Animation update function."""
            time, length, width, angle, _ = results[frame]
            cls.plot_shadow(wall_width, wall_angle, length, width, angle, time, ax, False)
            return ax,
            
        # Create animation
        anim = FuncAnimation(
            fig, update, frames=len(results),
            interval=100, blit=True
        )
        
        if output_file:
            if output_file.endswith('.gif'):
                anim.save(output_file, writer='pillow')
            elif output_file.endswith('.mp4'):
                anim.save(output_file, writer='ffmpeg')
        else:
            plt.show()
