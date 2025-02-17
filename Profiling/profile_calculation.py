#!/usr/bin/env python3
import os
import sys
import cProfile
import pstats
from pstats import SortKey
from line_profiler import LineProfiler
import timeit

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from ShadowCalculator import ShadowCalculator
from Calculation.ShadowCalculations import ShadowCalculations
from Calculation.Sun import Sun
from DataModel.Wall import Wall
from DataModel.Point import Point, ureg
from datetime import datetime, timezone

def create_test_data():
    """Create test data for profiling."""
    # Create a set of walls at different angles
    walls = [
        # North-South wall
        Wall(
            name="North-South Wall",
            height=ureg.Quantity('10 feet'),
            start_point=Point(
                x=ureg.Quantity('0 feet'),
                y=ureg.Quantity('0 feet')
            ),
            end_point=Point(
                x=ureg.Quantity('0 feet'),
                y=ureg.Quantity('20 feet')
            )
        ),
        # East-West wall
        Wall(
            name="East-West Wall",
            height=ureg.Quantity('10 feet'),
            start_point=Point(
                x=ureg.Quantity('0 feet'),
                y=ureg.Quantity('0 feet')
            ),
            end_point=Point(
                x=ureg.Quantity('20 feet'),
                y=ureg.Quantity('0 feet')
            )
        ),
        # Diagonal wall
        Wall(
            name="Diagonal Wall",
            height=ureg.Quantity('10 feet'),
            start_point=Point(
                x=ureg.Quantity('0 feet'),
                y=ureg.Quantity('0 feet')
            ),
            end_point=Point(
                x=ureg.Quantity('20 feet'),
                y=ureg.Quantity('20 feet')
            )
        )
    ]
    
    # Create a range of times throughout the day
    times = [
        datetime(2025, 2, 17, hour, 0, tzinfo=timezone.utc)
        for hour in range(6, 19)  # 6 AM to 6 PM
    ]
    
    return walls, times

def profile_shadow_calculations():
    """Profile shadow calculation performance."""
    walls, times = create_test_data()
    
    # Calculate shadows for each wall at each time
    for time in times:
        sun_pos = Sun.get_position(
            latitude=40.7128,
            longitude=-74.0060,
            time=time
        )
        
        for wall in walls:
            shadow = ShadowCalculations.calculate_shadow(
                wall=wall,
                solar_elevation=sun_pos.elevation,
                solar_azimuth=sun_pos.azimuth,
                time=time
            )

def benchmark_calculations():
    """Run timed benchmarks for different aspects of calculation."""
    walls, times = create_test_data()
    wall = walls[0]  # Use first wall for benchmarks
    time = times[0]  # Use first time for benchmarks
    
    # Benchmark sun position calculation
    sun_time = timeit.timeit(
        lambda: Sun.get_position(40.7128, -74.0060, time),
        number=1000
    )
    print(f"\nSun position calculation (1000 iterations):")
    print(f"Total time: {sun_time:.3f}s")
    print(f"Average time: {sun_time/1000*1000:.3f}ms per calculation")
    
    # Get sun position for shadow benchmarks
    sun_pos = Sun.get_position(40.7128, -74.0060, time)
    
    # Benchmark shadow calculation
    shadow_time = timeit.timeit(
        lambda: ShadowCalculations.calculate_shadow(
            wall=wall,
            solar_elevation=sun_pos.elevation,
            solar_azimuth=sun_pos.azimuth,
            time=time
        ),
        number=1000
    )
    print(f"\nShadow calculation (1000 iterations):")
    print(f"Total time: {shadow_time:.3f}s")
    print(f"Average time: {shadow_time/1000*1000:.3f}ms per calculation")

def profile_with_cprofile():
    """Profile using cProfile for function-level profiling."""
    print("\nFunction-level profiling with cProfile:")
    print("-" * 50)
    
    # Run profiler
    profiler = cProfile.Profile()
    profiler.enable()
    profile_shadow_calculations()
    profiler.disable()
    
    # Print stats sorted by total time
    stats = pstats.Stats(profiler).sort_stats(SortKey.TIME)
    stats.print_stats(20)  # Show top 20 functions

def profile_with_line_profiler():
    """Profile using line_profiler for line-level profiling."""
    print("\nLine-level profiling with line_profiler:")
    print("-" * 50)
    
    # Create line profiler
    profiler = LineProfiler()
    
    # Profile key functions
    profiler.add_function(ShadowCalculations.calculate_shadow)
    profiler.add_function(ShadowCalculations.calculate_shadow_length)
    profiler.add_function(ShadowCalculations.calculate_shadow_vertices)
    
    # Wrap main function
    wrapped = profiler(profile_shadow_calculations)
    
    # Run profiler
    wrapped()
    
    # Print stats
    profiler.print_stats()

if __name__ == '__main__':
    print("Profiling shadow calculations...")
    
    # Run benchmarks
    benchmark_calculations()
    
    # Run profilers
    profile_with_cprofile()
    profile_with_line_profiler()
