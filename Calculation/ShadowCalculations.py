import math
import numpy as np
from typing import List, Tuple
from DataModel.Point import Point, ureg
from DataModel.Wall import Wall
from DataModel.Shadow import Shadow

class ShadowCalculations:
    """Static utility class for calculating shadow geometry."""
    
    @staticmethod
    def calculate_wall_direction(wall: Wall) -> float:
        """Calculate wall's direction in degrees clockwise from north.
        
        Args:
            wall: Wall to calculate direction for
            
        Returns:
            Direction in degrees (0-360)
        """
        # Get wall vector
        dx = wall.end_point.x - wall.start_point.x
        dy = wall.end_point.y - wall.start_point.y
        
        # Convert to angle (math angle is counterclockwise from east)
        math_angle = math.atan2(dy.magnitude, dx.magnitude)
        
        # Convert to compass angle (clockwise from north)
        compass_angle = (90 - math.degrees(math_angle)) % 360
        
        return compass_angle
    
    @staticmethod
    def is_sun_parallel(wall_direction: float, shadow_direction: float,
                       tolerance_degrees: float = 5) -> bool:
        """Check if sun direction is parallel to wall.
        
        Args:
            wall_direction: Wall direction in degrees
            shadow_direction: Shadow direction in degrees
            tolerance_degrees: Angle tolerance for parallel check
            
        Returns:
            True if sun is parallel (within tolerance)
        """
        # The shadow direction is opposite to the sun direction
        sun_direction = (shadow_direction + 180) % 360
        
        # Calculate angle between sun and wall
        angle_diff = abs((sun_direction - wall_direction) % 360)
        
        # Sun is parallel when angle is close to 0 or 180 degrees
        return (angle_diff <= tolerance_degrees or 
                abs(angle_diff - 180) <= tolerance_degrees)
    
    @staticmethod
    def is_sun_perpendicular(wall_direction: float, shadow_direction: float,
                            tolerance_degrees: float = 5) -> bool:
        """Check if sun direction is perpendicular to wall.
        
        Args:
            wall_direction: Wall direction in degrees
            shadow_direction: Shadow direction in degrees
            tolerance_degrees: Angle tolerance for perpendicular check
            
        Returns:
            True if sun is perpendicular (within tolerance)
        """
        # Calculate angle between wall and shadow
        angle_diff = abs((shadow_direction - wall_direction) % 360)
        print(f"Wall direction: {wall_direction:.1f}°")
        print(f"Shadow direction: {shadow_direction:.1f}°")
        print(f"Angle difference: {angle_diff:.1f}°")
        
        # For a north-south wall (0° or 180°), sun should be at 90° or 270° for perpendicular
        # For an east-west wall (90° or 270°), sun should be at 0° or 180° for perpendicular
        
        # The shadow direction is opposite to the sun direction
        sun_direction = (shadow_direction + 180) % 360
        angle_to_wall = abs((sun_direction - wall_direction) % 360)
        print(f"Sun direction: {sun_direction:.1f}°")
        print(f"Angle to wall: {angle_to_wall:.1f}°")
        
        # Check if angle is close to 90 or 270 degrees
        is_perp = (abs(angle_to_wall - 90) <= tolerance_degrees or 
                  abs(angle_to_wall - 270) <= tolerance_degrees)
        print(f"Is perpendicular: {is_perp}")
        return is_perp
    
    @staticmethod
    def calculate_shadow_length(wall_height: ureg.Quantity, 
                              solar_elevation: float) -> ureg.Quantity:
        """Calculate shadow length based on wall height and sun elevation.
        
        Args:
            wall_height: Height of wall
            solar_elevation: Sun elevation in degrees
            
        Returns:
            Shadow length in same units as wall height
            
        Note:
            Uses the formula: length = height / tan(elevation)
            When sun is at horizon (0°), length is infinite
            When sun is overhead (90°), length is 0
        """
        # Convert elevation to radians
        elevation_rad = math.radians(solar_elevation)
        
        # Avoid division by zero when sun is at horizon
        if elevation_rad < 0.001:  # About 0.057 degrees
            return wall_height * 1000  # Very long shadow
            
        # Calculate length using trigonometry
        return wall_height / math.tan(elevation_rad)
    
    @staticmethod
    def calculate_shadow_direction(solar_azimuth: float) -> float:
        """Calculate shadow direction based on sun position.
        
        Args:
            solar_azimuth: Sun azimuth in degrees clockwise from north
            
        Returns:
            Shadow direction in degrees (0-360)
            
        Note:
            Shadow direction is opposite to sun direction
        """
        return (solar_azimuth + 180) % 360
    
    @staticmethod
    def calculate_shadow_vertices(wall: Wall, shadow_length: ureg.Quantity,
                                shadow_direction: float) -> List[Point]:
        """Calculate shadow vertices based on wall and shadow geometry.
        
        Args:
            wall: Wall casting the shadow
            shadow_length: Length of shadow
            shadow_direction: Direction of shadow in degrees
            
        Returns:
            List of points forming shadow polygon.
            If sun is parallel to wall: triangular shadow
            Otherwise: parallelogram shadow
        """
        # Get wall direction
        wall_direction = ShadowCalculations.calculate_wall_direction(wall)
        
        # Convert shadow direction to radians
        direction_rad = math.radians(shadow_direction)
        
        # Calculate shadow offset
        dx = shadow_length * math.sin(direction_rad)
        dy = shadow_length * math.cos(direction_rad)
        
        # Create offset quantities
        dx = ureg.Quantity(dx, shadow_length.units)
        dy = ureg.Quantity(dy, shadow_length.units)
        
        # Check if sun is parallel to wall
        if ShadowCalculations.is_sun_parallel(wall_direction, shadow_direction):
            # Create triangular shadow (sun parallel to wall)
            # Use wall midpoint for shadow end
            wall_mid_x = (wall.start_point.x + wall.end_point.x) / 2
            wall_mid_y = (wall.start_point.y + wall.end_point.y) / 2
            
            shadow_end = Point(
                x=wall_mid_x + dx,
                y=wall_mid_y + dy
            )
            
            # Return triangular shadow vertices
            return [
                wall.start_point,    # Wall start
                wall.end_point,      # Wall end
                shadow_end,          # Shadow end point
                wall.start_point     # Back to start to close polygon
            ]
        else:
            # Create parallelogram shadow (normal case)
            # Each wall point casts a shadow in the same direction
            shadow_start = Point(
                x=wall.start_point.x + dx,
                y=wall.start_point.y + dy
            )
            shadow_end = Point(
                x=wall.end_point.x + dx,
                y=wall.end_point.y + dy
            )
            
            # Return parallelogram vertices
            return [
                wall.start_point,    # Wall start
                wall.end_point,      # Wall end
                shadow_end,          # Shadow end
                shadow_start,        # Shadow start
                wall.start_point     # Back to start to close polygon
            ]
    
    @staticmethod
    def calculate_shadow(wall: Wall, solar_elevation: float, 
                        solar_azimuth: float, time) -> Shadow:
        """Calculate complete shadow for a wall.
        
        Args:
            wall: Wall casting the shadow
            solar_elevation: Sun elevation in degrees
            solar_azimuth: Sun azimuth in degrees
            time: Time of calculation
            
        Returns:
            Shadow object with complete geometry
        """
        # Calculate shadow length
        shadow_length = ShadowCalculations.calculate_shadow_length(
            wall_height=wall.height,
            solar_elevation=solar_elevation
        )
        
        # Calculate shadow direction
        shadow_direction = ShadowCalculations.calculate_shadow_direction(
            solar_azimuth=solar_azimuth
        )
        
        # Calculate shadow vertices
        vertices = ShadowCalculations.calculate_shadow_vertices(
            wall=wall,
            shadow_length=shadow_length,
            shadow_direction=shadow_direction
        )
        
        # Create shadow object
        return Shadow(
            wall=wall,
            time=time,
            vertices=vertices,
            solar_elevation=solar_elevation,
            solar_azimuth=solar_azimuth
        )
