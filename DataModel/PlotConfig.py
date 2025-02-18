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
        x_limits: Optional tuple of (min, max) for x-axis
        y_limits: Optional tuple of (min, max) for y-axis
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
    x_limits: Optional[Tuple[float, float]] = None
    y_limits: Optional[Tuple[float, float]] = None
    
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
            
        # Validate axis limits if provided
        if self.x_limits is not None:
            if not isinstance(self.x_limits, (list, tuple)) or len(self.x_limits) != 2:
                raise ValueError("x_limits must be a tuple of (min, max)")
            if self.x_limits[0] >= self.x_limits[1]:
                raise ValueError("x_limits[0] must be less than x_limits[1]")
            self.x_limits = tuple(self.x_limits)
            
        if self.y_limits is not None:
            if not isinstance(self.y_limits, (list, tuple)) or len(self.y_limits) != 2:
                raise ValueError("y_limits must be a tuple of (min, max)")
            if self.y_limits[0] >= self.y_limits[1]:
                raise ValueError("y_limits[0] must be less than y_limits[1]")
            self.y_limits = tuple(self.y_limits)
    
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
        x_limits: [min, max]
        y_limits: [min, max]
        """
        # Handle figure size specially
        if 'figure_size' in data:
            size = data['figure_size']
            if not isinstance(size, list) or len(size) != 2:
                raise ValueError("figure_size must be [width, height]")
            data['figure_size'] = tuple(size)
            
        # Handle axis limits specially
        if 'x_limits' in data and data['x_limits'] is not None:
            data['x_limits'] = tuple(data['x_limits'])
        if 'y_limits' in data and data['y_limits'] is not None:
            data['y_limits'] = tuple(data['y_limits'])
            
        # Use dataclass defaults for missing values
        return cls(**{
            k: v for k, v in data.items()
            if k in PlotConfig.__annotations__
        })
