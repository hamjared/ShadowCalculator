"""
Input file parser for the shadow calculator.
Handles loading and validating YAML input files.
"""

import yaml
from typing import Dict, Any, List
from pathlib import Path

def print_debug(message: str) -> None:
    print(f"DEBUG: {message}")

class InputFileParser:
    """Parser for shadow calculator input files."""
    
    @staticmethod
    def validate_wall_section(wall_data: Dict[str, Any]) -> None:
        """
        Validate the wall section of the input file.
        
        Args:
            wall_data: Dictionary containing wall parameters
            
        Raises:
            ValueError: If required parameters are missing
        """
        if not wall_data:
            raise ValueError("Wall section is required")
        
        required_params = ['height', 'width']
        for param in required_params:
            if param not in wall_data:
                raise ValueError(f"Missing required wall parameter: {param}")
        
        # Validate angle
        if 'angle' in wall_data:
            try:
                wall_data['angle'] = float(wall_data['angle'])
            except (ValueError, TypeError):
                raise ValueError(f"Invalid wall angle: {wall_data['angle']}")
    
    @staticmethod
    def validate_time_section(time_data: Dict[str, Any]) -> None:
        """
        Validate the time section of the input file.
        
        Args:
            time_data: Dictionary containing time parameters
            
        Raises:
            ValueError: If time parameters are invalid
        """
        if not isinstance(time_data, dict):
            raise ValueError("Time section must be a dictionary")
            
        # Validate interval format if present
        if 'interval' in time_data:
            interval = str(time_data['interval'])
            if not interval[-1] in ['m', 'h'] or not interval[:-1].isdigit():
                raise ValueError(
                    "Invalid interval format. Use:\n"
                    "- <number>m for minutes (e.g., 30m)\n"
                    "- <number>h for hours (e.g., 2h)"
                )
    
    @staticmethod
    def validate_visualization_section(viz_data: Dict[str, Any]) -> None:
        """
        Validate the visualization section of the input file.
        
        Args:
            viz_data: Dictionary containing visualization parameters
            
        Raises:
            ValueError: If visualization parameters are invalid
        """
        if not isinstance(viz_data, dict):
            raise ValueError("Visualization section must be a dictionary")
        
        # Check that plot and animate are boolean
        if 'plot' in viz_data and not isinstance(viz_data['plot'], bool):
            raise ValueError("Visualization 'plot' must be a boolean")
        if 'animate' in viz_data and not isinstance(viz_data['animate'], bool):
            raise ValueError("Visualization 'animate' must be a boolean")
        
        # Check that save_animation is a string if present
        if 'save_animation' in viz_data and not isinstance(viz_data['save_animation'], str):
            raise ValueError("Visualization 'save_animation' must be a string")
    
    @classmethod
    def validate_areas_section(cls, areas: List[Dict[str, Any]]) -> None:
        """
        Validate the areas section of the input file.
        
        Args:
            areas: List of area dictionaries from input file
            
        Raises:
            ValueError if validation fails
        """
        if not isinstance(areas, list):
            raise ValueError("Areas section must be a list")
            
        for area in areas:
            if not isinstance(area, dict):
                raise ValueError("Each area must be a dictionary")
                
            required_fields = {'name', 'shape', 'center', 'width', 'height'}
            if not all(field in area for field in required_fields):
                raise ValueError(f"Area missing required fields: {required_fields}")
                
            if not isinstance(area['name'], str):
                raise ValueError("Area name must be a string")
                
            if area['shape'] != 'rectangle':
                raise ValueError("Only rectangle shape is currently supported")
                
            if not isinstance(area['center'], list) or len(area['center']) != 2:
                raise ValueError("Area center must be [x, y] coordinates")
                
            try:
                float(area['width'])
                float(area['height'])
                float(area.get('angle', 0))  # Angle is optional, defaults to 0
            except (ValueError, TypeError):
                raise ValueError("Area dimensions and angle must be numbers")
    
    @classmethod
    def validate_input_file(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the input file data.
        
        Args:
            input_data: Dictionary of input parameters
            
        Returns:
            Dictionary of validated input parameters
            
        Raises:
            ValueError: If the file is invalid or missing required parameters
        """
        if not isinstance(input_data, dict):
            raise ValueError("Input file must be a dictionary")
        
        # Validate wall section
        if 'wall' not in input_data:
            raise ValueError("Input file must contain 'wall' section")
        cls.validate_wall_section(input_data['wall'])
        
        # Validate time section if present
        if 'time' in input_data:
            cls.validate_time_section(input_data['time'])
        
        # Validate visualization section if present
        if 'visualization' in input_data:
            cls.validate_visualization_section(input_data['visualization'])
            # Ensure plot is a boolean
            if 'plot' in input_data['visualization']:
                input_data['visualization']['plot'] = bool(input_data['visualization']['plot'])
        
        # Validate areas section if present
        if 'areas' in input_data:
            cls.validate_areas_section(input_data['areas'])
        
        return input_data
    
    @classmethod
    def load_from_file(cls, file_path: str) -> Dict[str, Any]:
        """
        Load input parameters from a YAML file.
        
        Args:
            file_path: Path to YAML file
            
        Returns:
            Dictionary of input parameters
            
        Raises:
            ValueError: If the file cannot be parsed
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                print_debug(f"Raw file content:\n{content}")
                input_data = yaml.safe_load(content)
                print_debug(f"Parsed YAML:\n{input_data}")
                if not isinstance(input_data, dict):
                    raise ValueError("Invalid YAML: root must be a dictionary")
                return cls.validate_input_file(input_data)
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file: {e}")
        except FileNotFoundError:
            raise ValueError(f"File not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error reading file: {e}")
    
    @classmethod
    def convert_to_args(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert input file data to argument format.
        
        Args:
            input_data: Dictionary of input parameters
            
        Returns:
            Dictionary of arguments
        """
        print_debug(f"Converting input data to args: {input_data}")
        args = {}
        wall = input_data['wall']
        
        # Convert wall parameters
        args['height'] = str(wall.get('height', ''))
        args['width'] = str(wall.get('width', ''))
        args['wall_angle'] = float(wall.get('angle', 0))  # Convert angle to float
        
        # Convert location
        args['location'] = str(input_data.get('location', ''))
        
        # Convert time parameters
        if 'time' in input_data:
            time = input_data['time']
            args['start_time'] = str(time.get('start', ''))
            args['end_time'] = str(time.get('end', ''))
            args['interval'] = str(time.get('interval', '30m'))
        
        # Convert visualization parameters
        if 'visualization' in input_data:
            print_debug(f"Found visualization section: {input_data['visualization']}")
            vis = input_data['visualization']
            args['plot'] = True if vis.get('plot', False) else False
            args['animate'] = True if vis.get('animate', False) else False
            args['save_animation'] = str(vis.get('save_animation', ''))
            print_debug(f"Visualization settings: {vis}")
            print_debug(f"Plot flag: {args['plot']}")
        
        print_debug(f"Final args: {args}")
        return args
    
    @classmethod
    def parse_file(cls, file_path: str) -> Dict[str, Any]:
        """
        Parse a YAML input file.
        
        Args:
            file_path: Path to YAML input file
            
        Returns:
            Dictionary of validated input parameters
        """
        # First load and validate the raw input
        input_data = cls.load_from_file(file_path)
        
        # Convert to args format
        args = cls.convert_to_args(input_data)
        
        # Preserve the raw input data for sections that don't map to args
        args['raw_input'] = input_data
        
        print_debug(f"Final parsed data: {args}")
        return args
    
    @staticmethod
    def get_areas_from_input_file(file_path: str) -> List[Dict[str, Any]]:
        """
        Get areas from input file.
        
        Args:
            file_path: Path to input file
            
        Returns:
            List of area dictionaries
        """
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            if not data or 'areas' not in data:
                print_debug("No areas found in input file")
                return []
                
            areas = []
            for area in data['areas']:
                if not isinstance(area, dict):
                    print_debug(f"Skipping invalid area: {area}")
                    continue
                    
                required_fields = ['name', 'shape', 'center', 'width', 'height']
                if not all(field in area for field in required_fields):
                    print_debug(f"Area missing required fields: {area}")
                    continue
                    
                # Convert area to meters if units are specified
                try:
                    center = area['center']
                    if isinstance(center[0], str):
                        center_x = float(center[0].split()[0])
                        if len(center[0].split()) > 1 and center[0].split()[1].lower() == 'feet':
                            center_x *= 0.3048
                    else:
                        center_x = float(center[0])
                        
                    if isinstance(center[1], str):
                        center_y = float(center[1].split()[0])
                        if len(center[1].split()) > 1 and center[1].split()[1].lower() == 'feet':
                            center_y *= 0.3048
                    else:
                        center_y = float(center[1])
                        
                    width = area['width']
                    if isinstance(width, str):
                        width_val = float(width.split()[0])
                        if len(width.split()) > 1 and width.split()[1].lower() == 'feet':
                            width_val *= 0.3048
                    else:
                        width_val = float(width)
                        
                    height = area['height']
                    if isinstance(height, str):
                        height_val = float(height.split()[0])
                        if len(height.split()) > 1 and height.split()[1].lower() == 'feet':
                            height_val *= 0.3048
                    else:
                        height_val = float(height)
                        
                    areas.append({
                        'name': area['name'],
                        'shape': area['shape'],
                        'center': [center_x, center_y],
                        'width': width_val,
                        'height': height_val,
                        'angle': float(area.get('angle', 0))
                    })
                except (ValueError, IndexError) as e:
                    print_debug(f"Error parsing area {area['name']}: {e}")
                    continue
                    
            return areas
            
        except Exception as e:
            print_debug(f"Error reading areas from file: {e}")
            return []
