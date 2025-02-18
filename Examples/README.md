# Shadow Calculator Examples

This directory contains example input files demonstrating different shadow calculation scenarios.

## Files

### example_single_time.yml
- Single point in time calculation
- Two walls at right angles
- Default settings for plotting

### example_perpendicular.yml
- Test case for perpendicular sun position
- North-south wall with sun from east
- Shows rectangular shadow formation

### example_perpendicular2.yml
- Simplified test case for perpendicular shadows
- Single north-south wall
- Fixed sun position from east

### example_angles.yml
- Test case for different wall orientations
- North-south wall (perpendicular to sun)
- East-west wall (parallel to sun)
- Diagonal wall (angled to sun)
- Shows all three shadow types:
  1. Rectangular (perpendicular sun)
  2. Triangular (parallel sun)
  3. Parallelogram (angled sun)

## Usage

Run any example with:
```bash
python Main.py -i Examples/example_name.yml -v
```

The `-v` flag enables verbose output showing detailed shadow calculations.
