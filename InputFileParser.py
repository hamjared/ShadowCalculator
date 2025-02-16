"""
Input file parser for the shadow calculator.
Handles loading and validating YAML input files.
"""

import yaml
from typing import Dict, Any, List
from pathlib import Path

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
        if not isinstance(wall_data, dict):
            raise ValueError("Wall section must be a dictionary")
            
        required_fields = ['height', 'width']
        for field in required_fields:
            if field not in wall_data:
                raise ValueError(f"Wall section must contain '{field}'")
    
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
            
        # Validate animation file extension if present
        if 'save_animation' in viz_data:
            file_ext = Path(str(viz_data['save_animation'])).suffix.lower()
            if file_ext not in ['.gif', '.mp4']:
                raise ValueError("Animation file must end in .gif or .mp4")
    
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
            raise ValueError("Input file must contain a dictionary")
            
        # Validate required sections
        if 'wall' not in input_data:
            raise ValueError("Input file must contain 'wall' section")
            
        # Validate each section
        cls.validate_wall_section(input_data['wall'])
        if 'time' in input_data:
            cls.validate_time_section(input_data['time'])
        if 'visualization' in input_data:
            cls.validate_visualization_section(input_data['visualization'])
        if 'areas' in input_data:
            cls.validate_areas_section(input_data['areas'])
            
        return input_data
    
    @classmethod
    def load_and_validate(cls, file_path: str) -> Dict[str, Any]:
        """
        Load and validate a YAML input file.
        
        Args:
            file_path: Path to YAML input file
            
        Returns:
            Dictionary of validated input parameters
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                print(f"DEBUG: Raw file content:\n{content}")
                input_data = yaml.safe_load(content)
                print(f"DEBUG: Parsed YAML:\n{input_data}")
                return cls.validate_input_file(input_data)
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file: {e}")
        except FileNotFoundError:
            raise ValueError(f"Input file not found: {file_path}")
    
    @classmethod
    def convert_to_args(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert input data dictionary to command line arguments.
        
        Args:
            input_data: Dictionary of input parameters from YAML file
            
        Returns:
            Dictionary of command line arguments
        """
        args = {}
        
        # Wall parameters
        wall_data = input_data.get('wall', {})
        args['height'] = wall_data.get('height')
        args['width'] = wall_data.get('width')
        args['wall_angle'] = str(wall_data.get('angle', 0))
        
        # Location
        args['location'] = input_data.get('location')
        
        # Time parameters
        time_data = input_data.get('time', {})
        args['start_time'] = time_data.get('start')
        args['end_time'] = time_data.get('end')
        args['interval'] = time_data.get('interval', '30m')
        
        # Visualization parameters
        vis_data = input_data.get('visualization', {})
        args['plot'] = vis_data.get('plot', True)
        args['animate'] = vis_data.get('animate', False)
        args['save_animation'] = vis_data.get('save_animation')
        
        # Areas to analyze
        args['areas'] = input_data.get('areas', [])
        
        return args
    
    @classmethod
    def parse(cls, file_path: str) -> Dict[str, Any]:
        """
        Parse and validate a YAML input file.
        
        Args:
            file_path: Path to YAML input file
            
        Returns:
            Dictionary of validated input parameters
        """
        # First load and validate the raw input
        input_data = cls.load_and_validate(file_path)
        
        # Convert to args format
        args = cls.convert_to_args(input_data)
        
        # Preserve the raw input data for sections that don't map to args
        args['raw_input'] = input_data
        
        print(f"DEBUG: Final parsed data: {args}")
        return args
