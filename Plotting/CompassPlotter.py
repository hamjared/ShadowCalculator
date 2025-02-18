from typing import Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.axes import Axes
import numpy as np
from DataModel.Shadow import Shadow
from DataModel.Location import Location
from Calculation.Sun import Sun

class CompassPlotter:
    """Class for plotting compass and sun path."""
    
    def __init__(self, location: Location):
        """Initialize with location."""
        self.location = location
    
    def plot_compass(self, ax: Axes, corner_x: float, corner_y: float, 
                    size: float, shadow: Shadow) -> None:
        """Plot compass with sun path in specified corner.
        
        Args:
            ax: Matplotlib axes to plot on
            corner_x: X coordinate for compass center
            corner_y: Y coordinate for compass center
            size: Size of compass
            shadow: Shadow to get time from
        """
        # Draw compass circle
        compass_circle = patches.Circle(
            (corner_x, corner_y),
            radius=size,
            fill=False,
            color='gray',
            linestyle='--',
            alpha=0.5
        )
        ax.add_patch(compass_circle)
        
        # Add direction labels
        directions = {
            'N': (0, 1),    # North
            'NE': (0.707, 0.707),  # Northeast
            'E': (1, 0),    # East
            'SE': (0.707, -0.707), # Southeast
            'S': (0, -1),   # South
            'SW': (-0.707, -0.707), # Southwest
            'W': (-1, 0),   # West
            'NW': (-0.707, 0.707),  # Northwest
        }
        
        for direction, (dx, dy) in directions.items():
            x = corner_x + dx * size * 0.8
            y = corner_y + dy * size * 0.8
            ax.text(
                x, y, direction,
                ha='center', va='center',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'),
                fontsize=6,  # Smaller font for more directions
                fontweight='bold'
            )
            
        # Get sun positions for the day
        positions = Sun.get_day_positions(
            latitude=self.location.latitude,
            longitude=self.location.longitude,
            date=shadow.time,
            interval_minutes=30
        )
        
        # Helper function to convert sun position to compass coordinates
        def sun_to_compass(azimuth: float, elevation: float) -> tuple:
            angle_rad = np.radians(90 - azimuth)  # Convert to math angle
            radius = size * (1 - elevation/90) * 0.8
            x = corner_x + np.cos(angle_rad) * radius
            y = corner_y + np.sin(angle_rad) * radius
            return (x, y)
        
        # Draw sun path
        if positions:
            path_points = [
                sun_to_compass(pos.azimuth, pos.elevation)
                for pos in positions
            ]
            path_x, path_y = zip(*path_points)
            ax.plot(path_x, path_y, '--', color='orange', alpha=0.3, linewidth=1)
            
            # Add sunrise and sunset markers
            sunrise_pos = positions[0]
            sunset_pos = positions[-1]
            for pos, label in [(sunrise_pos, "Sunrise"), (sunset_pos, "Sunset")]:
                x, y = sun_to_compass(pos.azimuth, pos.elevation)
                ax.text(x, y, label,
                       fontsize=5, ha='center', va='center',
                       bbox=dict(facecolor='white', alpha=0.7, 
                               edgecolor='none', pad=0.5))
        
        # Draw current sun position
        sun_x, sun_y = sun_to_compass(shadow.solar_azimuth, shadow.solar_elevation)
        sun = patches.Circle(
            (sun_x, sun_y),
            radius=size * 0.08,
            facecolor='yellow',
            edgecolor='orange',
            label='Sun'
        )
        ax.add_patch(sun)
        
        # Add current time and elevation
        current_time = shadow.time.strftime('%H:%M')
        ax.text(
            corner_x, corner_y - size * 0.2,
            f"{current_time}\nEl: {shadow.solar_elevation:.0f}°",
            ha='center', va='center',
            fontsize=6,
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
        )
