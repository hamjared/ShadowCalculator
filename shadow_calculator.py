import astral
from astral.sun import sun, elevation, azimuth
from datetime import datetime, timedelta
import math
from typing import Tuple, Dict, List
import argparse
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import yaml
import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, Polygon, Circle
from matplotlib.animation import FuncAnimation
from InputFileParser import InputFileParser
from UnitConverter import UnitConverter
from datetime import timezone, timedelta

# Dictionary of conversion factors to meters
UNIT_CONVERSIONS = UnitConverter.UNIT_CONVERSIONS

def load_config() -> Dict:
    """
    Load configuration from config.yaml file.
    Creates default config if file doesn't exist.
    
    Returns:
        Dict: Configuration dictionary
    """
    config_path = Path(__file__).parent / 'config.yaml'
    
    # Default configuration
    default_config = {
        'output_units': {
            'default': 'meters',
            'height': 'meters',
            'shadow': 'meters'
        },
        'default_location': '39.7392,-104.9903'  # Denver
    }
    
    # Create default config if it doesn't exist
    if not config_path.exists():
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        return default_config
    
    # Load existing config
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Validate units
        for key in ['default', 'height', 'shadow']:
            unit = config['output_units'].get(key, 'meters').lower()
            if unit not in UNIT_CONVERSIONS and unit not in [u.lower() for u in UNIT_CONVERSIONS.keys()]:
                print(f"Warning: Invalid unit '{unit}' in config for {key}, using meters")
                config['output_units'][key] = 'meters'
                
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        print("Using default configuration")
        return default_config

def calculate_shadow_length(wall_height: float, wall_width: float, wall_angle: float, latitude: float, longitude: float, date_time: datetime) -> Tuple[float, float, float, float]:
    """
    Calculate the length, width, and direction of a shadow cast by a wall at a specific time and location.
    
    Args:
        wall_height: Height of the wall in meters
        wall_width: Width of the wall in meters
        wall_angle: Angle of the wall in degrees from true north (clockwise, 0-360)
        latitude: Latitude of the location in degrees
        longitude: Longitude of the location in degrees
        date_time: DateTime object representing the time to calculate for
        
    Returns:
        Tuple[float, float, float, float]: (shadow_length in meters, shadow_width in meters, 
                                          shadow_angle in degrees from true north, shadow_area in square meters)
        Returns None if sun is below horizon
    """
    # Create location object
    loc = astral.LocationInfo(latitude=latitude, longitude=longitude)
    
    # Calculate the sun's position
    solar_elevation = elevation(observer=loc.observer, dateandtime=date_time)
    solar_azimuth = azimuth(observer=loc.observer, dateandtime=date_time)
    
    print(f"DEBUG: Solar azimuth at {date_time}: {solar_azimuth}°")  # Debug print
    
    # Convert angles to radians
    elevation_rad = math.radians(solar_elevation)
    azimuth_rad = math.radians(solar_azimuth)
    wall_angle_rad = math.radians(wall_angle)
    
    # If sun is below horizon, return None
    if solar_elevation <= 0:
        return None
    
    # Calculate the relative angle between the sun and the wall
    relative_angle = abs(solar_azimuth - wall_angle)
    if relative_angle > 180:
        relative_angle = 360 - relative_angle
    relative_angle_rad = math.radians(relative_angle)
    
    # Calculate basic shadow length using elevation
    base_shadow_length = wall_height / math.tan(elevation_rad)
    
    # Adjust shadow length based on wall orientation
    # When sun is parallel to wall, shadow is shortest
    # When sun is perpendicular to wall, shadow is longest
    shadow_length = base_shadow_length * math.sin(relative_angle_rad)
    
    # Calculate shadow width
    # The wall's width creates a shadow that depends on the sun's position
    # When sun is perpendicular to wall, shadow width equals wall width
    # When sun is parallel to wall, shadow width is extended
    shadow_width = wall_width / math.cos(relative_angle_rad) if relative_angle_rad < math.pi/2 else wall_width
    
    # Calculate shadow angle (direction)
    # Shadow is cast in the opposite direction from the sun's azimuth
    shadow_angle = (solar_azimuth + 180) % 360  # Shadow points opposite to sun
    
    # Calculate shadow area (approximate as a trapezoid)
    shadow_area = (shadow_width * shadow_length)
    
    return shadow_length, shadow_width, shadow_angle, shadow_area

def calculate_shadow_range(
    wall_height: float,
    wall_width: float,
    wall_angle: float,
    latitude: float,
    longitude: float,
    start_time: datetime,
    end_time: datetime,
    time_step: timedelta
) -> list:
    """
    Calculate shadow dimensions for a range of times.
    
    Args:
        wall_height: Height of the wall in meters
        wall_width: Width of the wall in meters
        wall_angle: Angle of the wall in degrees from true north
        latitude: Latitude of the location
        longitude: Longitude of the location
        start_time: Start time for calculations
        end_time: End time for calculations
        time_step: Time interval between calculations
        
    Returns:
        list: List of tuples (time, shadow_length, shadow_width, shadow_angle, shadow_area)
    """
    results = []
    current_time = start_time
    
    while current_time <= end_time:
        shadow_result = calculate_shadow_length(
            wall_height, wall_width, wall_angle, latitude, longitude, current_time
        )
        
        if shadow_result is not None:
            length, width, angle, area = shadow_result
            results.append((current_time, length, width, angle, area))
            
        current_time += time_step
        
    return results

def parse_angle(angle_str: str) -> float:
    """
    Parse an angle string and ensure it's within 0-360 degrees.
    
    Args:
        angle_str: String containing angle in degrees
        
    Returns:
        float: Angle normalized to 0-360 degrees
    """
    try:
        angle = float(angle_str)
        return angle % 360
    except ValueError:
        raise ValueError("Angle must be a number (degrees from true north, 0-360)")

def get_coordinates(location: str) -> Tuple[float, float, str]:
    """
    Get coordinates from an address string using geocoding.
    
    Args:
        location: Address string or "lat,long" coordinates
        
    Returns:
        Tuple of (latitude, longitude, location_name)
    """
    # First try to parse as lat,long
    try:
        if ',' in location:
            lat, lon = map(float, location.split(','))
            try:
                # Reverse geocode to get location name
                geolocator = Nominatim(user_agent="shadow_calculator", timeout=5)
                location_obj = geolocator.reverse(f"{lat}, {lon}", language="en")
                if location_obj:
                    return lat, lon, location_obj.address
            except (GeocoderTimedOut, GeocoderUnavailable):
                pass
            return lat, lon, f"{lat:.4f}°, {lon:.4f}°"
    except ValueError:
        pass
    
    # If not lat,long, try geocoding the address
    try:
        geolocator = Nominatim(user_agent="shadow_calculator", timeout=5)
        location_obj = geolocator.geocode(location)
        if location_obj:
            return location_obj.latitude, location_obj.longitude, location_obj.address
    except (GeocoderTimedOut, GeocoderUnavailable):
        pass
    
    # If all else fails, use default coordinates (Denver, CO)
    default_lat, default_lon = 39.7392, -104.9903
    return default_lat, default_lon, "Denver, CO (default location)"

def parse_time(time_str: str) -> datetime:
    """
    Parse a time string into a datetime object.
    Accepts formats:
    - HH:MM
    - YYYY-MM-DD
    - YYYY-MM-DD HH:MM
    If only time is provided, uses current date.
    If only date is provided, uses 00:00 as time.
    All times are interpreted in the local timezone.
    
    Args:
        time_str: Time string in one of the supported formats
        
    Returns:
        datetime: Parsed datetime object with timezone information
    """
    try:
        now = datetime.now()
        
        # Try parsing as time only (HH:MM)
        try:
            time = datetime.strptime(time_str, "%H:%M").time()
            dt = datetime.combine(now.date(), time)
            # Add timezone offset for Denver (UTC-7)
            return dt.replace(tzinfo=timezone(timedelta(hours=-7)))
        except ValueError:
            pass
        
        # Try parsing as date only (YYYY-MM-DD)
        try:
            date = datetime.strptime(time_str, "%Y-%m-%d").date()
            dt = datetime.combine(date, datetime.min.time())
            return dt.replace(tzinfo=timezone(timedelta(hours=-7)))
        except ValueError:
            pass
        
        # Try parsing as full datetime (YYYY-MM-DD HH:MM)
        try:
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            return dt.replace(tzinfo=timezone(timedelta(hours=-7)))
        except ValueError:
            pass
        
        raise ValueError(f"Invalid time format: {time_str}")
    except Exception as e:
        raise ValueError(f"Error parsing time: {str(e)}")

def parse_duration(duration_str: str) -> timedelta:
    """
    Parse a duration string into a timedelta object.
    Format: <number><unit> where unit is m (minutes) or h (hours)
    
    Args:
        duration_str: Duration string (e.g., "30m" or "2h")
        
    Returns:
        timedelta: Parsed duration
    """
    try:
        if not duration_str[-1] in ['m', 'h']:
            raise ValueError()
            
        value = int(duration_str[:-1])
        unit = duration_str[-1]
        
        if unit == 'm':
            return timedelta(minutes=value)
        else:  # unit == 'h'
            return timedelta(hours=value)
            
    except (ValueError, IndexError):
        raise ValueError(
            "Invalid duration format. Use:\n"
            "- <number>m for minutes (e.g., 30m)\n"
            "- <number>h for hours (e.g., 2h)"
        )

def plot_shadow(wall_width: float, wall_angle: float, shadow_length: float, 
                shadow_width: float, shadow_angle: float, time: datetime = None,
                show: bool = True) -> tuple:
    """
    Plot the wall and its shadow.
    
    Args:
        wall_width: Width of the wall in meters
        wall_angle: Wall angle in degrees from true north (clockwise)
        shadow_length: Length of the shadow in meters
        shadow_width: Width of the shadow in meters
        shadow_angle: Shadow angle in degrees from true north (clockwise)
        time: Optional datetime for plot title
        show: Whether to show the plot immediately
    """
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Convert angles to radians (compass coordinates: clockwise from north)
    wall_rad = np.radians(wall_angle)
    shadow_rad = np.radians(shadow_angle)
    
    # Calculate shadow vertices using compass coordinates
    # In compass coordinates: x = r * sin(theta), y = r * cos(theta)
    vertices = [
        (-wall_width/2 * np.sin(wall_rad), -wall_width/2 * np.cos(wall_rad)),  # Left wall point
        (wall_width/2 * np.sin(wall_rad), wall_width/2 * np.cos(wall_rad)),    # Right wall point
        (wall_width/2 * np.sin(wall_rad) + shadow_length * np.sin(shadow_rad),  # Right shadow point
         wall_width/2 * np.cos(wall_rad) + shadow_length * np.cos(shadow_rad)),
        (-wall_width/2 * np.sin(wall_rad) + shadow_length * np.sin(shadow_rad), # Left shadow point
         -wall_width/2 * np.cos(wall_rad) + shadow_length * np.cos(shadow_rad))
    ]
    
    # Create patches
    shadow = Polygon(vertices, color='gray', alpha=0.3, zorder=1)
    
    # Create wall line
    wall_start = vertices[0]  # Left wall point
    wall_end = vertices[1]    # Right wall point
    wall_line = plt.Line2D([wall_start[0], wall_end[0]], 
                          [wall_start[1], wall_end[1]], 
                          color='black', 
                          linewidth=2,
                          zorder=2)
    
    # Add sun symbol at solar azimuth
    sun_angle = (shadow_angle + 180) % 360  # Sun is opposite the shadow
    sun_rad = np.radians(sun_angle)
    sun_radius = max(shadow_length, wall_width) * 1.2
    sun_x = sun_radius * np.sin(sun_rad)  # Compass coordinates
    sun_y = sun_radius * np.cos(sun_rad)  # Compass coordinates
    
    # Draw sun
    sun = plt.Circle((sun_x, sun_y), radius=sun_radius*0.05, 
                    color='orange', alpha=0.8, zorder=3)
    ax.add_patch(sun)
    
    # Add sun rays
    ray_length = sun_radius * 0.1
    for i in range(8):
        ray_angle = i * np.pi/4
        ray_dx = ray_length * np.cos(ray_angle)
        ray_dy = ray_length * np.sin(ray_angle)
        ax.add_line(plt.Line2D([sun_x - ray_dx, sun_x + ray_dx],
                              [sun_y - ray_dy, sun_y + ray_dy],
                              color='orange', alpha=0.8, zorder=3))
    
    # Add compass directions
    compass_radius = sun_radius
    compass_points = {
        'N': (0, compass_radius),
        'S': (0, -compass_radius),
        'E': (compass_radius, 0),
        'W': (-compass_radius, 0),
        'NE': (compass_radius * 0.707, compass_radius * 0.707),
        'SE': (compass_radius * 0.707, -compass_radius * 0.707),
        'SW': (-compass_radius * 0.707, -compass_radius * 0.707),
        'NW': (-compass_radius * 0.707, compass_radius * 0.707)
    }
    
    for direction, (x, y) in compass_points.items():
        ax.text(x, y, direction, ha='center', va='center')
    
    # Set title if time provided
    if time:
        title = f"Shadow at {time.strftime('%Y-%m-%d %H:%M')}\n"
        title += f"Sun azimuth: {sun_angle:.1f}°, Shadow angle: {shadow_angle:.1f}°"
        ax.set_title(title)
    
    # Set equal aspect ratio and limits
    ax.set_aspect('equal')
    limit = compass_radius * 1.1
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.3)
    
    # Add axes labels
    ax.set_xlabel('Distance (meters)')
    ax.set_ylabel('Distance (meters)')
    
    # Add patches to plot
    ax.add_patch(shadow)
    ax.add_line(wall_line)
    
    if show:
        plt.show()
    return fig, ax

def create_shadow_animation(results: list, wall_width: float, wall_angle: float, 
                          output_file: str = None) -> None:
    """
    Create an animation of shadow movement over time.
    
    Args:
        results: List of (time, shadow_length, shadow_width, shadow_angle) tuples
        wall_width: Width of the wall in meters
        wall_angle: Wall angle in degrees from true north
        output_file: Optional path to save animation file
    """
    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(10, 10))
    
    def update(frame):
        ax.clear()
        
        # Get shadow properties for this frame
        time, shadow_length, shadow_width, shadow_angle, _ = results[frame]
        
        # Plot shadow for this frame
        plot_shadow(wall_width, wall_angle, shadow_length, shadow_width, 
                   shadow_angle, time, show=False)
        
        # Maintain axis properties
        ax.set_aspect('equal')
        limit = max(max(r[1] for r in results), wall_width) * 1.5
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.grid(True, linestyle='--', alpha=0.3)
        
        return ax.patches
    
    # Create animation
    anim = FuncAnimation(fig, update, frames=len(results), 
                        interval=100, blit=True)
    
    # Save if output file specified
    if output_file:
        anim.save(output_file, writer='pillow')
    else:
        plt.show()

def main():
    # Load configuration
    config = load_config()
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Calculate shadow dimensions based on wall height, width, orientation, and location.')
    parser.add_argument('height', type=str, nargs='?',
                      help=f'Wall height with unit (e.g., "10 feet" or "3 meters"). Supported units: {", ".join(UnitConverter.get_supported_units())}')
    parser.add_argument('--width', type=str,
                      help=f'Wall width with unit (e.g., "20 feet" or "6 meters"). Supported units: {", ".join(UnitConverter.get_supported_units())}')
    parser.add_argument('--wall-angle', type=str, default="0",
                      help='Wall angle in degrees from true north (0-360, clockwise)')
    parser.add_argument('--location', type=str, default=config['default_location'],
                      help=f'Location as address or "latitude,longitude" (default: {config["default_location"]})')
    parser.add_argument('--start-time', type=str,
                      help='Start time (HH:MM, YYYY-MM-DD, or YYYY-MM-DD HH:MM)')
    parser.add_argument('--end-time', type=str,
                      help='End time (HH:MM, YYYY-MM-DD, or YYYY-MM-DD HH:MM)')
    parser.add_argument('--interval', type=str, default="30m",
                      help='Time interval between calculations (e.g., 30m for 30 minutes, 1h for 1 hour)')
    parser.add_argument('--plot', action='store_true',
                      help='Show shadow plot')
    parser.add_argument('--animate', action='store_true',
                      help='Create animation for time range calculations')
    parser.add_argument('--save-animation', type=str,
                      help='Save animation to file (must end in .gif or .mp4)')
    parser.add_argument('--input-file', type=str,
                      help='YAML file containing input parameters')
    parser.add_argument('--config', action='store_true',
                      help='Show current configuration')
    
    args = parser.parse_args()
    
    # Handle input file
    if args.input_file:
        try:
            input_args = InputFileParser.parse(args.input_file)
            # Update args with input file values, preserving any command-line overrides
            args_dict = vars(args)
            for key, value in input_args.items():
                if args_dict[key] is None or (isinstance(args_dict[key], bool) and not args_dict[key]):
                    args_dict[key] = value
            args = argparse.Namespace(**args_dict)
        except ValueError as e:
            print(f"Error: {str(e)}")
            return
        
    if args.config:
        print("Current configuration:")
        print(yaml.dump(config, default_flow_style=False))
        return
        
    if not args.height:
        parser.print_help()
        return
        
    if not args.width:
        print("Error: Wall width is required")
        return
        
    try:
        # Parse height and convert to meters
        height_value, height_unit = UnitConverter.parse_value_with_unit(args.height)
        height_meters = UnitConverter.convert_to_meters(height_value, height_unit)
        
        # Parse width and convert to meters
        width_value, width_unit = UnitConverter.parse_value_with_unit(args.width)
        width_meters = UnitConverter.convert_to_meters(width_value, width_unit)
        
        # Parse wall angle
        wall_angle = parse_angle(args.wall_angle)
        
        # Get coordinates
        lat, lon, location_name = get_coordinates(args.location)
        
        # Handle time range calculations
        if args.start_time and args.end_time:  # Only do range if both times are specified
            # Parse start and end times
            start_time = parse_time(args.start_time)
            end_time = parse_time(args.end_time)
            
            # Ensure start time is before end time
            if start_time > end_time:
                start_time, end_time = end_time, start_time
                
            # Parse time interval
            time_step = parse_duration(args.interval)
            
            # Calculate shadows for time range
            results = calculate_shadow_range(
                height_meters, width_meters, wall_angle, lat, lon,
                start_time, end_time, time_step
            )
            
            # Output results
            print(f"\nLocation: {location_name}")
            print(f"Wall dimensions: {height_value} {height_unit} x {width_value} {width_unit}")
            print(f"Wall angle: {wall_angle}° from true north")
            print(f"\nShadow calculations from {start_time.strftime('%Y-%m-%d %H:%M')} "
                  f"to {end_time.strftime('%Y-%m-%d %H:%M')} "
                  f"at {args.interval} intervals:")
            print("\nTime                  Shadow Length  Shadow Width   Direction     Area")
            print("-" * 75)
            
            # Convert measurements to configured output units
            output_unit = config['output_units'].get('shadow', config['output_units']['default'])
            area_unit = f"sq {output_unit}"
            
            for time, length, width, angle, area in results:
                length_converted = UnitConverter.convert_from_meters(length, output_unit)
                width_converted = UnitConverter.convert_from_meters(width, output_unit)
                area_converted = UnitConverter.convert_from_meters(area, output_unit) ** 2
                print(f"{time.strftime('%Y-%m-%d %H:%M')}  "
                      f"{length_converted:8.2f} {output_unit:8}  "
                      f"{width_converted:8.2f} {output_unit:8}  "
                      f"{angle:6.1f}°  "
                      f"{area_converted:8.2f} {area_unit}")
            
            # Create animation if requested
            if args.animate or args.save_animation:
                create_shadow_animation(results, width_meters, wall_angle, args.save_animation)
                
        else:
            # Calculate shadow for single time
            calc_time = parse_time(args.start_time) if args.start_time else datetime.now()
            shadow_result = calculate_shadow_length(height_meters, width_meters, wall_angle, lat, lon, calc_time)
            
            if shadow_result is None:
                print(f"\nNo shadow calculation possible - sun is below horizon at {location_name}")
                return
                
            shadow_length, shadow_width, shadow_angle, shadow_area = shadow_result
            
            # Convert measurements to configured output units
            output_unit = config['output_units'].get('shadow', config['output_units']['default'])
            area_unit = f"sq {output_unit}"
            
            shadow_length_converted = UnitConverter.convert_from_meters(shadow_length, output_unit)
            shadow_width_converted = UnitConverter.convert_from_meters(shadow_width, output_unit)
            shadow_area_converted = UnitConverter.convert_from_meters(shadow_area, output_unit) ** 2
            
            print(f"\nLocation: {location_name}")
            print(f"Wall dimensions: {height_value} {height_unit} x {width_value} {width_unit}")
            print(f"Wall angle: {wall_angle}° from true north")
            print(f"Time: {calc_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"Shadow length: {shadow_length_converted:.2f} {output_unit}")
            print(f"Shadow width: {shadow_width_converted:.2f} {output_unit}")
            print(f"Shadow direction: {shadow_angle:.1f}° from true north")
            print(f"Shadow area: {shadow_area_converted:.2f} {area_unit}")
            
            # Show plot if requested
            if args.plot:
                plot_shadow(width_meters, wall_angle, shadow_length, shadow_width, 
                          shadow_angle, calc_time)
            
    except ValueError as e:
        print(f"Error: {str(e)}")
        return

if __name__ == "__main__":
    main()
