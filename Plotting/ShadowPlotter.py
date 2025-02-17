from typing import List
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.axes import Axes
from DataModel.Shadow import Shadow
from DataModel.Wall import Wall

class ShadowPlotter:
    """Class for plotting walls and their shadows."""
    
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
    
    def plot_shadow(self, shadow: Shadow, ax: Axes) -> None:
        """Plot a shadow on the given axes.
        
        Args:
            shadow: Shadow to plot
            ax: Matplotlib axes to plot on
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
    
    def get_plot_limits(self, shadows: List[Shadow]) -> tuple[float, float, float, float]:
        """Calculate plot limits to encompass all shadows.
        
        Args:
            shadows: List of shadows to consider
            
        Returns:
            Tuple of (x_min, x_max, y_min, y_max)
        """
        all_x = []
        all_y = []
        for shadow in shadows:
            all_x.extend(v.x.magnitude for v in shadow.vertices)
            all_y.extend(v.y.magnitude for v in shadow.vertices)
            
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
        unit = str(shadows[0].wall.start_point.x.units)
        ax.set_xlabel(f'Distance ({unit})')
        ax.set_ylabel(f'Distance ({unit})')
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.3)
