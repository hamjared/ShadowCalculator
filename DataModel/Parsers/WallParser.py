from typing import Dict, Any
from ..Wall import Wall
from ..Point import Point, ureg

class WallParser:
    """Parser for wall data from dictionary format."""
    
    @staticmethod
    def parse(wall_data: Dict[str, Any]) -> Wall:
        """Parse wall data from a dictionary format.
        
        Args:
            wall_data: Dictionary containing wall data with fields:
                      - name (optional): Wall name
                      - height: Wall height with units (e.g., "10 feet")
                      - start: [x, y] coordinates with units
                      - end: [x, y] coordinates with units
                      
        Returns:
            Wall: Parsed wall object
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields
        required_fields = {'height', 'start', 'end'}
        missing_fields = required_fields - wall_data.keys()
        if missing_fields:
            raise ValueError(f"Missing required wall fields: {missing_fields}")
            
        # Parse start point
        if not isinstance(wall_data['start'], list) or len(wall_data['start']) != 2:
            raise ValueError("Start point must be a list of [x, y] coordinates")
            
        # Parse end point
        if not isinstance(wall_data['end'], list) or len(wall_data['end']) != 2:
            raise ValueError("End point must be a list of [x, y] coordinates")
            
        # Create points
        start_point = Point.from_strings(
            str(wall_data['start'][0]),
            str(wall_data['start'][1])
        )
        end_point = Point.from_strings(
            str(wall_data['end'][0]),
            str(wall_data['end'][1])
        )
        
        # Parse height
        height = ureg(wall_data['height'])
        
        # Create wall
        return Wall(
            name=wall_data.get('name', 'Wall'),
            height=height,
            start_point=start_point,
            end_point=end_point
        )
