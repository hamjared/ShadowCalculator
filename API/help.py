from typing import Dict, Any

def get_help_data() -> Dict[str, Any]:
    """Get help information and example requests."""
    return {
        "description": "Shadow Calculator API Help",
        "endpoints": {
            "/calculate/json": {
                "method": "POST",
                "description": "Calculate shadows using JSON input",
                "parameters": {
                    "save_animation": "bool (default: true) - Whether to generate animation",
                    "save_plot": "bool (default: true) - Whether to generate plot"
                },
                "example_request": {
                    "location": {
                        "latitude": 40.512053,
                        "longitude": -104.966723
                    },
                    "time": {
                        # Single time point
                        "point": "2025-06-17T12:00:00-07:00",
                        # Or time range
                        "start": "2025-06-17T09:00:00-07:00",
                        "end": "2025-06-17T20:00:00-07:00",
                        "interval": "30m"  # Format: <number>m for minutes, <number>h for hours
                    },
                    "walls": [
                        {
                            "name": "South Wall",
                            "height": "20 feet",
                            "start": ["0 feet", "0 feet"],
                            "end": ["15 feet", "0 feet"]
                        },
                        {
                            "name": "East Wall",
                            "height": "20 feet",
                            "start": ["15 feet", "0 feet"],
                            "end": ["15 feet", "20 feet"]
                        }
                    ],
                    "areas": [  # Optional
                        {
                            "name": "Patio",
                            "units": "feet",
                            "vertices": [
                                [5, 5],
                                [15, 5],
                                [15, 15],
                                [5, 15]
                            ]
                        }
                    ],
                    "plotConfig": {  # Optional
                        "enabled": True,
                        "figure_size": [12, 8],
                        "show_compass": True,
                        "show_sun": True,
                        "show_dimensions": True,
                        "dpi": 300,
                        "timezone": "America/Denver",
                        "output_units": "feet",
                        "x_limits": [-10, 50],  # Optional
                        "y_limits": [-10, 30]   # Optional
                    },
                    "animationConfig": {  # Optional
                        "enabled": True,
                        "fps": 1,
                        "loop": True
                    },
                    "sunConfig": {  # Optional - override sun position
                        "override_position": True,
                        "elevation": 45.0,
                        "azimuth": 180.0
                    }
                }
            },
            "/calculate/file": {
                "method": "POST",
                "description": "Calculate shadows using file upload (YAML/JSON)",
                "parameters": {
                    "file": "File upload (YAML/JSON with same format as /calculate/json)",
                    "save_animation": "bool (default: true) - Whether to generate animation",
                    "save_plot": "bool (default: true) - Whether to generate plot"
                }
            }
        },
        "notes": [
            "All times must include timezone information",
            "Measurements must include units (e.g., 'feet', 'meters')",
            "Wall coordinates are specified as [x, y] pairs",
            "Areas must have at least 3 vertices specified counter-clockwise",
            "Animation intervals: '30m' = 30 minutes, '1h' = 1 hour",
            "Available timezones: Use standard IANA timezone names (e.g., 'America/Denver')"
        ],
        "example_curl": {
            "json": """
curl -X POST "http://localhost:8000/calculate/json" \\
     -H "accept: application/json" \\
     -H "Content-Type: application/json" \\
     -d '{
       "location": {
         "latitude": 40.512053,
         "longitude": -104.966723
       },
       "time": {
         "point": "2025-06-17T12:00:00-07:00"
       },
       "walls": [
         {
           "name": "South Wall",
           "height": "20 feet",
           "start": ["0 feet", "0 feet"],
           "end": ["15 feet", "0 feet"]
         }
       ]
     }'
""",
            "file": """
curl -X POST "http://localhost:8000/calculate/file" \\
     -H "accept: application/json" \\
     -H "Content-Type: multipart/form-data" \\
     -F "file=@example.yml"
"""
        }
    }
