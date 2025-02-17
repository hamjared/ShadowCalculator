from dataclasses import dataclass
from typing import List
from .Point import Point, ureg
import numpy as np

@dataclass
class Area:
    """Represents a polygon area defined by vertices.
    
    The vertices should be specified in counter-clockwise order to
    ensure proper area calculation and point-in-polygon testing.
    
    Attributes:
        name: Name of the area
        vertices: List of vertices defining the polygon
        units: Units for all vertex coordinates (e.g., 'feet', 'meters')
    """
    name: str
    vertices: List[List[float]]  # Raw vertex coordinates
    units: str
    
    def __post_init__(self):
        """Validate area data and convert vertices to Points."""
        if len(self.vertices) < 3:
            raise ValueError(
                f"Area must have at least 3 vertices, got {len(self.vertices)}"
            )
            
        # Validate vertex format
        for i, vertex in enumerate(self.vertices, 1):
            if not isinstance(vertex, list) or len(vertex) != 2:
                raise ValueError(
                    f"Vertex {i} must be a list of [x, y], got {vertex}"
                )
                
        # Validate units
        try:
            ureg.parse_units(self.units)
        except:
            raise ValueError(f"Invalid units: {self.units}")
            
        # Convert vertices to Points with units
        self._points = [
            Point(
                x=ureg.Quantity(x, self.units),
                y=ureg.Quantity(y, self.units)
            )
            for x, y in self.vertices
        ]
    
    @property
    def points(self) -> List[Point]:
        """Get vertices as Points with units."""
        return self._points
    
    @property
    def area(self) -> ureg.Quantity:
        """Calculate area of the polygon using the shoelace formula.
        
        Returns:
            Area in square units matching vertex coordinates
        """
        # Get vertex coordinates
        x = [v[0] for v in self.vertices]
        y = [v[1] for v in self.vertices]
        
        # Add first point to end to close polygon
        x.append(x[0])
        y.append(y[0])
        
        # Calculate area using shoelace formula
        area = 0.0
        for i in range(len(x) - 1):
            area += x[i] * y[i + 1] - x[i + 1] * y[i]
        area = abs(area) / 2
        
        # Return with proper units
        return ureg.Quantity(area, self.units + "²")
    
    def contains_point(self, point: Point) -> bool:
        """Check if a point lies within the area.
        
        Args:
            point: Point to test
            
        Returns:
            True if point is inside the area
            
        Note:
            Uses the ray casting algorithm. A point is inside if a ray
            cast from it crosses the polygon boundary an odd number of times.
        """
        # Convert point to area units
        point_x = point.x.to(self.units).magnitude
        point_y = point.y.to(self.units).magnitude
        
        # Get vertex coordinates
        x = [v[0] for v in self.vertices]
        y = [v[1] for v in self.vertices]
        
        # Add first point to end to close polygon
        x.append(x[0])
        y.append(y[0])
        
        # Ray casting algorithm
        inside = False
        for i in range(len(x) - 1):
            if ((y[i] > point_y) != (y[i + 1] > point_y) and
                point_x < (x[i + 1] - x[i]) * (point_y - y[i]) /
                         (y[i + 1] - y[i]) + x[i]):
                inside = not inside
                
        return inside
    
    def get_bounding_box(self) -> tuple[Point, Point]:
        """Get the bounding box of the area.
        
        Returns:
            Tuple of (min_point, max_point) defining the bounding box
        """
        x_coords = [v[0] for v in self.vertices]
        y_coords = [v[1] for v in self.vertices]
        
        x_min = min(x_coords)
        x_max = max(x_coords)
        y_min = min(y_coords)
        y_max = max(y_coords)
        
        return (
            Point(
                x=ureg.Quantity(x_min, self.units),
                y=ureg.Quantity(y_min, self.units)
            ),
            Point(
                x=ureg.Quantity(x_max, self.units),
                y=ureg.Quantity(y_max, self.units)
            )
        )