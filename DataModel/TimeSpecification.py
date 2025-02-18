from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Generator, Tuple
import zoneinfo
import re

@dataclass
class TimeSpecification:
    """Specifies time(s) for shadow calculation.
    
    Can represent either:
    1. A single point in time
    2. A range of times with an interval
    
    All times must include timezone information. If not provided,
    times are assumed to be in the specified default_timezone.
    """
    
    # For single time calculation
    point_time: Optional[datetime] = None
    
    # For time range calculation
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    interval: Optional[timedelta] = None
    
    # Default timezone for times without zone info
    default_timezone: str = "America/Denver"
    
    def __post_init__(self):
        """Validate the time specification and ensure timezone information."""
        # Check that we have either point_time or a complete range
        if self.point_time is not None:
            if any([self.start_time, self.end_time, self.interval]):
                raise ValueError("Cannot specify both point time and time range")
        else:
            if not all([self.start_time, self.end_time, self.interval]):
                raise ValueError("Must specify all range parameters (start, end, interval) or none")
        
        # Validate timezone
        try:
            tz = zoneinfo.ZoneInfo(self.default_timezone)
        except zoneinfo.ZoneInfoNotFoundError:
            raise ValueError(f"Invalid timezone: {self.default_timezone}")
        
        # Ensure all times have timezone info
        if self.point_time:
            if self.point_time.tzinfo is None:
                self.point_time = self.point_time.replace(tzinfo=tz)
        if self.start_time:
            if self.start_time.tzinfo is None:
                self.start_time = self.start_time.replace(tzinfo=tz)
            if self.end_time.tzinfo is None:
                self.end_time = self.end_time.replace(tzinfo=tz)
            
            # Validate range
            if self.end_time <= self.start_time:
                raise ValueError("End time must be after start time")
            if self.interval <= timedelta(0):
                raise ValueError("Interval must be positive")
            
            # Check range size
            total_points = (self.end_time - self.start_time) / self.interval
            if total_points > 1000:
                raise ValueError(
                    f"Time range too large: would generate {total_points:.0f} points. "
                    "Maximum is 1000 points."
                )
    
    @property
    def is_point(self) -> bool:
        """Return True if this is a point time specification."""
        return self.point_time is not None
    
    @property
    def is_range(self) -> bool:
        """Return True if this is a range time specification."""
        return self.start_time is not None
    
    def get_times(self) -> Generator[datetime, None, None]:
        """Get all times specified.
        
        For point time, yields a single time.
        For time range, yields times from start to end at given interval.
        
        Yields:
            datetime objects with timezone information
        """
        if self.is_point:
            yield self.point_time
        else:
            current = self.start_time
            while current <= self.end_time:
                yield current
                current += self.interval
    
    def get_progress_info(self) -> Tuple[int, str]:
        """Get information about the number of points and time format.
        
        Returns:
            Tuple of (number of points, human readable description)
        """
        if self.is_point:
            return 1, "single time point"
        else:
            points = len(list(self.get_times()))
            duration = self.end_time - self.start_time
            hours = duration.total_seconds() / 3600
            return points, f"{points} points over {hours:.1f} hours"
    
    @classmethod
    def parse_interval(cls, interval_str: str) -> timedelta:
        """Parse an interval string into a timedelta.
        
        Formats supported:
        - <number>m: minutes (e.g., "30m")
        - <number>h: hours (e.g., "1h")
        
        Args:
            interval_str: Interval string to parse
            
        Returns:
            timedelta object
            
        Raises:
            ValueError: If format is invalid
        """
        match = re.match(r"^(\d+)([mh])$", interval_str)
        if not match:
            raise ValueError(
                f"Invalid interval format: {interval_str}. "
                "Use <number>m for minutes or <number>h for hours"
            )
            
        value = int(match.group(1))
        unit = match.group(2)
        
        if unit == 'm':
            return timedelta(minutes=value)
        else:  # unit == 'h'
            return timedelta(hours=value)
    
    @classmethod
    def from_dict(cls, data: dict, default_timezone: str = "America/Denver") -> "TimeSpecification":
        """Create a TimeSpecification from a dictionary.
        
        The dictionary should have one of:
        1. 'point': A single time string
        2. 'start', 'end', 'interval': Range parameters
        
        Time strings should be in ISO format with optional timezone.
        If no timezone is specified, default_timezone is used.
        
        Args:
            data: Dictionary with time specification
            default_timezone: Timezone to use if none specified in times
            
        Returns:
            TimeSpecification object
            
        Raises:
            ValueError: If data format is invalid
        """
        if 'point' in data:
            return cls(
                point_time=datetime.fromisoformat(data['point']),
                default_timezone=default_timezone
            )
            
        # Parse interval
        interval = cls.parse_interval(data.get('interval', '30m'))
            
        return cls(
            start_time=datetime.fromisoformat(data['start']),
            end_time=datetime.fromisoformat(data['end']),
            interval=interval,
            default_timezone=default_timezone
        )
