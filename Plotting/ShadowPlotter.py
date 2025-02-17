from typing import List, Optional, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np
from DataModel.Shadow import Shadow
from DataModel.Wall import Wall
from DataModel.PlotConfig import PlotConfig

class ShadowPlotter:
    """Class for plotting shadows and walls."""
    
    def __init__(self, config: PlotConfig):
        """Initialize the plotter with configuration."""
        self.config = config
        
    def plot_wall(self, wall: Wall, ax: Axes, show_dimensions: bool = True) -> None:
        """Plot a wall on the given axes.
        
        Args:
            wall: Wall to plot
            ax: Matplotlib axes to plot on
            show_dimensions: Whether to show wall dimensions
        """
        # Plot wall line
        ax.plot(
            [wall.start_point.x.magnitude, wall.end_point.x.magnitude],
            [wall.start_point.y.magnitude, wall.end_point.y.magnitude],
            'k-',  # Black solid line
            linewidth=2,
            label=f'Wall: {wall.name}'
        )
        
        # Add wall height annotation if requested
        if show_dimensions:
            midpoint_x = (wall.start_point.x.magnitude + wall.end_point.x.magnitude) / 2
            midpoint_y = (wall.start_point.y.magnitude + wall.end_point.y.magnitude) / 2
            ax.annotate(
                f'H: {wall.height:~P}',
                (midpoint_x, midpoint_y),
                xytext=(5, 5),
                textcoords='offset points'
            )
    
    def plot_shadow(self, shadow: Shadow, ax: Axes, show_dimensions: bool = True) -> None:
        """Plot a shadow on the given axes.
        
        Args:
            shadow: Shadow to plot
            ax: Matplotlib axes to plot on
            show_dimensions: Whether to show shadow dimensions
        """
        # Get vertex coordinates
        x_coords = [v.x.magnitude for v in shadow.vertices]
        y_coords = [v.y.magnitude for v in shadow.vertices]
        
        # Plot shadow polygon
        polygon = patches.Polygon(
            list(zip(x_coords, y_coords)),
            facecolor='gray',
            alpha=0.3,
            label=f'Shadow: {shadow.wall.name}'
        )
        ax.add_patch(polygon)
        
        # Add shadow dimensions if requested
        if show_dimensions:
            shadow_mid_x = (x_coords[2] + x_coords[3]) / 2
            shadow_mid_y = (y_coords[2] + y_coords[3]) / 2
            ax.annotate(
                f'L: {shadow.length:~P}\nW: {shadow.width:~P}',
                (shadow_mid_x, shadow_mid_y),
                xytext=(5, 5),
                textcoords='offset points'
            )
    
    def plot_compass_with_sun(self, ax: Axes, x_min: float, x_max: float, 
                            y_min: float, y_max: float, shadow: Shadow) -> None:
        """Plot compass with sun position in bottom right corner.
        
        Args:
            ax: Matplotlib axes to plot on
            x_min, x_max, y_min, y_max: Plot limits
            shadow: Shadow to get sun position from
        """
        # Calculate compass size and position
        plot_width = x_max - x_min
        plot_height = y_max - y_min
        compass_size = min(plot_width, plot_height) * 0.1  # Even smaller compass
        
        # Position compass in bottom right with padding
        padding = compass_size * 0.5
        center_x = x_max - compass_size - padding
        center_y = y_min + compass_size + padding
        
        # Draw compass circle
        compass_circle = patches.Circle(
            (center_x, center_y),
            radius=compass_size,
            fill=False,
            color='gray',
            linestyle='--',
            alpha=0.5
        )
        ax.add_patch(compass_circle)
        
        # Add direction labels
        directions = {
            'N': (0, 1),    # North
            'S': (0, -1),   # South
            'E': (1, 0),    # East
            'W': (-1, 0),   # West
        }
        
        for direction, (dx, dy) in directions.items():
            x = center_x + dx * compass_size * 0.8
            y = center_y + dy * compass_size * 0.8
            ax.text(
                x, y, direction,
                ha='center', va='center',
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'),
                fontsize=8,
                fontweight='bold'
            )
            
        # Add sun position inside compass
        sun_angle_rad = np.radians(shadow.solar_azimuth)
        sun_x = center_x + np.cos(sun_angle_rad) * compass_size * 0.6
        sun_y = center_y + np.sin(sun_angle_rad) * compass_size * 0.6
        
        # Draw sun symbol
        sun = patches.Circle(
            (sun_x, sun_y),
            radius=compass_size * 0.1,
            facecolor='yellow',
            edgecolor='orange',
            label='Sun'
        )
        ax.add_patch(sun)
        
        # Add compact sun info
        ax.text(
            center_x, center_y,
            f"El: {shadow.solar_elevation:.0f}°",
            ha='center', va='center',
            fontsize=7,
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
        )
    
    def plot(self, shadows: List[Shadow], title: Optional[str] = None) -> Figure:
        """Create a complete plot with walls, shadows, and annotations.
        
        Args:
            shadows: List of shadows to plot
            title: Optional title for the plot
            
        Returns:
            Matplotlib figure
        """
        # Create figure and axes
        fig, ax = plt.subplots(figsize=self.config.figure_size)
        
        # Plot each shadow and its wall
        for shadow in shadows:
            self.plot_shadow(shadow, ax, self.config.show_dimensions)
            self.plot_wall(shadow.wall, ax, self.config.show_dimensions)
        
        # Get plot limits
        all_x = []
        all_y = []
        for shadow in shadows:
            all_x.extend(v.x.magnitude for v in shadow.vertices)
            all_y.extend(v.y.magnitude for v in shadow.vertices)
        
        # Add padding to limits
        x_min, x_max = min(all_x), max(all_x)
        y_min, y_max = min(all_y), max(all_y)
        padding = max(x_max - x_min, y_max - y_min) * 0.2
        x_min -= padding
        x_max += padding
        y_min -= padding
        y_max += padding
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        
        # Plot compass with sun if requested
        if self.config.show_compass and shadows:
            self.plot_compass_with_sun(ax, x_min, x_max, y_min, y_max, shadows[0])
        
        # Set title with time in configured timezone
        if title:
            ax.set_title(title)
        elif shadows:
            time_str = self.config.format_time(shadows[0].time)
            ax.set_title(f"Shadow Calculations for {time_str}")
            
        # Add grid and labels
        ax.grid(True, linestyle='--', alpha=0.3)
        unit = str(shadows[0].wall.start_point.x.units)  # Get unit from first point
        ax.set_xlabel(f'Distance ({unit})')
        ax.set_ylabel(f'Distance ({unit})')
        
        # Add legend
        ax.legend(
            bbox_to_anchor=(1.05, 1),
            loc='upper left',
            borderaxespad=0
        )
        
        # Set equal aspect ratio
        ax.set_aspect('equal')
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        return fig
    
    def save(self, fig: Figure, filename: str) -> None:
        """Save the figure to a file.
        
        Args:
            fig: Figure to save
            filename: Output filename (should end in .png, .pdf, etc.)
        """
        fig.savefig(filename, bbox_inches='tight', dpi=self.config.dpi)
