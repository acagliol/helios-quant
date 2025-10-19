#!/usr/bin/env python3
"""
Black-Scholes API script for web interface.
Called by Next.js API route to calculate option prices and Greeks.
"""

import sys
import json
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from pricing.options.black_scholes import BlackScholes


def main():
    if len(sys.argv) != 8:
        print(json.dumps({"error": "Invalid number of arguments"}), file=sys.stderr)
        sys.exit(1)

    try:
        # Parse command line arguments
        S = float(sys.argv[1])
        K = float(sys.argv[2])
        T = float(sys.argv[3])
        r = float(sys.argv[4])
        sigma = float(sys.argv[5])
        q = float(sys.argv[6])
        option_type = sys.argv[7]

        # Create Black-Scholes instance
        bs = BlackScholes(
            S=S,
            K=K,
            T=T,
            r=r,
            sigma=sigma,
            q=q,
            option_type=option_type
        )

        # Calculate all Greeks
        result = bs.all_greeks()

        # Output as JSON
        print(json.dumps(result))

    except ValueError as e:
        print(json.dumps({"error": f"Invalid parameter: {str(e)}"}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Calculation error: {str(e)}"}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
