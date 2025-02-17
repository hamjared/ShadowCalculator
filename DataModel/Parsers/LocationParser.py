from typing import Dict, Any
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from ..Location import Location

class LocationParser:
    """Parser for location data from various formats."""
    
    @staticmethod
    def parse(location_data: Any) -> Location:
        """Parse location data from various formats.
        
        Args:
            location_data: Can be one of:
                - Dictionary with 'latitude' and 'longitude'
                - Dictionary with 'address'
                - String with 'latitude,longitude'
                - String with address
                
        Returns:
            Location object
            
        Raises:
            ValueError: If location data cannot be parsed
        """
        if isinstance(location_data, dict):
            return LocationParser._parse_dict(location_data)
        elif isinstance(location_data, str):
            return LocationParser._parse_string(location_data)
        else:
            raise ValueError(f"Unsupported location data type: {type(location_data)}")
    
    @staticmethod
    def _parse_dict(data: Dict[str, Any]) -> Location:
        """Parse location from a dictionary format."""
        # Try coordinates first
        if 'latitude' in data and 'longitude' in data:
            try:
                lat = float(data['latitude'])
                lon = float(data['longitude'])
                return LocationParser._from_coordinates(lat, lon)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid coordinates in dictionary: {str(e)}")
                
        # Try address
        elif 'address' in data:
            return LocationParser._from_address(str(data['address']))
            
        else:
            raise ValueError("Dictionary must contain either 'latitude' and 'longitude' or 'address'")
    
    @staticmethod
    def _parse_string(data: str) -> Location:
        """Parse location from a string format."""
        # Try parsing as coordinates first
        try:
            if ',' in data:
                lat, lon = map(float, data.strip().split(','))
                return LocationParser._from_coordinates(lat, lon)
        except ValueError:
            pass
            
        # If not coordinates, try as address
        return LocationParser._from_address(data)
    
    @staticmethod
    def _from_coordinates(latitude: float, longitude: float) -> Location:
        """Create Location from coordinates."""
        # Validate coordinates
        if not -90 <= latitude <= 90:
            raise ValueError(f"Invalid latitude: {latitude}. Must be between -90 and 90 degrees.")
        if not -180 <= longitude <= 180:
            raise ValueError(f"Invalid longitude: {longitude}. Must be between -180 and 180 degrees.")
            
        # Try to get address from coordinates
        try:
            geolocator = Nominatim(user_agent="shadow_calculator")
            location = geolocator.reverse(f"{latitude}, {longitude}", language="en")
            address = location.address if location else None
        except (GeocoderTimedOut, GeocoderUnavailable):
            address = None
            
        return Location(latitude=latitude, longitude=longitude, address=address)
    
    @staticmethod
    def _from_address(address: str) -> Location:
        """Create Location from address string."""
        try:
            geolocator = Nominatim(user_agent="shadow_calculator")
            location = geolocator.geocode(address)
            if location:
                return Location(
                    latitude=location.latitude,
                    longitude=location.longitude,
                    address=location.address
                )
            else:
                raise ValueError(f"Could not find coordinates for address: {address}")
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            raise ValueError(f"Error geocoding address: {str(e)}")
