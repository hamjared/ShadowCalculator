from dataclasses import dataclass
from datetime import datetime
from typing import List
import math
from .Point import Point, ureg
from .Wall import Wall

@dataclass
class Shadow:
    """Represents a shadow cast by a wall at a specific time.
    
    The shadow is defined by four vertices that form a quadrilateral.
    The vertices MUST be specified in the following order:
    
    vertices[0]: Wall start point
    vertices[1]: Wall end point
    vertices[2]: Shadow end point connected to wall start
    vertices[3]: Shadow end point connected to wall end
    
    This ordering creates two edges along the wall (0->1),
    two edges along the shadow sides (0->2 and 1->3),
    and one edge at the shadow's end (2->3).
    
    Visual representation:
    
        Wall Edge
    0 ------------- 1
    |               |
    |   Shadow     |
    |    Area      |
    |               |
    2 ------------- 3
      Shadow End
    
    This specific ordering is required for:
    1. Length calculation (uses wall midpoint to shadow end midpoint)
    2. Width calculation (uses distance between shadow end points)
    3. Area calculation (uses shoelace formula, order affects sign)
    4. Angle calculation (uses wall midpoint to shadow end midpoint)
    """
    
    # The wall casting this shadow
    wall: Wall
    
    # When this shadow was calculated
    time: datetime
    
    # The shadow's outline as a polygon
    vertices: List[Point]
    
    # Solar elevation when shadow was calculated (degrees)
    solar_elevation: float
    
    # Solar azimuth when shadow was calculated (degrees clockwise from north)
    solar_azimuth: float
    
    def __post_init__(self):
        """Validate the shadow data after initialization."""
        if len(self.vertices) != 4:
            raise ValueError(
                f"Shadow must have exactly 4 vertices, got {len(self.vertices)}"
            )
    
    @property
    def length(self) -> ureg.Quantity:
        """Calculate the length of the shadow.
        
        Uses the average distance from the wall's midpoint
        to the shadow's end midpoint.
        
        Requires vertices to be ordered as:
        - vertices[0], vertices[1]: Wall points
        - vertices[2], vertices[3]: Shadow end points
        """
        # Get wall midpoint
        wall_mid_x = (self.vertices[0].x + self.vertices[1].x) / 2
        wall_mid_y = (self.vertices[0].y + self.vertices[1].y) / 2
        
        # Get shadow end midpoint
        shadow_mid_x = (self.vertices[2].x + self.vertices[3].x) / 2
        shadow_mid_y = (self.vertices[2].y + self.vertices[3].y) / 2
        
        # Calculate distance
        dx = shadow_mid_x - wall_mid_x
        dy = shadow_mid_y - wall_mid_y
        
        # Return length (units are preserved through math operations)
        return (dx**2 + dy**2)**0.5
    
    @property
    def width(self) -> ureg.Quantity:
        """Calculate the width of the shadow at its end.
        
        Uses the distance between the last two vertices.
        
        Requires vertices to be ordered as:
        - vertices[2], vertices[3]: Shadow end points
        """
        # Calculate distance between shadow end points
        dx = self.vertices[3].x - self.vertices[2].x
        dy = self.vertices[3].y - self.vertices[2].y
        
        # Return width (units are preserved through math operations)
        return (dx**2 + dy**2)**0.5
    
    @property
    def area(self) -> ureg.Quantity:
        """Calculate the area of the shadow using the shoelace formula.
        
        The shoelace formula calculates the area of any polygon given its vertices:
        Area = 1/2 * |∑(x[i] * y[i+1] - x[i+1] * y[i])|
        where i goes from 0 to n-1 and index n is the same as index 0.
        
        Vertex order affects the sign of the area before absolute value is taken.
        The specified vertex ordering ensures a positive area.
        """
        # Get x and y coordinates
        x_coords = [v.x for v in self.vertices]
        y_coords = [v.y for v in self.vertices]
        
        # Add first point to end to close the polygon
        x_coords.append(x_coords[0])
        y_coords.append(y_coords[0])
        
        # Calculate area using shoelace formula
        area = 0
        for i in range(len(self.vertices)):
            area += x_coords[i] * y_coords[i+1]
            area -= y_coords[i] * x_coords[i+1]
        
        # Take absolute value and divide by 2
        return abs(area) / 2
    
    @property
    def angle(self) -> float:
        """Calculate the angle of the shadow in degrees clockwise from north.
        
        Uses the midpoint of the wall and the midpoint of the shadow's end
        to determine the direction the shadow is cast.
        
        Requires vertices to be ordered as:
        - vertices[0], vertices[1]: Wall points
        - vertices[2], vertices[3]: Shadow end points
        """
        # Get wall midpoint
        wall_mid_x = (self.vertices[0].x + self.vertices[1].x) / 2
        wall_mid_y = (self.vertices[0].y + self.vertices[1].y) / 2
        
        # Get shadow end midpoint
        shadow_mid_x = (self.vertices[2].x + self.vertices[3].x) / 2
        shadow_mid_y = (self.vertices[2].y + self.vertices[3].y) / 2
        
        # Calculate angle using arctangent
        dx = shadow_mid_x - wall_mid_x
        dy = shadow_mid_y - wall_mid_y
        
        # Convert from math angle (counterclockwise from east)
        # to compass angle (clockwise from north)
        math_angle = math.atan2(dy.magnitude, dx.magnitude)
        compass_angle = (90 - math.degrees(math_angle)) % 360
        
        return compass_angle
    
    def __str__(self) -> str:
        """Return string representation of the shadow."""
        return (
            f"Shadow of {self.wall.name} at {self.time.strftime('%Y-%m-%d %H:%M')}:\n"
            f"  Length: {self.length:~P}\n"  # ~P formats with units
            f"  Width: {self.width:~P}\n"
            f"  Area: {self.area:~P}\n"
            f"  Direction: {self.angle:.1f}° from north\n"
            f"  Sun position: {self.solar_azimuth:.1f}° azimuth, {self.solar_elevation:.1f}° elevation"
        )
    
    def to_dict(self) -> dict:
        """Convert shadow to dictionary format."""
        return {
            'wall_name': self.wall.name,
            'time': self.time.isoformat(),
            'length': str(self.length),
            'width': str(self.width),
            'area': str(self.area),
            'angle': self.angle,
            'solar_elevation': self.solar_elevation,
            'solar_azimuth': self.solar_azimuth,
            'vertices': [
                [str(p.x), str(p.y)] for p in self.vertices
            ]
        }
