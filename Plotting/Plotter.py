from typing import List, Optional
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter
from DataModel.Shadow import Shadow
from DataModel.Location import Location
from DataModel.PlotConfig import PlotConfig
from DataModel.AnimationConfig import AnimationConfig
from DataModel.Area import Area
from .ShadowPlotter import ShadowPlotter
from .CompassPlotter import CompassPlotter
from .AreaPlotter import AreaPlotter

class Plotter:
    """Main plotter class that coordinates shadow and compass plotting."""
    
    def __init__(self, config: PlotConfig, location: Location,
                 animation_config: Optional[AnimationConfig] = None):
        """Initialize with configuration and location.
        
        Args:
            config: Plot configuration
            location: Location for sun calculations
            animation_config: Optional animation configuration
        """
        self.config = config
        self.location = location
        self.animation_config = animation_config or AnimationConfig()
        self.shadow_plotter = ShadowPlotter(config)
        self.compass_plotter = CompassPlotter(location)
        self.area_plotter = AreaPlotter(config)
    
    def format_location(self) -> str:
        """Format location for display.
        
        Returns:
            Location string in format "lat°N/S, lon°E/W"
        """
        lat = abs(self.location.latitude)
        lon = abs(self.location.longitude)
        lat_dir = 'N' if self.location.latitude >= 0 else 'S'
        lon_dir = 'E' if self.location.longitude >= 0 else 'W'
        return f"{lat:.4f}°{lat_dir}, {lon:.4f}°{lon_dir}"
    
    def plot(self, shadows: List[Shadow], areas: Optional[List[Area]] = None,
             title: Optional[str] = None) -> Figure:
        """Create a complete plot with walls, shadows, areas, and compass.
        
        Args:
            shadows: List of shadows to plot
            areas: Optional list of areas to plot
            title: Optional title for the plot
            
        Returns:
            Matplotlib figure
        """
        # Create figure and axes
        fig, ax = plt.subplots(figsize=self.config.figure_size)
        
        # Plot areas first (if any)
        if areas:
            self.area_plotter.plot_areas(areas, ax)
        
        # Plot shadows and walls
        self.shadow_plotter.plot_shadows(shadows, ax, self.config.show_dimensions)
        
        # Get plot limits considering both shadows and areas
        if self.config.x_limits is not None and self.config.y_limits is not None:
            # Use configured limits
            x_min, x_max = self.config.x_limits
            y_min, y_max = self.config.y_limits
        else:
            # Calculate limits from content
            shadow_limits = self.shadow_plotter.get_plot_limits(shadows)
            if areas:
                area_limits = self.area_plotter.get_plot_limits(areas)
                x_min = min(shadow_limits[0], area_limits[0])
                x_max = max(shadow_limits[1], area_limits[1])
                y_min = min(shadow_limits[2], area_limits[2])
                y_max = max(shadow_limits[3], area_limits[3])
            else:
                x_min, x_max, y_min, y_max = shadow_limits
            
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        
        # Add compass if requested
        if self.config.show_compass and shadows:
            # Calculate compass size and position
            plot_width = x_max - x_min
            plot_height = y_max - y_min
            compass_size = min(plot_width, plot_height) * 0.1
            
            # Position in bottom right with padding
            padding = compass_size * 0.5
            corner_x = x_max - compass_size - padding
            corner_y = y_min + compass_size + padding
            
            # Plot compass
            self.compass_plotter.plot_compass(
                ax=ax,
                corner_x=corner_x,
                corner_y=corner_y,
                size=compass_size,
                shadow=shadows[0]
            )
        
        # Set title
        if shadows:
            time_str = self.config.format_time(shadows[0].time)
            location_str = self.format_location()
            if title:
                title = f"{title}\n{location_str}"
            else:
                title = f"Shadow Calculations for {time_str}\n{location_str}"
        ax.set_title(title)
        
        # Add legend
        ax.legend(
            bbox_to_anchor=(1.05, 1),
            loc='upper left',
            borderaxespad=0
        )
        
        # Set equal aspect ratio
        ax.set_aspect('equal')
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        return fig
    
    def create_animation(self, all_shadows: List[List[Shadow]], 
                        areas: Optional[List[Area]] = None) -> None:
        """Create animation from shadow calculations.
        
        Args:
            all_shadows: List of shadow lists, one for each time point
            areas: Optional list of areas to plot
        """
        if not self.animation_config.enabled or not all_shadows:
            return
            
        # Create figure and axes
        fig, ax = plt.subplots(figsize=self.config.figure_size)
        
        # Get plot limits
        if self.config.x_limits is not None and self.config.y_limits is not None:
            # Use configured limits
            x_min, x_max = self.config.x_limits
            y_min, y_max = self.config.y_limits
        else:
            # Calculate limits from all shadows and areas
            all_shadow_limits = [
                self.shadow_plotter.get_plot_limits(shadows)
                for shadows in all_shadows
            ]
            x_min = min(limits[0] for limits in all_shadow_limits)
            x_max = max(limits[1] for limits in all_shadow_limits)
            y_min = min(limits[2] for limits in all_shadow_limits)
            y_max = max(limits[3] for limits in all_shadow_limits)
            
            # Include area limits if present
            if areas:
                area_limits = self.area_plotter.get_plot_limits(areas)
                x_min = min(x_min, area_limits[0])
                x_max = max(x_max, area_limits[1])
                y_min = min(y_min, area_limits[2])
                y_max = max(y_max, area_limits[3])
        
        # Set fixed plot limits
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        
        # Calculate compass position
        plot_width = x_max - x_min
        plot_height = y_max - y_min
        compass_size = min(plot_width, plot_height) * 0.1
        padding = compass_size * 0.5
        corner_x = x_max - compass_size - padding
        corner_y = y_min + compass_size + padding
        
        # Animation update function
        def update(frame):
            ax.clear()
            shadows = all_shadows[frame]
            
            # Plot areas first (if any)
            if areas:
                self.area_plotter.plot_areas(areas, ax)
            
            # Plot shadows and walls
            self.shadow_plotter.plot_shadows(shadows, ax, self.config.show_dimensions)
            
            # Add compass if requested
            if self.config.show_compass:
                self.compass_plotter.plot_compass(
                    ax=ax,
                    corner_x=corner_x,
                    corner_y=corner_y,
                    size=compass_size,
                    shadow=shadows[0]
                )
            
            # Set title
            time_str = self.config.format_time(shadows[0].time)
            location_str = self.format_location()
            ax.set_title(f"Shadow Calculations for {time_str}\n{location_str}")
            
            # Add legend
            ax.legend(
                bbox_to_anchor=(1.05, 1),
                loc='upper left',
                borderaxespad=0
            )
            
            # Set equal aspect ratio
            ax.set_aspect('equal')
            
            # Add grid and labels
            ax.grid(True, linestyle='--', alpha=0.3)
            unit = self.config.output_units
            ax.set_xlabel(f'Distance ({unit})')
            ax.set_ylabel(f'Distance ({unit})')
            
            # Set fixed limits
            ax.set_xlim(x_min, x_max)
            ax.set_ylim(y_min, y_max)
            
            return ax,
        
        # Create animation
        anim = FuncAnimation(
            fig=fig,
            func=update,
            frames=len(all_shadows),
            interval=1000 / self.animation_config.fps,  # Convert to milliseconds
            blit=False,
            repeat=self.animation_config.loop
        )
        
        # Save animation
        if self.animation_config.save_path.endswith('.gif'):
            writer = PillowWriter(
                fps=self.animation_config.fps,
                metadata=dict(artist='Shadow Calculator')
            )
        else:  # .mp4
            writer = FFMpegWriter(
                fps=self.animation_config.fps,
                metadata=dict(artist='Shadow Calculator')
            )
        
        anim.save(
            self.animation_config.save_path,
            writer=writer,
            dpi=self.config.dpi
        )
        
        # Close figure to free memory
        plt.close(fig)
    
    def save(self, fig: Figure, filename: str) -> None:
        """Save the figure to a file.
        
        Args:
            fig: Figure to save
            filename: Output filename (should end in .png, .pdf, etc.)
        """
        fig.savefig(filename, bbox_inches='tight', dpi=self.config.dpi)
