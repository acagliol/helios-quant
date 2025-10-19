#!/usr/bin/env python3
"""
Heston model API script for web interface.
"""

import sys
import json
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from pricing.options.heston import HestonModel


def main():
    if len(sys.argv) != 11:
        print(json.dumps({"error": "Invalid number of arguments"}), file=sys.stderr)
        sys.exit(1)

    try:
        S0 = float(sys.argv[1])
        K = float(sys.argv[2])
        T = float(sys.argv[3])
        r = float(sys.argv[4])
        v0 = float(sys.argv[5])
        kappa = float(sys.argv[6])
        theta = float(sys.argv[7])
        sigma = float(sys.argv[8])
        rho = float(sys.argv[9])
        q = float(sys.argv[10])

        heston = HestonModel(
            S0=S0, v0=v0, kappa=kappa, theta=theta,
            sigma=sigma, rho=rho, r=r, T=T, K=K, q=q
        )

        result = {
            "call_price": heston.price_call(),
            "put_price": heston.price_put(),
            "implied_vol": heston.implied_volatility('call')
        }

        print(json.dumps(result))

    except ValueError as e:
        print(json.dumps({"error": f"Invalid parameter: {str(e)}"}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Calculation error: {str(e)}"}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
