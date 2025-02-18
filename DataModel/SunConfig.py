from dataclasses import dataclass
from typing import Optional

@dataclass
class SunConfig:
    """Configuration for sun position calculation.
    
    If override_position is True, uses fixed elevation and azimuth
    instead of calculating from location and time.
    
    Attributes:
        override_position: Whether to use fixed position
        elevation: Fixed elevation in degrees (0-90)
        azimuth: Fixed azimuth in degrees (0-360)
    """
    override_position: bool = False
    elevation: Optional[float] = None
    azimuth: Optional[float] = None
    
    def __post_init__(self):
        """Validate configuration."""
        if self.override_position:
            if self.elevation is None or self.azimuth is None:
                raise ValueError(
                    "When override_position is True, "
                    "both elevation and azimuth must be specified"
                )
            if not 0 <= self.elevation <= 90:
                raise ValueError(
                    f"Invalid elevation: {self.elevation}. "
                    "Must be between 0 and 90 degrees"
                )
            if not 0 <= self.azimuth <= 360:
                raise ValueError(
                    f"Invalid azimuth: {self.azimuth}. "
                    "Must be between 0 and 360 degrees"
                )
    
    @classmethod
    def from_dict(cls, data: dict) -> "SunConfig":
        """Create SunConfig from dictionary.
        
        The dictionary can contain:
        override_position: bool
        elevation: float
        azimuth: float
        """
        return cls(**{
            k: v for k, v in data.items()
            if k in SunConfig.__annotations__
        })
