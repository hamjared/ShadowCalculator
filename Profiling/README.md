# Shadow Calculator Profiling Tools

This directory contains tools for profiling the shadow calculator performance.

## Tools

### profile_animation.py
Profiles the animation creation process using:
- cProfile for function-level profiling
- line_profiler for line-level profiling

Usage:
```bash
python Profiling/profile_animation.py
```

Results show:
1. Function-level timing breakdown
2. Line-by-line timing for key functions
3. Memory usage statistics

## Adding New Profiling Tools

When adding new profiling tools:
1. Create a new Python file in this directory
2. Add documentation in this README
3. Use both cProfile and line_profiler when appropriate
4. Focus on specific functionality (e.g., shadow calculation, plotting)
