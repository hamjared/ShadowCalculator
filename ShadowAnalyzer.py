import numpy as np
from matplotlib.patches import Polygon, Rectangle
from shapely.geometry import Polygon as ShapelyPolygon
from shapely.geometry import Point, box
from typing import List, Tuple, Dict, Optional
import matplotlib.pyplot as plt

class ShadowAnalyzer:
    """Class to analyze shadow coverage of defined areas."""
    
    def __init__(self):
        self.areas = {}  # Dictionary to store named areas
        
    def add_rectangular_area(self, name: str, center: Tuple[float, float], 
                           width: float, height: float, angle: float = 0) -> None:
        """
        Add a rectangular area to analyze for shadow coverage.
        
        Args:
            name: Unique identifier for the area
            center: (x, y) coordinates of rectangle center in meters from wall base
            width: Width of rectangle in meters
            height: Height of rectangle in meters
            angle: Angle of rectangle in degrees from true north (clockwise)
        """
        # Convert angle to radians
        angle_rad = np.radians(angle)
        
        # Calculate corners in compass coordinates (clockwise from north)
        # In compass coordinates: x = r * sin(theta), y = r * cos(theta)
        dx = width / 2
        dy = height / 2
        
        # Calculate corner points
        corners = [
            (-dx, -dy),  # Bottom left
            (dx, -dy),   # Bottom right
            (dx, dy),    # Top right
            (-dx, dy)    # Top left
        ]
        
        # Rotate corners
        rotated_corners = []
        for x, y in corners:
            rx = x * np.cos(angle_rad) - y * np.sin(angle_rad)
            ry = x * np.sin(angle_rad) + y * np.cos(angle_rad)
            rotated_corners.append((
                center[0] + rx,
                center[1] + ry
            ))
        
        print(f"DEBUG: Area {name} corners: {rotated_corners}")
        
        # Create shapely polygon for intersection calculations
        area_poly = ShapelyPolygon(rotated_corners)
        
        # Store area data
        self.areas[name] = {
            'polygon': area_poly,
            'corners': rotated_corners,
            'center': center,
            'width': width,
            'height': height,
            'angle': angle
        }
    
    def calculate_shadow_polygon(self, wall_width: float, wall_angle: float,
                               shadow_length: float, shadow_angle: float) -> ShapelyPolygon:
        """
        Calculate the shadow polygon for intersection tests.
        
        Args:
            wall_width: Width of the wall in meters
            wall_angle: Wall angle in degrees from true north (clockwise)
            shadow_length: Length of shadow in meters
            shadow_angle: Shadow angle in degrees from true north (clockwise)
            
        Returns:
            ShapelyPolygon representing the shadow area
        """
        # Convert angles to radians (compass coordinates: clockwise from north)
        wall_rad = np.radians(wall_angle)
        shadow_rad = np.radians(shadow_angle)
        
        # Calculate shadow vertices using compass coordinates
        # In compass coordinates: x = r * sin(theta), y = r * cos(theta)
        vertices = [
            (-wall_width/2 * np.sin(wall_rad), -wall_width/2 * np.cos(wall_rad)),  # Left wall point
            (wall_width/2 * np.sin(wall_rad), wall_width/2 * np.cos(wall_rad)),    # Right wall point
            (wall_width/2 * np.sin(wall_rad) + shadow_length * np.sin(shadow_rad),  # Right shadow point
             wall_width/2 * np.cos(wall_rad) + shadow_length * np.cos(shadow_rad)),
            (-wall_width/2 * np.sin(wall_rad) + shadow_length * np.sin(shadow_rad), # Left shadow point
             -wall_width/2 * np.cos(wall_rad) + shadow_length * np.cos(shadow_rad))
        ]
        
        print(f"DEBUG: Shadow vertices: {vertices}")
        return ShapelyPolygon(vertices)
    
    def analyze_shadow_coverage(self, wall_width: float, wall_angle: float,
                              shadow_length: float, shadow_angle: float) -> Dict[str, float]:
        """
        Analyze what percentage of each area is covered by the shadow.
        
        Args:
            wall_width: Width of the wall in meters
            wall_angle: Wall angle in degrees from true north (clockwise)
            shadow_length: Length of shadow in meters
            shadow_angle: Shadow angle in degrees from true north (clockwise)
            
        Returns:
            Dictionary mapping area names to coverage percentages (0-100)
        """
        shadow_poly = self.calculate_shadow_polygon(wall_width, wall_angle,
                                                  shadow_length, shadow_angle)
        
        coverage = {}
        for name, area in self.areas.items():
            area_poly = area['polygon']
            if area_poly.intersects(shadow_poly):
                intersection = area_poly.intersection(shadow_poly)
                coverage_pct = (intersection.area / area_poly.area) * 100
            else:
                coverage_pct = 0
            coverage[name] = coverage_pct
            
        return coverage
    
    def plot_areas(self, ax, coverage: Optional[Dict[str, float]] = None):
        """
        Plot the defined areas on the given matplotlib axis.
        
        Args:
            ax: Matplotlib axis to plot on
            coverage: Optional dictionary of coverage percentages to display
        """
        proxies = []
        labels = []
        for name, area in self.areas.items():
            # Create polygon patch with unique color
            color = plt.cm.Set3(hash(name) % 8)  # Use color from Set3 colormap
            poly = Polygon(area['corners'], 
                         facecolor=color, 
                         alpha=0.5,
                         edgecolor=color,
                         linewidth=2,
                         zorder=4)  # Above shadow but below sun
            ax.add_patch(poly)
            
            # Add to legend
            if coverage is not None:
                label = f"{name} ({coverage[name]:.1f}% covered)"
            else:
                label = name
            
            # Create proxy artist for legend
            proxy = plt.Rectangle((0, 0), 1, 1, 
                                facecolor=color,
                                alpha=0.5,
                                edgecolor=color,
                                linewidth=2)
            proxies.append(proxy)
            labels.append(label)
        
        ax.legend(proxies, labels, 
                 loc='upper left',
                 bbox_to_anchor=(1.02, 1),
                 borderaxespad=0.,
                 title='Areas',
                 framealpha=0.9,
                 handlelength=1.5,
                 handletextpad=0.5)
