"""
Input file parser for the shadow calculator.
Handles loading and validating YAML input files.
"""

import yaml
from typing import Dict, Any
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
    def load_and_validate(cls, file_path: str) -> Dict[str, Any]:
        """
        Load and validate a YAML input file.
        
        Args:
            file_path: Path to the YAML input file
            
        Returns:
            dict: Dictionary of validated input parameters
            
        Raises:
            ValueError: If the file is invalid or missing required parameters
        """
        try:
            with open(file_path, 'r') as f:
                input_data = yaml.safe_load(f)
                
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
                
            return input_data
            
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error loading input file: {str(e)}")
    
    @classmethod
    def convert_to_args(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert input file data to command-line argument format.
        
        Args:
            input_data: Dictionary of input parameters from YAML file
            
        Returns:
            dict: Dictionary of command-line arguments
        """
        # Convert input data to command-line argument format
        args = {
            'height': input_data['wall']['height'],
            'width': input_data['wall']['width'],
            'wall_angle': str(input_data['wall'].get('angle', 0)),
            'location': input_data.get('location', None),
        }
        
        # Handle time parameters
        if 'time' in input_data:
            args['start_time'] = input_data['time'].get('start', None)
            args['end_time'] = input_data['time'].get('end', None)
            args['interval'] = input_data['time'].get('interval', '30m')
            
        # Handle visualization parameters
        if 'visualization' in input_data:
            args['plot'] = input_data['visualization'].get('plot', False)
            args['animate'] = input_data['visualization'].get('animate', False)
            args['save_animation'] = input_data['visualization'].get('save_animation', None)
            
        return args
    
    @classmethod
    def parse(cls, file_path: str) -> Dict[str, Any]:
        """
        Parse an input file and return command-line arguments.
        
        Args:
            file_path: Path to the YAML input file
            
        Returns:
            dict: Dictionary of command-line arguments
            
        Raises:
            ValueError: If the file is invalid or missing required parameters
        """
        input_data = cls.load_and_validate(file_path)
        return cls.convert_to_args(input_data)
