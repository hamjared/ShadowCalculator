from dataclasses import dataclass
from typing import Optional
from .Point import Point, ureg
import numpy as np

@dataclass
class Wall:
    """Represents a wall with a name, height, and start/end points."""
    name: str
    height: ureg.Quantity
    start_point: Point
    end_point: Point
    
    @classmethod
    def from_values(cls, name: str, height: float, height_unit: str,
                   start_x: float, start_y: float, end_x: float, end_y: float,
                   position_unit: str = "feet") -> "Wall":
        """Create a Wall from numerical values with units."""
        return cls(
            name=name,
            height=height * ureg(height_unit),
            start_point=Point.from_values(start_x, start_y, position_unit),
            end_point=Point.from_values(end_x, end_y, position_unit)
        )
    
    @classmethod
    def from_strings(cls, name: str, height_str: str,
                    start_x_str: str, start_y_str: str,
                    end_x_str: str, end_y_str: str) -> "Wall":
        """Create a Wall from string measurements like '10 feet'."""
        return cls(
            name=name,
            height=ureg(height_str),
            start_point=Point.from_strings(start_x_str, start_y_str),
            end_point=Point.from_strings(end_x_str, end_y_str)
        )
    
    @property
    def width(self) -> ureg.Quantity:
        """Calculate the width of the wall based on start and end points."""
        dx = self.end_point.x - self.start_point.x
        dy = self.end_point.y - self.start_point.y
        return np.sqrt(dx**2 + dy**2)
    
    @property
    def angle(self) -> float:
        """Calculate the angle of the wall in degrees from true north (clockwise)."""
        dx = self.end_point.x - self.start_point.x
        dy = self.end_point.y - self.start_point.y
        # Convert from math angle (counterclockwise from east) to compass angle (clockwise from north)
        angle_rad = np.arctan2(dy.magnitude, dx.magnitude)
        compass_angle = (90 - np.degrees(angle_rad)) % 360
        return compass_angle
    
    def to(self, unit: str) -> "Wall":
        """Convert all measurements to a different unit."""
        return Wall(
            name=self.name,
            height=self.height.to(unit),
            start_point=self.start_point.to(unit),
            end_point=self.end_point.to(unit)
        )