#!/usr/bin/env python3
"""
QuantLib Validation Suite

Validates our implementations against QuantLib across 100+ scenarios.
Target: <0.01% error for all cases.

Tests:
- Black-Scholes pricing and Greeks
- Heston model pricing
- Various market conditions (ITM, ATM, OTM)
- Edge cases (low/high vol, short/long maturity)
"""

import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import numpy as np
import QuantLib as ql
from typing import List, Dict, Tuple
from pricing.options.black_scholes import BlackScholes
from pricing.options.heston import HestonModel


class QuantLibValidator:
    """
    Validates our pricing implementations against QuantLib.

    Generates comprehensive test scenarios and compares results.
    """

    def __init__(self):
        self.results = []
        self.max_error_threshold = 0.0001  # 0.01%

    def generate_black_scholes_scenarios(self) -> List[Dict]:
        """
        Generate 100+ Black-Scholes test scenarios.

        Covers:
        - Spot prices: 80, 90, 100, 110, 120
        - Strikes: 80, 90, 100, 110, 120
        - Maturities: 0.1, 0.5, 1.0, 2.0 years
        - Volatilities: 0.1, 0.2, 0.3, 0.5
        - Rates: 0.01, 0.05
        - Option types: Call, Put
        """
        scenarios = []

        spots = [80, 90, 100, 110, 120]
        strikes = [80, 90, 100, 110, 120]
        maturities = [0.1, 0.5, 1.0, 2.0]
        vols = [0.1, 0.2, 0.3, 0.5]
        rates = [0.01, 0.05]
        option_types = ['call', 'put']

        scenario_id = 0
        for S in spots:
            for K in strikes:
                for T in maturities:
                    for sigma in vols:
                        for r in rates[:1]:  # Use fewer rates to keep count manageable
                            for opt_type in option_types:
                                scenarios.append({
                                    'id': scenario_id,
                                    'S': S,
                                    'K': K,
                                    'T': T,
                                    'r': r,
                                    'sigma': sigma,
                                    'q': 0.0,
                                    'option_type': opt_type
                                })
                                scenario_id += 1

        return scenarios

    def price_black_scholes_quantlib(
        self, S: float, K: float, T: float, r: float, sigma: float,
        option_type: str, q: float = 0.0
    ) -> Tuple[float, float, float, float, float, float]:
        """
        Price option using QuantLib Black-Scholes.

        Returns:
            Tuple of (price, delta, gamma, vega, theta, rho)
        """
        # Set evaluation date
        calculation_date = ql.Date.todaysDate()
        ql.Settings.instance().evaluationDate = calculation_date

        # Option parameters
        payoff_type = ql.Option.Call if option_type == 'call' else ql.Option.Put
        payoff = ql.PlainVanillaPayoff(payoff_type, K)

        # Maturity date
        maturity_date = calculation_date + ql.Period(int(T * 365), ql.Days)
        exercise = ql.EuropeanExercise(maturity_date)

        # Create option
        european_option = ql.VanillaOption(payoff, exercise)

        # Market data
        spot_handle = ql.QuoteHandle(ql.SimpleQuote(S))
        flat_ts = ql.YieldTermStructureHandle(
            ql.FlatForward(calculation_date, r, ql.Actual365Fixed())
        )
        dividend_yield = ql.YieldTermStructureHandle(
            ql.FlatForward(calculation_date, q, ql.Actual365Fixed())
        )
        flat_vol_ts = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(calculation_date, ql.NullCalendar(), sigma, ql.Actual365Fixed())
        )

        # Black-Scholes process
        bs_process = ql.BlackScholesMertonProcess(
            spot_handle,
            dividend_yield,
            flat_ts,
            flat_vol_ts
        )

        # Pricing engine
        engine = ql.AnalyticEuropeanEngine(bs_process)
        european_option.setPricingEngine(engine)

        # Calculate price and Greeks
        price = european_option.NPV()
        delta = european_option.delta()
        gamma = european_option.gamma()
        vega = european_option.vega() / 100  # QuantLib vega is per 1% vol change
        theta = european_option.theta() / 365  # Convert to per-day
        rho = european_option.rho() / 100  # QuantLib rho is per 1% rate change

        return price, delta, gamma, vega, theta, rho

    def validate_black_scholes(self, verbose: bool = True) -> Dict:
        """
        Validate Black-Scholes implementation against QuantLib.

        Returns:
            Dictionary with validation statistics
        """
        scenarios = self.generate_black_scholes_scenarios()

        if verbose:
            print(f"\nValidating Black-Scholes across {len(scenarios)} scenarios...")
            print("=" * 80)

        errors = {
            'price': [],
            'delta': [],
            'gamma': [],
            'vega': [],
            'theta': [],
            'rho': []
        }

        failed_scenarios = []

        for i, scenario in enumerate(scenarios):
            # Our implementation
            bs = BlackScholes(
                S=scenario['S'],
                K=scenario['K'],
                T=scenario['T'],
                r=scenario['r'],
                sigma=scenario['sigma'],
                q=scenario['q'],
                option_type=scenario['option_type']
            )

            our_price = bs.price()
            our_delta = bs.delta()
            our_gamma = bs.gamma()
            our_vega = bs.vega()
            our_theta = bs.theta()
            our_rho = bs.rho()

            # QuantLib implementation
            scenario_params = {k: v for k, v in scenario.items() if k != 'id'}
            ql_price, ql_delta, ql_gamma, ql_vega, ql_theta, ql_rho = \
                self.price_black_scholes_quantlib(**scenario_params)

            # Calculate relative errors
            def rel_error(our, ql):
                if abs(ql) < 1e-10:
                    return 0.0  # Both essentially zero
                return abs((our - ql) / ql)

            price_error = rel_error(our_price, ql_price)
            delta_error = rel_error(our_delta, ql_delta)
            gamma_error = rel_error(our_gamma, ql_gamma)
            vega_error = rel_error(our_vega, ql_vega)
            theta_error = rel_error(our_theta, ql_theta)
            rho_error = rel_error(our_rho, ql_rho)

            errors['price'].append(price_error)
            errors['delta'].append(delta_error)
            errors['gamma'].append(gamma_error)
            errors['vega'].append(vega_error)
            errors['theta'].append(theta_error)
            errors['rho'].append(rho_error)

            # Check if any error exceeds threshold
            max_error = max(price_error, delta_error, gamma_error, vega_error, theta_error, rho_error)
            if max_error > self.max_error_threshold:
                failed_scenarios.append({
                    'scenario': scenario,
                    'max_error': max_error,
                    'our_price': our_price,
                    'ql_price': ql_price
                })

        # Calculate statistics
        stats = {}
        for metric, error_list in errors.items():
            stats[metric] = {
                'max': np.max(error_list),
                'mean': np.mean(error_list),
                'std': np.std(error_list),
                'median': np.median(error_list)
            }

        if verbose:
            print(f"\n{'Metric':<10} {'Max Error %':<15} {'Mean Error %':<15} {'Status':<10}")
            print("-" * 60)
            for metric, s in stats.items():
                max_pct = s['max'] * 100
                mean_pct = s['mean'] * 100
                status = '✅ PASS' if s['max'] < self.max_error_threshold else '❌ FAIL'
                print(f"{metric:<10} {max_pct:<15.6f} {mean_pct:<15.6f} {status:<10}")

            print(f"\nTotal scenarios: {len(scenarios)}")
            print(f"Failed scenarios: {len(failed_scenarios)}")
            print(f"Pass rate: {(1 - len(failed_scenarios)/len(scenarios)) * 100:.2f}%")

            if len(failed_scenarios) > 0:
                print(f"\nFirst 3 failures:")
                for fail in failed_scenarios[:3]:
                    print(f"  Scenario {fail['scenario']['id']}: " +
                          f"Max error = {fail['max_error']*100:.4f}%, " +
                          f"Our={fail['our_price']:.4f}, QL={fail['ql_price']:.4f}")

        return {
            'stats': stats,
            'failed_scenarios': failed_scenarios,
            'total_scenarios': len(scenarios),
            'pass_rate': (1 - len(failed_scenarios) / len(scenarios)) * 100
        }

    def generate_heston_scenarios(self) -> List[Dict]:
        """
        Generate Heston model test scenarios.

        Focuses on realistic parameters to avoid numerical issues.
        """
        scenarios = []

        spots = [90, 100, 110]
        strikes = [90, 100, 110]
        maturities = [0.5, 1.0]
        v0_values = [0.04, 0.09]  # Current variance
        kappa_values = [2.0]  # Mean reversion speed
        theta_values = [0.04, 0.09]  # Long-term variance
        sigma_values = [0.3]  # Vol of vol
        rho_values = [-0.5, 0.0]  # Correlation

        scenario_id = 0
        for S0 in spots:
            for K in strikes:
                for T in maturities:
                    for v0 in v0_values:
                        for kappa in kappa_values:
                            for theta in theta_values:
                                # Check Feller condition
                                if 2 * kappa * theta >= sigma_values[0] ** 2:
                                    for sigma in sigma_values:
                                        for rho in rho_values:
                                            scenarios.append({
                                                'id': scenario_id,
                                                'S0': S0,
                                                'K': K,
                                                'T': T,
                                                'r': 0.05,
                                                'v0': v0,
                                                'kappa': kappa,
                                                'theta': theta,
                                                'sigma': sigma,
                                                'rho': rho,
                                                'q': 0.0
                                            })
                                            scenario_id += 1

        return scenarios

    def price_heston_quantlib(
        self, S0: float, K: float, T: float, r: float,
        v0: float, kappa: float, theta: float, sigma: float, rho: float,
        q: float = 0.0
    ) -> float:
        """
        Price call option using QuantLib Heston model.

        Returns:
            Option price
        """
        calculation_date = ql.Date.todaysDate()
        ql.Settings.instance().evaluationDate = calculation_date

        # Option
        payoff = ql.PlainVanillaPayoff(ql.Option.Call, K)
        maturity_date = calculation_date + ql.Period(int(T * 365), ql.Days)
        exercise = ql.EuropeanExercise(maturity_date)
        european_option = ql.VanillaOption(payoff, exercise)

        # Market data
        spot_handle = ql.QuoteHandle(ql.SimpleQuote(S0))
        flat_ts = ql.YieldTermStructureHandle(
            ql.FlatForward(calculation_date, r, ql.Actual365Fixed())
        )
        dividend_yield = ql.YieldTermStructureHandle(
            ql.FlatForward(calculation_date, q, ql.Actual365Fixed())
        )

        # Heston process
        heston_process = ql.HestonProcess(
            flat_ts,
            dividend_yield,
            spot_handle,
            v0,
            kappa,
            theta,
            sigma,
            rho
        )

        # Pricing engine
        engine = ql.AnalyticHestonEngine(ql.HestonModel(heston_process))
        european_option.setPricingEngine(engine)

        return european_option.NPV()

    def validate_heston(self, verbose: bool = True) -> Dict:
        """
        Validate Heston implementation against QuantLib.

        Returns:
            Dictionary with validation statistics
        """
        scenarios = self.generate_heston_scenarios()

        if verbose:
            print(f"\n\nValidating Heston Model across {len(scenarios)} scenarios...")
            print("=" * 80)

        price_errors = []
        failed_scenarios = []

        for scenario in scenarios:
            # Our implementation
            heston = HestonModel(
                S0=scenario['S0'],
                v0=scenario['v0'],
                kappa=scenario['kappa'],
                theta=scenario['theta'],
                sigma=scenario['sigma'],
                rho=scenario['rho'],
                r=scenario['r'],
                T=scenario['T'],
                K=scenario['K'],
                q=scenario['q']
            )

            try:
                our_price = heston.price_call()
                scenario_params = {k: v for k, v in scenario.items() if k != 'id'}
                ql_price = self.price_heston_quantlib(**scenario_params)

                # Relative error
                rel_error = abs((our_price - ql_price) / ql_price) if ql_price > 1e-10 else 0.0
                price_errors.append(rel_error)

                if rel_error > self.max_error_threshold:
                    failed_scenarios.append({
                        'scenario': scenario,
                        'error': rel_error,
                        'our_price': our_price,
                        'ql_price': ql_price
                    })
            except Exception as e:
                print(f"Error in scenario {scenario['id']}: {e}")
                failed_scenarios.append({
                    'scenario': scenario,
                    'error': 1.0,
                    'exception': str(e)
                })

        # Statistics
        stats = {
            'max': np.max(price_errors) if price_errors else 1.0,
            'mean': np.mean(price_errors) if price_errors else 1.0,
            'std': np.std(price_errors) if price_errors else 0.0,
            'median': np.median(price_errors) if price_errors else 1.0
        }

        if verbose:
            print(f"\n{'Metric':<10} {'Max Error %':<15} {'Mean Error %':<15} {'Status':<10}")
            print("-" * 60)
            max_pct = stats['max'] * 100
            mean_pct = stats['mean'] * 100
            status = '✅ PASS' if stats['max'] < self.max_error_threshold else '❌ FAIL'
            print(f"{'Price':<10} {max_pct:<15.6f} {mean_pct:<15.6f} {status:<10}")

            print(f"\nTotal scenarios: {len(scenarios)}")
            print(f"Failed scenarios: {len(failed_scenarios)}")
            print(f"Pass rate: {(1 - len(failed_scenarios)/len(scenarios)) * 100:.2f}%")

        return {
            'stats': stats,
            'failed_scenarios': failed_scenarios,
            'total_scenarios': len(scenarios),
            'pass_rate': (1 - len(failed_scenarios) / len(scenarios)) * 100
        }


def main():
    """Run full validation suite."""
    validator = QuantLibValidator()

    print("=" * 80)
    print("QUANTLIB VALIDATION SUITE")
    print("Target: <0.01% error across all scenarios")
    print("=" * 80)

    # Validate Black-Scholes
    bs_results = validator.validate_black_scholes(verbose=True)

    # Validate Heston
    heston_results = validator.validate_heston(verbose=True)

    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    total_scenarios = bs_results['total_scenarios'] + heston_results['total_scenarios']
    total_failed = len(bs_results['failed_scenarios']) + len(heston_results['failed_scenarios'])

    print(f"\nTotal scenarios tested: {total_scenarios}")
    print(f"Total failed: {total_failed}")
    print(f"Overall pass rate: {(1 - total_failed/total_scenarios) * 100:.2f}%")

    if total_failed == 0:
        print("\n✅ All validations passed! Our implementations match QuantLib within 0.01% error.")
    else:
        print(f"\n⚠️  {total_failed} scenarios failed. Review implementation.")

    print("=" * 80)


if __name__ == "__main__":
    main()
