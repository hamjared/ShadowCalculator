#!/usr/bin/env python3
import argparse
import sys
from ShadowCalculator import ShadowCalculator

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
    
    args = parser.parse_args()
    
    try:
        # Create calculator from input file
        calculator = ShadowCalculator.from_input_file(args.input)
        
        # Calculate shadows
        results = calculator.calculate()
        
        # Print results
        if args.verbose:
            print("\nInput Summary:")
            print(f"Location: {results['location']}")
            print(f"Walls: {', '.join(results['walls'])}")
            print("\nCalculations:")
            
        print(results)  # TODO: Format results nicely
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
