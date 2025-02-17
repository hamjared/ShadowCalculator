from typing import Dict, Any, List
from datetime import datetime
from InputFileParser import InputFileParser
from DataModel.Location import Location
from DataModel.Wall import Wall
from DataModel.Shadow import Shadow
from DataModel.Point import Point, ureg
from DataModel.TimeSpecification import TimeSpecification
from DataModel.PlotConfig import PlotConfig
from DataModel.SunConfig import SunConfig
from DataModel.AnimationConfig import AnimationConfig
from Plotting.Plotter import Plotter
from Calculation.Sun import Sun
from Calculation.ShadowCalculations import ShadowCalculations
import matplotlib.pyplot as plt
import numpy as np

class ShadowCalculator:
    """Main class for calculating shadows cast by walls."""
    
    def __init__(self, location: Location, walls: list[Wall], 
                 time_spec: TimeSpecification, plot_config: PlotConfig,
                 sun_config: SunConfig, animation_config: AnimationConfig):
        """Initialize the calculator with location, walls, and specifications."""
        self.location = location
        self.walls = walls
        self.time_spec = time_spec
        self.plot_config = plot_config
        self.sun_config = sun_config
        self.animation_config = animation_config
        self.plotter = Plotter(plot_config, location, animation_config)
    
    @classmethod
    def from_input_file(cls, file_path: str) -> "ShadowCalculator":
        """Create a ShadowCalculator from an input file.
        
        Args:
            file_path: Path to YAML input file
            
        Returns:
            ShadowCalculator instance
            
        Raises:
            ValueError: If file cannot be parsed
        """
        try:
            data = InputFileParser.load_from_file(file_path)
            return cls(
                location=data['location'],
                walls=data['walls'],
                time_spec=data['time_spec'],
                plot_config=data['plot_config'],
                sun_config=data['sun_config'],
                animation_config=data['animation_config']
            )
        except Exception as e:
            raise ValueError(f"Error loading input file: {str(e)}")
    
    def calculate_for_time(self, time: datetime) -> List[Shadow]:
        """Calculate shadows for all walls at a specific time.
        
        Args:
            time: Time to calculate shadows for
            
        Returns:
            List of Shadow objects, one for each wall
        """
        # Get sun position for this time and location
        sun_position = Sun.get_position(
            latitude=self.location.latitude,
            longitude=self.location.longitude,
            time=time,
            sun_config=self.sun_config
        )
        
        # Calculate shadows for each wall
        shadows = []
        for wall in self.walls:
            shadow = ShadowCalculations.calculate_shadow(
                wall=wall,
                solar_elevation=sun_position.elevation,
                solar_azimuth=sun_position.azimuth,
                time=time
            )
            shadows.append(shadow)
            
        return shadows
    
    def calculate(self) -> List[List[Shadow]]:
        """Calculate shadows for all walls at all specified times.
        
        Returns:
            List of shadow lists, one list for each time point
        """
        return [
            self.calculate_for_time(time)
            for time in self.time_spec.get_times()
        ]
    
    def plot_shadows(self, shadows: List[Shadow]) -> None:
        """Plot shadows if plotting is enabled in configuration.
        
        Args:
            shadows: List of shadows to plot
        """
        if not self.plot_config.enabled:
            return
            
        # Create plot
        fig = self.plotter.plot(shadows)
        
        # Save or display based on configuration
        if self.plot_config.save_path:
            self.plotter.save(fig, self.plot_config.save_path)
        else:
            plt.show()
            
    def create_animation(self, all_shadows: List[List[Shadow]]) -> None:
        """Create animation if animation is enabled in configuration.
        
        Args:
            all_shadows: List of shadow lists, one for each time point
        """
        if not self.animation_config.enabled:
            return
            
        self.plotter.create_animation(all_shadows)
