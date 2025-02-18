from typing import List
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.axes import Axes
from DataModel.Shadow import Shadow
from DataModel.Wall import Wall
from DataModel.PlotConfig import PlotConfig

class ShadowPlotter:
    """Class for plotting walls and their shadows."""
    
    def __init__(self, config: PlotConfig):
        """Initialize with plot configuration."""
        self.config = config
    
    def plot_wall(self, wall: Wall, ax: Axes, show_dimensions: bool = True) -> None:
        """Plot a wall on the given axes.
        
        Args:
            wall: Wall to plot
            ax: Matplotlib axes to plot on
            show_dimensions: Whether to show wall dimensions
        """
        # Convert coordinates to output units
        start_x = self.config.convert_to_output_units(wall.start_point.x).magnitude
        start_y = self.config.convert_to_output_units(wall.start_point.y).magnitude
        end_x = self.config.convert_to_output_units(wall.end_point.x).magnitude
        end_y = self.config.convert_to_output_units(wall.end_point.y).magnitude
        
        # Plot wall line
        ax.plot(
            [start_x, end_x],
            [start_y, end_y],
            'k-',  # Black solid line
            linewidth=2,
            label=f'Wall: {wall.name}'
        )
        
        # Add wall height annotation if requested
        if show_dimensions:
            midpoint_x = (start_x + end_x) / 2
            midpoint_y = (start_y + end_y) / 2
            height = self.config.convert_to_output_units(wall.height)
            # Format height with 2 decimal places
            height_str = f"{height.magnitude:.2f} {height.units:~P}"
            ax.annotate(
                f'H: {height_str}',
                (midpoint_x, midpoint_y),
                xytext=(5, 5),
                textcoords='offset points'
            )
    
    def plot_shadow(self, shadow: Shadow, ax: Axes) -> None:
        """Plot a shadow on the given axes.
        
        Args:
            shadow: Shadow to plot
            ax: Matplotlib axes to plot on
        """
        # Convert vertex coordinates to output units
        x_coords = [
            self.config.convert_to_output_units(v.x).magnitude 
            for v in shadow.vertices
        ]
        y_coords = [
            self.config.convert_to_output_units(v.y).magnitude 
            for v in shadow.vertices
        ]
        
        # Plot shadow polygon
        polygon = patches.Polygon(
            list(zip(x_coords, y_coords)),
            facecolor='gray',
            alpha=0.3,
            label=f'Shadow: {shadow.wall.name}'
        )
        ax.add_patch(polygon)
    
    def get_plot_limits(self, shadows: List[Shadow]) -> tuple[float, float, float, float]:
        """Calculate plot limits to encompass all shadows.
        
        Args:
            shadows: List of shadows to consider
            
        Returns:
            Tuple of (x_min, x_max, y_min, y_max) in output units
        """
        all_x = []
        all_y = []
        for shadow in shadows:
            # Convert all coordinates to output units
            all_x.extend(
                self.config.convert_to_output_units(v.x).magnitude 
                for v in shadow.vertices
            )
            all_y.extend(
                self.config.convert_to_output_units(v.y).magnitude 
                for v in shadow.vertices
            )
            
        x_min, x_max = min(all_x), max(all_x)
        y_min, y_max = min(all_y), max(all_y)
        
        # Add padding
        padding = max(x_max - x_min, y_max - y_min) * 0.2
        x_min -= padding
        x_max += padding
        y_min -= padding
        y_max += padding
        
        return x_min, x_max, y_min, y_max
    
    def plot_shadows(self, shadows: List[Shadow], ax: Axes, show_dimensions: bool = True) -> None:
        """Plot all shadows and their walls.
        
        Args:
            shadows: List of shadows to plot
            ax: Matplotlib axes to plot on
            show_dimensions: Whether to show wall dimensions
        """
        # Plot each shadow and its wall
        for shadow in shadows:
            self.plot_shadow(shadow, ax)
            self.plot_wall(shadow.wall, ax, show_dimensions)
            
        # Set axis labels
        ax.set_xlabel(f'Distance ({self.config.output_units})')
        ax.set_ylabel(f'Distance ({self.config.output_units})')
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.3)
