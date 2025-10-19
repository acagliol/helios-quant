#!/usr/bin/env python3
"""
Portfolio Optimization API script for web interface.
"""

import sys
import json
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from optimization import MarkowitzOptimizer, RiskParityOptimizer, CVaROptimizer, generate_sample_returns
import numpy as np


def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Invalid number of arguments"}), file=sys.stderr)
        sys.exit(1)

    try:
        params = json.loads(sys.argv[1])

        n_assets = params.get('n_assets', 10)
        risk_free_rate = params.get('risk_free_rate', 0.02)
        method = params.get('method', 'all')

        # Generate sample returns (in production, would load real data)
        # Using seed for consistency in demos
        returns = generate_sample_returns(n_assets=n_assets, n_periods=252, seed=42)

        results = {}

        if method == 'all' or method == 'markowitz':
            # Markowitz optimizer
            mv = MarkowitzOptimizer(returns, risk_free_rate=risk_free_rate)
            max_sharpe = mv.max_sharpe_ratio()

            results['markowitz'] = {
                'method': 'markowitz',
                'weights': max_sharpe['weights'].tolist(),
                'expected_return': float(max_sharpe['return']),
                'volatility': float(max_sharpe['volatility']),
                'sharpe_ratio': float(max_sharpe['sharpe_ratio'])
            }

        if method == 'all' or method == 'risk_parity':
            # Risk Parity optimizer
            cov_matrix = np.cov(returns, rowvar=False) * 252  # Annualize
            rp = RiskParityOptimizer(cov_matrix)
            rp_result = rp.optimize()

            # Calculate expected return for risk parity
            mean_returns = np.mean(returns, axis=0) * 252
            rp_return = np.dot(rp_result['weights'], mean_returns)

            results['risk_parity'] = {
                'method': 'risk_parity',
                'weights': rp_result['weights'].tolist(),
                'expected_return': float(rp_return),
                'volatility': float(rp_result['volatility']),
                'sharpe_ratio': float((rp_return - risk_free_rate) / rp_result['volatility']) if rp_result['volatility'] > 0 else 0.0
            }

        if method == 'all' or method == 'cvar':
            # CVaR optimizer
            cvar_opt = CVaROptimizer(returns, alpha=0.95)
            cvar_result = cvar_opt.optimize()

            results['cvar'] = {
                'method': 'cvar',
                'weights': cvar_result['weights'].tolist(),
                'expected_return': float(cvar_result['return']),
                'volatility': float(cvar_result['volatility']),
                'cvar': float(cvar_result['cvar']),
                'sharpe_ratio': float((cvar_result['return'] - risk_free_rate) / cvar_result['volatility']) if cvar_result['volatility'] > 0 else 0.0
            }

        print(json.dumps(results))

    except Exception as e:
        print(json.dumps({"error": f"Optimization error: {str(e)}"}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
