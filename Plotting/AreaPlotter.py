from typing import List
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.axes import Axes
from DataModel.Area import Area
from DataModel.PlotConfig import PlotConfig

class AreaPlotter:
    """Class for plotting areas."""
    
    def __init__(self, config: PlotConfig):
        """Initialize with plot configuration.
        
        Args:
            config: Plot configuration
        """
        self.config = config
    
    def plot_area(self, area: Area, ax: Axes, show_name: bool = True) -> None:
        """Plot a single area.
        
        Args:
            area: Area to plot
            ax: Matplotlib axes to plot on
            show_name: Whether to show area name
        """
        # Convert vertices to output units
        vertices = []
        for vertex in area.vertices:
            x = self.config.convert_to_output_units(
                area.points[0].x.__class__(vertex[0], area.units)
            ).magnitude
            y = self.config.convert_to_output_units(
                area.points[0].y.__class__(vertex[1], area.units)
            ).magnitude
            vertices.append([x, y])
        
        # Add first vertex to close polygon
        vertices.append(vertices[0])
        
        # Split into x and y coordinates
        x_coords = [v[0] for v in vertices]
        y_coords = [v[1] for v in vertices]
        
        # Plot area outline
        ax.plot(
            x_coords,
            y_coords,
            'g-',  # Green solid line
            linewidth=1.5,
            label=f'Area: {area.name}'
        )
        
        # Fill area with semi-transparent color
        polygon = patches.Polygon(
            vertices,
            facecolor='green',
            alpha=0.1,
            edgecolor='none'
        )
        ax.add_patch(polygon)
        
        # Add area name if requested
        if show_name:
            # Calculate centroid for label position
            center_x = sum(x_coords[:-1]) / (len(x_coords) - 1)
            center_y = sum(y_coords[:-1]) / (len(y_coords) - 1)
            
            # Calculate area in output units
            area_in_input_units = area.area
            area_in_output_units = (
                area_in_input_units.to(self.config.output_units + "²")
            )
            
            # Add area name and size
            ax.annotate(
                f"{area.name}\n{area_in_output_units:.1f~P}",
                (center_x, center_y),
                ha='center',
                va='center',
                bbox=dict(
                    facecolor='white',
                    alpha=0.7,
                    edgecolor='green',
                    boxstyle='round'
                )
            )
    
    def plot_areas(self, areas: List[Area], ax: Axes, show_names: bool = True) -> None:
        """Plot multiple areas.
        
        Args:
            areas: List of areas to plot
            ax: Matplotlib axes to plot on
            show_names: Whether to show area names
        """
        for area in areas:
            self.plot_area(area, ax, show_names)
    
    def get_plot_limits(self, areas: List[Area]) -> tuple[float, float, float, float]:
        """Calculate plot limits to encompass all areas.
        
        Args:
            areas: List of areas to consider
            
        Returns:
            Tuple of (x_min, x_max, y_min, y_max) in output units
        """
        if not areas:
            return 0, 0, 0, 0
            
        # Get all vertices
        all_vertices = []
        for area in areas:
            for vertex in area.vertices:
                x = self.config.convert_to_output_units(
                    area.points[0].x.__class__(vertex[0], area.units)
                ).magnitude
                y = self.config.convert_to_output_units(
                    area.points[0].y.__class__(vertex[1], area.units)
                ).magnitude
                all_vertices.append([x, y])
        
        # Calculate limits
        x_coords = [v[0] for v in all_vertices]
        y_coords = [v[1] for v in all_vertices]
        
        x_min = min(x_coords)
        x_max = max(x_coords)
        y_min = min(y_coords)
        y_max = max(y_coords)
        
        return x_min, x_max, y_min, y_max
