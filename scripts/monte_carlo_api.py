#!/usr/bin/env python3
"""
Monte Carlo API script for web interface.
"""

import sys
import json
import os
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from pricing.monte_carlo import MonteCarloEngine


def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Invalid number of arguments"}), file=sys.stderr)
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])

        S = params['S']
        K = params['K']
        T = params['T']
        r = params['r']
        sigma = params['sigma']
        option_type = params.get('option_type', 'call')
        q = params.get('q', 0.0)
        n_paths = params.get('n_paths', 100000)
        variance_reduction = params.get('variance_reduction', 'antithetic')

        # Create Monte Carlo engine
        mc = MonteCarloEngine(
            n_paths=n_paths,
            n_steps=252,
            variance_reduction=variance_reduction,
            seed=42
        )

        # Price the option and measure time
        start = time.perf_counter()
        price = mc.price_european_option(
            S0=S, K=K, T=T, r=r, sigma=sigma,
            option_type=option_type, q=q
        )
        elapsed = (time.perf_counter() - start) * 1000

        # Also compute convergence analysis with different path counts
        convergence = []
        path_counts = [10_000, 50_000, 100_000]
        if n_paths > 100_000:
            path_counts.append(n_paths)

        for n in path_counts:
            if n <= n_paths:
                mc_conv = MonteCarloEngine(
                    n_paths=n,
                    n_steps=252,
                    variance_reduction=variance_reduction,
                    seed=42
                )
                start_conv = time.perf_counter()
                price_conv = mc_conv.price_european_option(
                    S0=S, K=K, T=T, r=r, sigma=sigma,
                    option_type=option_type, q=q
                )
                elapsed_conv = (time.perf_counter() - start_conv) * 1000

                convergence.append({
                    'n_paths': n,
                    'price': float(price_conv),
                    'time_ms': float(elapsed_conv)
                })

        result = {
            'price': float(price),
            'time_ms': float(elapsed),
            'convergence': convergence
        }

        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"error": f"Calculation error: {str(e)}"}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
