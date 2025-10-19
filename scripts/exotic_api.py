#!/usr/bin/env python3
"""
Exotic options API script for web interface.
"""

import sys
import json
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from pricing.options.exotics import (
    AsianOption, BarrierOption, LookbackOption, DigitalOption, SimulationParams
)


def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Invalid number of arguments"}), file=sys.stderr)
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])
        exotic_type = params.get('exotic_type')

        S = params['S']
        K = params.get('K')
        T = params['T']
        r = params['r']
        sigma = params['sigma']
        option_type = params.get('option_type', 'call')
        q = params.get('q', 0.0)

        # Simulation params for MC-based options
        sim_params = SimulationParams(n_paths=50000, n_steps=252, antithetic=True, seed=42)

        result = {}

        if exotic_type == 'asian':
            average_type = params.get('average_type', 'arithmetic')
            option = AsianOption(
                S=S, K=K, T=T, r=r, sigma=sigma,
                option_type=option_type,
                average_type=average_type,
                q=q
            )
            result['price'] = option.price(sim_params)

        elif exotic_type == 'barrier':
            barrier = params['barrier']
            barrier_type = params.get('barrier_type', 'up-and-out')
            option = BarrierOption(
                S=S, K=K, T=T, r=r, sigma=sigma,
                barrier=barrier,
                barrier_type=barrier_type,
                option_type=option_type,
                q=q
            )
            result['price'] = option.price(sim_params)

        elif exotic_type == 'lookback':
            strike_type = params.get('strike_type', 'floating')
            option = LookbackOption(
                S=S, K=K, T=T, r=r, sigma=sigma,
                option_type=option_type,
                strike_type=strike_type,
                q=q
            )
            result['price'] = option.price(sim_params)

        elif exotic_type == 'digital':
            payout_type = params.get('payout_type', 'cash')
            payout_amount = params.get('payout_amount', 1.0)
            option = DigitalOption(
                S=S, K=K, T=T, r=r, sigma=sigma,
                option_type=option_type,
                payout_type=payout_type,
                payout_amount=payout_amount,
                q=q
            )
            result['price'] = option.price()

        else:
            raise ValueError(f"Unknown exotic type: {exotic_type}")

        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"error": f"Calculation error: {str(e)}"}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
