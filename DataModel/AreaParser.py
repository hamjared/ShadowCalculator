from typing import Dict, Any, List
from .Area import Area
from .Point import ureg

class AreaParser:
    """Parser for Area objects from configuration data."""
    
    @classmethod
    def parse(cls, data: Dict[str, Any]) -> Area:
        """Parse an Area from dictionary data.
        
        Args:
            data: Dictionary containing area data with fields:
                name: Name of the area
                units: Units for vertex coordinates (e.g., 'feet', 'meters')
                vertices: List of [x, y] coordinates as numbers
                
        Returns:
            Area object
            
        Raises:
            ValueError: If data is invalid
        """
        # Validate required fields
        if 'name' not in data:
            raise ValueError("Area must have a name")
        if 'units' not in data:
            raise ValueError("Area must specify units")
        if 'vertices' not in data:
            raise ValueError("Area must have vertices")
            
        # Parse vertices
        if not isinstance(data['vertices'], list):
            raise ValueError("Vertices must be a list")
        if len(data['vertices']) < 3:
            raise ValueError(
                f"Area must have at least 3 vertices, got {len(data['vertices'])}"
            )
            
        vertices = []
        for i, vertex in enumerate(data['vertices'], 1):
            if not isinstance(vertex, list) or len(vertex) != 2:
                raise ValueError(
                    f"Vertex {i} must be a list of [x, y], got {vertex}"
                )
                
            try:
                # Convert to float, units will be added by Area class
                x = float(vertex[0])
                y = float(vertex[1])
                vertices.append([x, y])
            except Exception as e:
                raise ValueError(
                    f"Error parsing vertex {i}: {str(e)}"
                )
        
        # Create area
        return Area(
            name=data['name'],
            vertices=vertices,
            units=data['units']
        )
