from typing import Dict, Any, List
import yaml
from DataModel import Wall, Location, WallParser, LocationParser
from DataModel.TimeSpecification import TimeSpecification
from DataModel.PlotConfig import PlotConfig
from DataModel.SunConfig import SunConfig
from DataModel.AnimationConfig import AnimationConfig

class InputFileParser:
    """Parser for shadow calculator input files."""
    
    @classmethod
    def parse_walls(cls, data: Dict[str, Any]) -> List[Wall]:
        """Parse all walls from input data."""
        if 'walls' not in data:
            raise ValueError("No 'walls' section found in input file")
            
        if not isinstance(data['walls'], list):
            raise ValueError("'walls' section must be a list")
            
        walls = []
        for i, wall_data in enumerate(data['walls'], 1):
            try:
                wall = WallParser.parse(wall_data)
                walls.append(wall)
            except Exception as e:
                raise ValueError(f"Error parsing wall {i}: {str(e)}")
                
        return walls
    
    @classmethod
    def parse_location(cls, data: Dict[str, Any]) -> Location:
        """Parse location from input data."""
        if 'location' not in data:
            raise ValueError("No 'location' section found in input file")
            
        try:
            return LocationParser.parse(data['location'])
        except Exception as e:
            raise ValueError(f"Error parsing location: {str(e)}")
    
    @classmethod
    def parse_time_spec(cls, data: Dict[str, Any]) -> TimeSpecification:
        """Parse time specification from input data."""
        if 'time' not in data:
            raise ValueError("No 'time' section found in input file")
            
        try:
            return TimeSpecification.from_dict(data['time'])
        except Exception as e:
            raise ValueError(f"Error parsing time specification: {str(e)}")
    
    @classmethod
    def parse_plot_config(cls, data: Dict[str, Any]) -> PlotConfig:
        """Parse plot configuration from input data."""
        try:
            if 'plotConfig' in data:
                return PlotConfig.from_dict(data['plotConfig'])
            return PlotConfig()  # Return default config if not specified
        except Exception as e:
            raise ValueError(f"Error parsing plot configuration: {str(e)}")
    
    @classmethod
    def parse_sun_config(cls, data: Dict[str, Any]) -> SunConfig:
        """Parse sun configuration from input data."""
        try:
            if 'sunConfig' in data:
                return SunConfig.from_dict(data['sunConfig'])
            return SunConfig()  # Return default config if not specified
        except Exception as e:
            raise ValueError(f"Error parsing sun configuration: {str(e)}")
    
    @classmethod
    def parse_animation_config(cls, data: Dict[str, Any]) -> AnimationConfig:
        """Parse animation configuration from input data."""
        try:
            if 'animationConfig' in data:
                return AnimationConfig.from_dict(data['animationConfig'])
            return AnimationConfig()  # Return default config if not specified
        except Exception as e:
            raise ValueError(f"Error parsing animation configuration: {str(e)}")
    
    @classmethod
    def load_from_file(cls, file_path: str) -> Dict[str, Any]:
        """Load and parse data from a YAML file."""
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
                
            if not isinstance(data, dict):
                raise ValueError("Input file must be a dictionary")
                
            # Parse required sections
            walls = cls.parse_walls(data)
            location = cls.parse_location(data)
            time_spec = cls.parse_time_spec(data)
            plot_config = cls.parse_plot_config(data)
            sun_config = cls.parse_sun_config(data)
            animation_config = cls.parse_animation_config(data)
            
            return {
                'walls': walls,
                'location': location,
                'time_spec': time_spec,
                'plot_config': plot_config,
                'sun_config': sun_config,
                'animation_config': animation_config,
                'raw_data': data  # Include raw data for other sections
            }
            
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file: {e}")
        except FileNotFoundError:
            raise ValueError(f"File not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error reading file: {e}")
            
    @classmethod
    def parse_file(cls, file_path: str) -> Dict[str, Any]:
        """Alias for load_from_file for consistency with other parsers."""
        return cls.load_from_file(file_path)
