import astral
from astral.sun import sun, elevation, azimuth
from datetime import datetime, timedelta
import math
from typing import Tuple, Dict, List, Any
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
from ShadowAnalyzer import ShadowAnalyzer
import colorama
from colorama import Fore, Style
colorama.init()
import sys
import codecs
import re

# Set up UTF-8 encoding for stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

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
    
    print_debug(f"Solar azimuth at {date_time}: {solar_azimuth}°")  # Debug print
    
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
    Parse time string into datetime object.
    
    Supports formats:
    - HH:MM (e.g., "15:00")
    - YYYY-MM-DD HH:MM (e.g., "2025-02-16 15:00")
    - YYYY-MM-DDTHH:MM:SS-ZZ:ZZ (e.g., "2025-02-16T15:00:00-07:00")
    
    If no timezone is specified, assumes local time (MST/MDT).
    """
    try:
        # Try ISO format first (YYYY-MM-DDTHH:MM:SS-ZZ:ZZ)
        dt = datetime.fromisoformat(time_str)
        if dt.tzinfo is None:
            # If no timezone provided, assume MST/MDT (UTC-7)
            dt = dt.replace(tzinfo=timezone(timedelta(hours=-7)))
        return dt
    except ValueError:
        pass
        
    try:
        # Try YYYY-MM-DD HH:MM format
        dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        # Add MST/MDT timezone (UTC-7)
        return dt.replace(tzinfo=timezone(timedelta(hours=-7)))
    except ValueError:
        pass
        
    try:
        # Try HH:MM format
        time_match = re.match(r"^(\d{1,2}):(\d{2})$", time_str)
        if time_match:
            hour, minute = map(int, time_match.groups())
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                # Use current date with specified time
                now = datetime.now(timezone(timedelta(hours=-7)))
                return now.replace(hour=hour, minute=minute)
    except ValueError:
        pass
        
    raise ValueError(
        "Invalid time format. Supported formats:\n"
        "- HH:MM (e.g., '15:00')\n"
        "- YYYY-MM-DD HH:MM (e.g., '2025-02-16 15:00')\n"
        "- YYYY-MM-DDTHH:MM:SS-ZZ:ZZ (e.g., '2025-02-16T15:00:00-07:00')"
    )

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
                areas: List[Dict[str, Any]] = None, show: bool = True,
                wall_height: float = None) -> tuple:
    """
    Plot the wall and its shadow.
    
    Args:
        wall_width: Width of the wall in meters
        wall_angle: Wall angle in degrees from true north (clockwise)
        shadow_length: Length of shadow in meters
        shadow_width: Width of the shadow in meters
        shadow_angle: Shadow angle in degrees from true north (clockwise)
        time: Optional datetime for plot title
        areas: Optional list of areas to analyze for shadow coverage
        show: Whether to show the plot immediately
        wall_height: Height of the wall in meters
        
    Returns:
        tuple: (figure, axis) for further customization
    """
    print_debug(f"plot_shadow called with areas: {areas}")
    
    # Load config for plot units
    config = load_config()
    plot_unit = config.get('output_units', {}).get('plot', 'meters').lower()
    
    # Convert all dimensions to plot units if needed
    conversion_factor = 3.28084 if plot_unit == 'feet' else 1  # meters to feet
    plot_wall_width = wall_width * conversion_factor
    plot_shadow_length = shadow_length * conversion_factor
    plot_wall_height = wall_height * conversion_factor if wall_height is not None else None
    
    # Create figure and axis with extra space for legend
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Adjust layout to make room for legend
    plt.subplots_adjust(right=0.85)
    
    # Convert angles to radians (compass coordinates: clockwise from north)
    wall_rad = np.radians(wall_angle)
    shadow_rad = np.radians(shadow_angle)
    
    # Calculate shadow vertices using compass coordinates
    # In compass coordinates: x = r * sin(theta), y = r * cos(theta)
    vertices = [
        (-plot_wall_width/2 * np.sin(wall_rad), -plot_wall_width/2 * np.cos(wall_rad)),  # Left wall point
        (plot_wall_width/2 * np.sin(wall_rad), plot_wall_width/2 * np.cos(wall_rad)),    # Right wall point
        (plot_wall_width/2 * np.sin(wall_rad) + plot_shadow_length * np.sin(shadow_rad),  # Right shadow point
         plot_wall_width/2 * np.cos(wall_rad) + plot_shadow_length * np.cos(shadow_rad)),
        (-plot_wall_width/2 * np.sin(wall_rad) + plot_shadow_length * np.sin(shadow_rad), # Left shadow point
         -plot_wall_width/2 * np.cos(wall_rad) + plot_shadow_length * np.cos(shadow_rad))
    ]
    
    # Create patches
    shadow = Polygon(vertices, color='gray', alpha=0.3, zorder=1, label='Shadow')
    ax.add_patch(shadow)
    
    # Create wall line
    wall_start = vertices[0]  # Left wall point
    wall_end = vertices[1]    # Right wall point
    wall_line = plt.Line2D([wall_start[0], wall_end[0]], 
                          [wall_start[1], wall_end[1]], 
                          color='black', 
                          linewidth=2,
                          zorder=2,
                          label=f'Wall (height: {plot_wall_height:.1f} {plot_unit})')
    ax.add_line(wall_line)
    
    # Add sun position
    sun_angle = (shadow_angle + 180) % 360  # Sun is opposite the shadow
    sun_rad = np.radians(sun_angle)
    sun_radius = max(plot_shadow_length, plot_wall_width) * 1.2
    sun_x = sun_radius * np.sin(sun_rad)  # Compass coordinates
    sun_y = sun_radius * np.cos(sun_rad)  # Compass coordinates
    
    # Draw sun
    sun = plt.Circle((sun_x, sun_y), radius=sun_radius*0.05, 
                    color='orange', alpha=0.8, zorder=3, label='Sun')
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
    compass_radius = sun_radius * 1.1
    compass_points = {
        'N': (0, compass_radius),
        'S': (0, -compass_radius),
        'E': (compass_radius, 0),
        'W': (-compass_radius, 0)
    }
    
    for direction, (x, y) in compass_points.items():
        ax.text(x, y, direction, ha='center', va='center', fontsize=12, fontweight='bold')
    
    # Add areas if provided
    if areas:
        print_debug("Creating ShadowAnalyzer")
        analyzer = ShadowAnalyzer()
        for area in areas:
            # Convert area dimensions to plot units
            plot_area = area.copy()
            plot_area['center'] = [x * conversion_factor for x in area['center']]
            plot_area['width'] = area['width'] * conversion_factor
            plot_area['height'] = area['height'] * conversion_factor
            
            print_debug(f"Adding area: {plot_area}")
            analyzer.add_rectangular_area(
                name=plot_area['name'],
                center=plot_area['center'],
                width=plot_area['width'],
                height=plot_area['height'],
                angle=plot_area.get('angle', 0)
            )
        
        # Calculate and display coverage
        print_debug("Calculating coverage")
        coverage = analyzer.analyze_shadow_coverage(
            wall_width=plot_wall_width,
            wall_angle=wall_angle,
            shadow_length=plot_shadow_length,
            shadow_angle=shadow_angle
        )
        print_debug(f"Coverage results: {coverage}")
        
        # Plot areas with coverage information
        print_debug("Plotting areas")
        analyzer.plot_areas(ax, coverage)
    
    # Add legend
    handles, labels = ax.get_legend_handles_labels()
    
    # Sort handles and labels to ensure consistent order
    legend_items = list(zip(handles, labels))
    legend_items.sort(key=lambda x: x[1])  # Sort by label
    handles, labels = zip(*legend_items)
    
    # Create legend with two columns
    ax.legend(handles, labels, 
             loc='upper left', 
             bbox_to_anchor=(1.05, 1), 
             borderaxespad=0.,
             ncol=1,
             title='Legend',
             framealpha=0.9)
    
    # Add equal aspect ratio and limits
    ax.set_aspect('equal')
    limit = max(plot_shadow_length, plot_wall_width, sun_radius) * 1.2
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.3)
    
    # Add axes labels with units
    ax.set_xlabel(f'Distance ({plot_unit})')
    ax.set_ylabel(f'Distance ({plot_unit})')
    
    # Set title if time provided
    if time:
        title = f"Shadow at {time.strftime('%Y-%m-%d %H:%M')}\n"
        title += f"Wall width: {plot_wall_width:.1f} {plot_unit}\n"
        title += f"Sun azimuth: {(sun_angle):.1f}°, Shadow angle: {shadow_angle:.1f}°"
        ax.set_title(title)
    
    return fig, ax

def create_shadow_animation(results: list, wall_width: float, wall_angle: float, 
                          output_file: str = None, areas: List[Dict[str, Any]] = None) -> None:
    """
    Create an animation of shadow movement over time.
    
    Args:
        results: List of (time, shadow_length, shadow_width, shadow_angle) tuples
        wall_width: Width of the wall in meters
        wall_angle: Wall angle in degrees from true north
        output_file: Optional path to save animation file
        areas: Optional list of areas to analyze for shadow coverage
    """
    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(10, 10))
    
    def update(frame):
        ax.clear()
        
        # Get shadow properties for this frame
        time, shadow_length, shadow_width, shadow_angle, _ = results[frame]
        
        # Plot shadow for this frame
        plot_shadow(wall_width, wall_angle, shadow_length, shadow_width, 
                   shadow_angle, time, areas=areas, show=False)
        
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

def print_debug(msg: str) -> None:
    """Print a debug message with color and write to file."""
    print(f"{Fore.CYAN}DEBUG: {msg}{Style.RESET_ALL}")
    with open('debug.log', 'a', encoding='utf-8') as f:
        f.write(f"DEBUG: {msg}\n")

def main():
    try:
        # Load configuration
        config = load_config()
        
        # Parse command line arguments
        parser = argparse.ArgumentParser(description='Calculate shadow length and direction')
        parser.add_argument('--height', help='Height of wall (with units, e.g. "10 feet")')
        parser.add_argument('--width', help='Width of wall (with units, e.g. "20 feet")')
        parser.add_argument('--wall-angle', type=float, help='Wall angle in degrees from true north (clockwise)')
        parser.add_argument('--location', help='Location (address or "latitude,longitude")')
        parser.add_argument('--start-time', help='Start time (HH:MM, YYYY-MM-DD, or YYYY-MM-DD HH:MM)')
        parser.add_argument('--end-time', help='End time (same format as start-time)')
        parser.add_argument('--interval', help='Time interval (e.g. "30m", "1h")')
        parser.add_argument('--plot', action='store_true', help='Show plot')
        parser.add_argument('--animate', action='store_true', help='Show animation')
        parser.add_argument('--save-animation', help='Save animation to file')
        parser.add_argument('--input-file', help='Input file (YAML)')
        
        args = parser.parse_args()
        
        # Parse input file if provided
        if args.input_file:
            try:
                # Parse input file and get raw data
                input_data = InputFileParser.load_from_file(args.input_file)
                print_debug(f"Raw file content:\n{input_data}")
                
                # Convert to args format
                file_args = InputFileParser.convert_to_args(input_data)
                print_debug(f"Converted args: {file_args}")
                
                # Update args with file values
                for key, value in file_args.items():
                    if value is not None:
                        setattr(args, key, value)
                print_debug(f"Final args: {vars(args)}")
            except ValueError as e:
                print(f"Error processing input file: {str(e)}")
                return
        
        # Extract values and units from measurements
        if args.height:
            height_value, height_unit = UnitConverter.parse_value_with_unit(args.height)
            if not height_unit:
                height_unit = config['output_units'].get('shadow', config['output_units']['default'])
        else:
            print("Wall height is required")
            return
        
        if args.width:
            width_value, width_unit = UnitConverter.parse_value_with_unit(args.width)
            if not width_unit:
                width_unit = config['output_units'].get('shadow', config['output_units']['default'])
        else:
            width_value = height_value
            width_unit = height_unit
        
        # Convert measurements to meters for calculations
        height_meters = UnitConverter.convert_to_meters(height_value, height_unit)
        width_meters = UnitConverter.convert_to_meters(width_value, width_unit)
        
        # Parse wall angle
        if isinstance(args.wall_angle, str):
            try:
                wall_angle = float(args.wall_angle)
            except ValueError:
                print(f"Invalid wall angle: {args.wall_angle}")
                return
        else:
            wall_angle = args.wall_angle
        wall_angle = wall_angle % 360  # Normalize to 0-360
        
        # Get coordinates
        lat, lon, location_name = get_coordinates(args.location)
        
        # Calculate shadow for single time
        calc_time = None
        if args.start_time:
            try:
                calc_time = parse_time(args.start_time)
            except ValueError as e:
                print(f"Error parsing time: {e}")
                return
        
        shadow_result = calculate_shadow_length(height_meters, width_meters, wall_angle, lat, lon, calc_time)
        
        if shadow_result is None:
            print(f"\nNo shadow calculation possible - sun is below horizon at {location_name}")
            return
        
        shadow_length, shadow_width, shadow_angle, shadow_area = shadow_result
        
        # Convert measurements to configured output units
        output_unit = config.get('output_units', {}).get('shadow', 'meters')
        area_unit = f"sq {output_unit}"
        
        shadow_length_converted = UnitConverter.convert_from_meters(shadow_length, output_unit)
        shadow_width_converted = UnitConverter.convert_from_meters(shadow_width, output_unit)
        shadow_area_converted = UnitConverter.convert_from_meters(shadow_area, output_unit) ** 2
        
        print(f"\nLocation: {location_name}")
        print(f"Wall dimensions: {height_value} {height_unit} x {width_value} {width_unit}")
        print(f"Wall angle: {wall_angle:.1f}° from true north")
        print(f"Time: {calc_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"Shadow length: {shadow_length_converted:.2f} {output_unit}")
        print(f"Shadow width: {shadow_width_converted:.2f} {output_unit}")
        print(f"Shadow direction: {shadow_angle:.1f}° from true north")
        print(f"Shadow area: {shadow_area_converted:.2f} {area_unit}")
        
        # Show plot if requested
        if hasattr(args, 'plot') and args.plot:
            print_debug("Plotting shadow diagram...")
            print_debug(f"Args: {args}")
            print_debug(f"Plot flag: {args.plot}")
            
            # Plot shadow with areas using already-converted dimensions
            plt.close('all')  # Close any existing plots
            
            # Get areas from input file if it exists
            areas = []
            if args.input_file:
                areas = InputFileParser.get_areas_from_input_file(args.input_file)
                print_debug(f"Areas from input file: {areas}")
            
            fig, ax = plot_shadow(width_meters, wall_angle, shadow_length, shadow_width, 
                                shadow_angle, calc_time, areas=areas, show=True, wall_height=height_meters)
            print_debug("About to show plot...")
            plt.show()  # Show the plot
            print_debug("Plot shown")
            
    except ValueError as e:
        print(f"Error: {str(e)}")
        return
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return

if __name__ == "__main__":
    main()
