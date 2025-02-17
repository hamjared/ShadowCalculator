#!/usr/bin/env python3
import argparse
import sys
from datetime import datetime
from ShadowCalculator import ShadowCalculator
from tqdm import tqdm

def format_shadow_results(shadows, verbose: bool = False) -> str:
    """Format shadow calculation results as a string."""
    if not shadows:
        return "No shadows calculated"
        
    # Get time from first shadow
    time = shadows[0].time
    
    if verbose:
        lines = [f"\nShadow calculations for {time.strftime('%Y-%m-%d %H:%M %Z')}:"]
        for shadow in shadows:
            lines.extend([
                f"\nWall: {shadow.wall.name}",
                f"  Wall dimensions:",
                f"    Height: {shadow.wall.height:~P}",
                f"    Start: ({shadow.wall.start_point.x:~P}, {shadow.wall.start_point.y:~P})",
                f"    End: ({shadow.wall.end_point.x:~P}, {shadow.wall.end_point.y:~P})",
                f"  Shadow dimensions:",
                f"    Length from wall: {shadow.length:~P}",
                f"    Width at end: {shadow.width:~P}",
                f"    Total area: {shadow.area:~P}",
                f"    Direction: {shadow.angle:.1f}° from north",
                f"  Sun position:",
                f"    Elevation: {shadow.solar_elevation:.1f}°",
                f"    Azimuth: {shadow.solar_azimuth:.1f}° from north"
            ])
        return "\n".join(lines)
    else:
        # Compact format
        return (
            f"{time.strftime('%H:%M')}: "
            + ", ".join(
                f"{s.wall.name} shadow: {s.length:~P} long × {s.width:~P} wide"
                for s in shadows
            )
        )

def main():
    """Main entry point for the shadow calculator."""
    parser = argparse.ArgumentParser(
        description="Calculate shadows cast by walls at a specific location"
    )
    parser.add_argument(
        '-i', '--input',
        type=str,
        required=True,
        help='Path to input YAML file'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--progress',
        action='store_true',
        help='Show progress bar for time range calculations'
    )
    parser.add_argument(
        '--no-plot',
        action='store_true',
        help='Disable plotting even if enabled in input file'
    )
    
    args = parser.parse_args()
    
    try:
        # Create calculator from input file
        calculator = ShadowCalculator.from_input_file(args.input)
        
        # Override plot config if --no-plot specified
        if args.no_plot:
            calculator.plot_config.enabled = False
        
        # Get time specification info
        num_points, time_desc = calculator.time_spec.get_progress_info()
        
        # Show calculation info
        print(f"\nLocation: {calculator.location}")
        print(f"Number of walls: {len(calculator.walls)}")
        print(f"Time points: {time_desc}")
        if calculator.plot_config.enabled:
            if calculator.plot_config.save_path:
                print(f"Plots will be saved to: {calculator.plot_config.save_path}")
            else:
                print("Plots will be displayed")
        
        # Calculate shadows
        all_shadows = calculator.calculate()
        
        # Print results
        if calculator.time_spec.is_point:
            # Single time point
            shadows = all_shadows[0]
            print(format_shadow_results(shadows, args.verbose))
            if calculator.plot_config.enabled:
                calculator.plot_shadows(shadows)
        else:
            # Time range
            print("\nShadow calculations:")
            if args.progress:
                for shadows in tqdm(all_shadows, total=num_points):
                    print(format_shadow_results(shadows, args.verbose))
                    if calculator.plot_config.enabled:
                        calculator.plot_shadows(shadows)
            else:
                for shadows in all_shadows:
                    print(format_shadow_results(shadows, args.verbose))
                    if calculator.plot_config.enabled:
                        calculator.plot_shadows(shadows)
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
