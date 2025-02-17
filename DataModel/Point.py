from dataclasses import dataclass
from typing import Optional
from pint import UnitRegistry

# Create a unit registry for the entire module
ureg = UnitRegistry()

@dataclass
class Point:
    """Represents a 2D point with measurements that include units."""
    x: ureg.Quantity
    y: ureg.Quantity
    
    @classmethod
    def from_values(cls, x: float, y: float, unit: str = "feet") -> "Point":
        """Create a Point from x,y values with an optional unit."""
        return cls(
            x=x * ureg(unit),
            y=y * ureg(unit)
        )
    
    @classmethod
    def from_strings(cls, x_str: str, y_str: str) -> "Point":
        """Create a Point from strings like '5 feet' and '3 meters'."""
        return cls(
            x=ureg(x_str),
            y=ureg(y_str)
        )
    
    def to(self, unit: str) -> "Point":
        """Convert point coordinates to a different unit."""
        return Point(
            x=self.x.to(unit),
            y=self.y.to(unit)
        )
    
    def __str__(self) -> str:
        return f"Point(x={self.x}, y={self.y})"
