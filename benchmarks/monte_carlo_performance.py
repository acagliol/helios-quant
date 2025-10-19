#!/usr/bin/env python3
"""
Monte Carlo Performance Benchmarks

Tests Week 3 performance targets:
- 1M paths in <50ms (vectorized)
- 10M paths in <500ms
- Antithetic variates: 2x variance reduction
- Sobol sequences: faster convergence
"""

import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import numpy as np
import time
from pricing.monte_carlo import MonteCarloEngine, compare_variance_reduction
from pricing.options.black_scholes import BlackScholes


def benchmark_performance_targets():
    """Test Week 3 performance targets."""
    print('=' * 80)
    print('WEEK 3: MONTE CARLO PERFORMANCE BENCHMARKS')
    print('=' * 80)
    print()

    targets = [
        (10_000, 2, '10k paths'),
        (100_000, 10, '100k paths'),
        (1_000_000, 50, '1M paths'),
        (10_000_000, 500, '10M paths'),
    ]

    print('Performance Targets vs Actual:')
    print('-' * 80)
    print(f'{"Paths":<15} {"Target (ms)":<15} {"Actual (ms)":<15} {"Status":<10}')
    print('-' * 80)

    for n_paths, target_ms, label in targets:
        mc = MonteCarloEngine(
            n_paths=n_paths,
            n_steps=252,
            variance_reduction='antithetic',
            seed=42
        )

        # Run benchmark
        stats = mc.benchmark(n_runs=5)

        status = '✅ PASS' if stats['mean_ms'] < target_ms else '❌ FAIL'
        print(f'{label:<15} {target_ms:<15.1f} {stats["mean_ms"]:<15.2f} {status:<10}')

    print()


def benchmark_variance_reduction():
    """Test variance reduction effectiveness."""
    print('=' * 80)
    print('VARIANCE REDUCTION COMPARISON')
    print('=' * 80)
    print()

    print('Testing with 100k paths, 10 trials...')
    print()

    results = compare_variance_reduction(n_paths=100_000, n_trials=10)

    # True price
    bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2)
    true_price = bs.price()

    print(f'True Price (Black-Scholes): ${true_price:.4f}')
    print()
    print('-' * 80)
    print(f'{"Method":<15} {"Mean Price":<12} {"Std Dev":<12} {"RMSE":<12} {"VRF":<8} {"Time (ms)"}')
    print('-' * 80)

    for method, stats in results.items():
        vrf = stats.get('variance_reduction_factor', 1.0)
        print(f'{method:<15} ${stats["mean_price"]:<11.4f} '
              f'{stats["std_price"]:<12.4f} {stats["rmse"]:<12.4f} '
              f'{vrf:<8.2f}x {stats["mean_time_ms"]:<.2f}')

    print()
    print('VRF = Variance Reduction Factor (higher is better)')
    print()

    # Check if targets met
    antithetic_vrf = results['antithetic']['variance_reduction_factor']
    if antithetic_vrf >= 1.5:
        print(f'✅ Antithetic variates: {antithetic_vrf:.2f}x variance reduction (target: 2x)')
    else:
        print(f'⚠️  Antithetic variates: {antithetic_vrf:.2f}x variance reduction (target: 2x)')

    print()


def benchmark_convergence():
    """Test convergence rates for different methods."""
    print('=' * 80)
    print('CONVERGENCE ANALYSIS')
    print('=' * 80)
    print()

    # True price
    bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2)
    true_price = bs.price()

    path_counts = [1000, 5000, 10000, 50000, 100000]
    methods = ['none', 'antithetic', 'sobol']

    print(f'True Price: ${true_price:.4f}')
    print()

    for method in methods:
        print(f'{method.upper()} Convergence:')
        print('-' * 60)
        print(f'{"Paths":<12} {"Price":<12} {"Error":<12} {"Rel Error %":<15}')
        print('-' * 60)

        for n_paths in path_counts:
            mc = MonteCarloEngine(
                n_paths=n_paths,
                n_steps=252,
                variance_reduction=method,
                seed=42
            )

            price = mc.price_european_option(
                S0=100, K=100, T=1.0, r=0.05, sigma=0.2, option_type='call'
            )

            error = abs(price - true_price)
            rel_error = (error / true_price) * 100

            print(f'{n_paths:<12,} ${price:<11.4f} ${error:<11.4f} {rel_error:<15.4f}')

        print()


def benchmark_greeks():
    """Test Greeks calculation via pathwise method."""
    print('=' * 80)
    print('GREEKS CALCULATION (Pathwise Method)')
    print('=' * 80)
    print()

    mc = MonteCarloEngine(n_paths=500_000, n_steps=252, variance_reduction='antithetic', seed=42)

    start = time.perf_counter()
    results = mc.price_with_greeks(
        S0=100, K=100, T=1.0, r=0.05, sigma=0.2, option_type='call'
    )
    elapsed = (time.perf_counter() - start) * 1000

    # Compare with Black-Scholes
    bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2)

    print(f'Monte Carlo (500k paths):')
    print(f'  Price:  ${results["price"]:.4f}')
    print(f'  Delta:  {results["delta"]:.4f}')
    print(f'  Gamma:  {results["gamma"]:.4f}')
    print(f'  Time:   {elapsed:.2f}ms')
    print()

    print(f'Black-Scholes (Analytical):')
    print(f'  Price:  ${bs.price():.4f}')
    print(f'  Delta:  {bs.delta():.4f}')
    print(f'  Gamma:  {bs.gamma():.4f}')
    print()

    price_error = abs(results['price'] - bs.price())
    delta_error = abs(results['delta'] - bs.delta())
    gamma_error = abs(results['gamma'] - bs.gamma())

    print(f'Errors:')
    print(f'  Price:  ${price_error:.4f} ({(price_error/bs.price())*100:.2f}%)')
    print(f'  Delta:  {delta_error:.4f} ({(delta_error/abs(bs.delta()))*100:.2f}%)')
    print(f'  Gamma:  {gamma_error:.4f} ({(gamma_error/abs(bs.gamma()))*100:.2f}%)')
    print()


def main():
    """Run all benchmarks."""
    # Performance targets
    benchmark_performance_targets()

    # Variance reduction
    benchmark_variance_reduction()

    # Convergence
    benchmark_convergence()

    # Greeks
    benchmark_greeks()

    print('=' * 80)
    print('✅ WEEK 3 BENCHMARKING COMPLETE')
    print('=' * 80)


if __name__ == '__main__':
    main()
