from dataclasses import dataclass
from typing import Optional, Tuple
import zoneinfo
import datetime
from pint import UnitRegistry

# Create unit registry
ureg = UnitRegistry()

@dataclass
class PlotConfig:
    """Configuration for shadow plot generation.
    
    Attributes:
        enabled: Whether to generate plots
        save_path: Path to save plots (if None, display instead)
        figure_size: Size of figure in inches (width, height)
        show_compass: Whether to show compass directions
        show_sun: Whether to show sun position
        show_dimensions: Whether to show wall and shadow dimensions
        dpi: DPI for saved plots
        timezone: Timezone for displaying times (e.g., "America/Denver")
                 If None, uses system timezone
        output_units: Units to use for plot dimensions (e.g., "meters", "feet")
                     All measurements will be converted to these units
    """
    enabled: bool = False
    save_path: Optional[str] = None
    figure_size: Tuple[int, int] = (10, 10)
    show_compass: bool = True
    show_sun: bool = True
    show_dimensions: bool = True
    dpi: int = 300
    timezone: Optional[str] = None
    output_units: str = "meters"
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        # If no timezone specified, use system timezone
        if self.timezone is None:
            self.timezone = str(datetime.datetime.now().astimezone().tzinfo)
        
        # Validate timezone
        try:
            zoneinfo.ZoneInfo(self.timezone)
        except zoneinfo.ZoneInfoNotFoundError:
            raise ValueError(f"Invalid timezone: {self.timezone}")
            
        # Validate output units
        try:
            # Try to parse units to validate them
            ureg.parse_units(self.output_units)
        except:
            raise ValueError(
                f"Invalid output units: {self.output_units}. "
                "Must be a valid unit of length (e.g., 'meters', 'feet')"
            )
    
    def convert_to_output_units(self, quantity) -> ureg.Quantity:
        """Convert a quantity to the output units.
        
        Args:
            quantity: A Pint quantity to convert
            
        Returns:
            Quantity in output units
            
        Raises:
            ValueError: If quantity cannot be converted to output units
        """
        try:
            return quantity.to(self.output_units)
        except:
            raise ValueError(
                f"Cannot convert {quantity} to {self.output_units}. "
                "Make sure both units are measures of length."
            )
    
    def format_time(self, time: datetime.datetime) -> str:
        """Format a time in the configured timezone.
        
        Args:
            time: Time to format (must be timezone-aware)
            
        Returns:
            Formatted time string
        """
        if time.tzinfo is None:
            raise ValueError("Time must be timezone-aware")
            
        # Convert to configured timezone
        local_time = time.astimezone(zoneinfo.ZoneInfo(self.timezone))
        return local_time.strftime('%Y-%m-%d %H:%M %Z')
    
    @classmethod
    def from_dict(cls, data: dict) -> "PlotConfig":
        """Create PlotConfig from dictionary.
        
        The dictionary can contain:
        enabled: bool
        save_path: str
        figure_size: [width, height]
        show_compass: bool
        show_sun: bool
        show_dimensions: bool
        dpi: int
        timezone: str
        output_units: str
        """
        # Handle figure size specially
        if 'figure_size' in data:
            size = data['figure_size']
            if not isinstance(size, list) or len(size) != 2:
                raise ValueError("figure_size must be [width, height]")
            data['figure_size'] = tuple(size)
            
        # Use dataclass defaults for missing values
        return cls(**{
            k: v for k, v in data.items()
            if k in PlotConfig.__annotations__
        })
