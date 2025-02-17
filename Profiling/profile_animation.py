#!/usr/bin/env python3
import os
import sys
import cProfile
import pstats
from pstats import SortKey
from line_profiler import LineProfiler

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from ShadowCalculator import ShadowCalculator
from Plotting.Plotter import Plotter

def profile_animation():
    """Profile animation creation."""
    # Create calculator
    example_path = os.path.join(project_root, 'Examples', 'example_animation.yml')
    calculator = ShadowCalculator.from_input_file(example_path)
    
    # Calculate shadows
    all_shadows = calculator.calculate()
    
    # Create animation
    calculator.create_animation(all_shadows)

def profile_with_cprofile():
    """Profile using cProfile for function-level profiling."""
    print("\nFunction-level profiling with cProfile:")
    print("-" * 50)
    
    # Run profiler
    profiler = cProfile.Profile()
    profiler.enable()
    profile_animation()
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
    profiler.add_function(Plotter.create_animation)
    profiler.add_function(Plotter.plot)
    
    # Wrap main function
    wrapped = profiler(profile_animation)
    
    # Run profiler
    wrapped()
    
    # Print stats
    profiler.print_stats()

if __name__ == '__main__':
    print("Profiling shadow animation creation...")
    
    # Run both profilers
    profile_with_cprofile()
    profile_with_line_profiler()
