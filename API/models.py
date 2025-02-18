from typing import Dict, Any
from DataModel.Shadow import Shadow

def shadow_to_dict(shadow: Shadow) -> Dict[str, Any]:
    """Convert a Shadow object to a dictionary."""
    return {
        'wall_name': shadow.wall.name,
        'time': shadow.time.isoformat(),
        'solar_elevation': shadow.solar_elevation,
        'solar_azimuth': shadow.solar_azimuth,
        'vertices': [
            {
                'x': str(vertex.x),
                'y': str(vertex.y)
            }
            for vertex in shadow.vertices
        ],
        'length': str(shadow.length),
        'width': str(shadow.width),
        'area': str(shadow.area),
        'angle': shadow.angle
    }
