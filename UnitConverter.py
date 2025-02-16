"""
Unit conversion utilities for the shadow calculator.
Handles conversion between different units of measurement.
"""

from typing import Tuple, Dict

class UnitConverter:
    """Handles conversion between different units of measurement."""
    
    # Dictionary of conversion factors to meters
    UNIT_CONVERSIONS: Dict[str, float] = {
        'meters': 1.0,
        'm': 1.0,
        'feet': 0.3048,
        'ft': 0.3048,
        'inches': 0.0254,
        'in': 0.0254,
        'centimeters': 0.01,
        'cm': 0.01
    }
    
    @classmethod
    def get_supported_units(cls) -> list:
        """
        Get a list of supported unit names.
        
        Returns:
            list: List of supported unit names
        """
        return sorted(cls.UNIT_CONVERSIONS.keys())
    
    @classmethod
    def is_valid_unit(cls, unit: str) -> bool:
        """
        Check if a unit is supported.
        
        Args:
            unit: Unit name to check
            
        Returns:
            bool: True if unit is supported, False otherwise
        """
        return unit.lower() in cls.UNIT_CONVERSIONS
    
    @classmethod
    def convert_to_meters(cls, value: float, unit: str) -> float:
        """
        Convert a value from given unit to meters.
        
        Args:
            value: The numerical value to convert
            unit: The unit to convert from (must be in UNIT_CONVERSIONS)
            
        Returns:
            float: The value converted to meters
            
        Raises:
            ValueError: If unit is not supported
        """
        unit = unit.lower()
        if not cls.is_valid_unit(unit):
            raise ValueError(
                f"Unsupported unit: {unit}. Supported units are: "
                f"{', '.join(cls.get_supported_units())}"
            )
        return value * cls.UNIT_CONVERSIONS[unit]
    
    @classmethod
    def convert_from_meters(cls, value: float, unit: str) -> float:
        """
        Convert a value from meters to the target unit.
        
        Args:
            value: The value in meters
            unit: The unit to convert to (must be in UNIT_CONVERSIONS)
            
        Returns:
            float: The converted value
            
        Raises:
            ValueError: If unit is not supported
        """
        unit = unit.lower()
        if not cls.is_valid_unit(unit):
            raise ValueError(
                f"Unsupported unit: {unit}. Supported units are: "
                f"{', '.join(cls.get_supported_units())}"
            )
        return value / cls.UNIT_CONVERSIONS[unit]
    
    @classmethod
    def parse_value_with_unit(cls, value_str: str) -> Tuple[float, str]:
        """
        Parse a string containing a value and unit (e.g., "10 feet").
        
        Args:
            value_str: String containing value and unit separated by space
            
        Returns:
            Tuple[float, str]: Tuple of (value, unit)
            
        Raises:
            ValueError: If format is invalid or unit is not supported
        """
        try:
            value, unit = value_str.split()
            value = float(value)
            if not cls.is_valid_unit(unit):
                raise ValueError(
                    f"Unsupported unit: {unit}. Supported units are: "
                    f"{', '.join(cls.get_supported_units())}"
                )
            return value, unit
        except ValueError as e:
            if "not enough values to unpack" in str(e):
                raise ValueError(
                    "Please provide both value and unit, separated by space "
                    "(e.g., '10 feet')"
                )
            if "could not convert string to float" in str(e):
                raise ValueError(f"Invalid number format: {value_str.split()[0]}")
            raise
