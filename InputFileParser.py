from typing import List, Dict, Any
import yaml
from DataModel import Wall, Location, WallParser, LocationParser

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
            
            return {
                'walls': walls,
                'location': location,
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
