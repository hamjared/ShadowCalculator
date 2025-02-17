from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class Location:
    """Represents a geographic location with latitude and longitude."""
    latitude: float
    longitude: float
    address: Optional[str] = None
    
    def __post_init__(self):
        """Validate coordinates after initialization."""
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Invalid latitude: {self.latitude}. Must be between -90 and 90 degrees.")
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Invalid longitude: {self.longitude}. Must be between -180 and 180 degrees.")
    
    def __str__(self) -> str:
        """Return string representation of the location."""
        if self.address:
            return f"{self.address} ({self.latitude:.6f}°, {self.longitude:.6f}°)"
        return f"{self.latitude:.6f}°, {self.longitude:.6f}°"
    
    def to_tuple(self) -> Tuple[float, float]:
        """Return latitude and longitude as a tuple."""
        return (self.latitude, self.longitude)