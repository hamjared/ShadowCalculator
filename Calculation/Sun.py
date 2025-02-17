from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Tuple
from astral import LocationInfo
from astral.sun import sun, azimuth, elevation
import math

@dataclass
class SunPosition:
    """Represents the sun's position in the sky.
    
    Attributes:
        azimuth: Degrees clockwise from north (0-360)
        elevation: Degrees above horizon (0-90)
        time: Time of calculation
    """
    azimuth: float
    elevation: float
    time: datetime
    
    def __str__(self) -> str:
        """Return string representation."""
        return (
            f"Sun position at {self.time.strftime('%Y-%m-%d %H:%M %Z')}:\n"
            f"  Azimuth: {self.azimuth:.1f}° from north\n"
            f"  Elevation: {self.elevation:.1f}° above horizon"
        )

class Sun:
    """Static utility class for calculating sun position."""
    
    @staticmethod
    def validate_coordinates(latitude: float, longitude: float) -> None:
        """Validate latitude and longitude.
        
        Args:
            latitude: Latitude in degrees (-90 to 90)
            longitude: Longitude in degrees (-180 to 180)
            
        Raises:
            ValueError: If coordinates are invalid
        """
        if not -90 <= latitude <= 90:
            raise ValueError(f"Invalid latitude: {latitude}. Must be between -90 and 90.")
        if not -180 <= longitude <= 180:
            raise ValueError(f"Invalid longitude: {longitude}. Must be between -180 and 180.")
    
    @staticmethod
    def get_location_info(latitude: float, longitude: float) -> LocationInfo:
        """Create LocationInfo for coordinates.
        
        Args:
            latitude: Latitude in degrees (-90 to 90)
            longitude: Longitude in degrees (-180 to 180)
            
        Returns:
            LocationInfo object for calculations
        """
        Sun.validate_coordinates(latitude, longitude)
        return LocationInfo(
            name='',
            region='',
            timezone='UTC',  # Use UTC for calculations
            latitude=latitude,
            longitude=longitude
        )
    
    @staticmethod
    def get_position(latitude: float, longitude: float, time: datetime) -> SunPosition:
        """Get sun position at specified time and location.
        
        Args:
            latitude: Latitude in degrees (-90 to 90)
            longitude: Longitude in degrees (-180 to 180)
            time: Time to calculate position for (must be timezone-aware)
            
        Returns:
            SunPosition with azimuth and elevation
            
        Raises:
            ValueError: If coordinates are invalid or time is not timezone-aware
        """
        if time.tzinfo is None:
            raise ValueError("Time must be timezone-aware")
            
        location = Sun.get_location_info(latitude, longitude)
        
        # Calculate azimuth and elevation
        az = azimuth(location.observer, time)
        el = elevation(location.observer, time)
        
        return SunPosition(
            azimuth=az,
            elevation=el,
            time=time
        )
    
    @staticmethod
    def get_day_positions(latitude: float, longitude: float, 
                         date: datetime, interval_minutes: int = 60) -> list[SunPosition]:
        """Get sun positions throughout the day.
        
        Args:
            latitude: Latitude in degrees (-90 to 90)
            longitude: Longitude in degrees (-180 to 180)
            date: Date to calculate positions for (time component is ignored)
            interval_minutes: Minutes between calculations
            
        Returns:
            List of SunPosition objects for daylight hours
            
        Raises:
            ValueError: If coordinates are invalid or date is not timezone-aware
        """
        if date.tzinfo is None:
            raise ValueError("Date must be timezone-aware")
            
        location = Sun.get_location_info(latitude, longitude)
        
        # Get sun events for the day
        events = sun(location.observer, date)
        
        # Generate times from sunrise to sunset
        positions = []
        current = events['sunrise']
        while current <= events['sunset']:
            # Only include positions where sun is above horizon
            el = elevation(location.observer, current)
            if el > 0:
                az = azimuth(location.observer, current)
                positions.append(SunPosition(
                    azimuth=az,
                    elevation=el,
                    time=current
                ))
            # Add interval using timedelta
            current = current + timedelta(minutes=interval_minutes)
            
        return positions
    
    @staticmethod
    def get_sunrise_sunset(latitude: float, longitude: float, 
                          date: datetime) -> Tuple[datetime, datetime]:
        """Get sunrise and sunset times for a date.
        
        Args:
            latitude: Latitude in degrees (-90 to 90)
            longitude: Longitude in degrees (-180 to 180)
            date: Date to get times for (time component is ignored)
            
        Returns:
            Tuple of (sunrise, sunset) times
            
        Raises:
            ValueError: If coordinates are invalid or date is not timezone-aware
        """
        if date.tzinfo is None:
            raise ValueError("Date must be timezone-aware")
            
        location = Sun.get_location_info(latitude, longitude)
        events = sun(location.observer, date)
        return events['sunrise'], events['sunset']
    
    @staticmethod
    def is_daytime(latitude: float, longitude: float, time: datetime) -> bool:
        """Check if sun is above horizon at specified time and location.
        
        Args:
            latitude: Latitude in degrees (-90 to 90)
            longitude: Longitude in degrees (-180 to 180)
            time: Time to check (must be timezone-aware)
            
        Returns:
            True if sun is above horizon
            
        Raises:
            ValueError: If coordinates are invalid or time is not timezone-aware
        """
        if time.tzinfo is None:
            raise ValueError("Time must be timezone-aware")
            
        location = Sun.get_location_info(latitude, longitude)
        return elevation(location.observer, time) > 0
