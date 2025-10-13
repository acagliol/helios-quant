"""
Helios Quant Framework - QuantLib Integration Module
Financial calculations using QuantLib for bond pricing, IRR, duration, and risk metrics
"""

import QuantLib as ql
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import json
import os


class QuantLibFinanceCalculator:
    """QuantLib-based financial calculations for PE analytics"""

    def __init__(self):
        self.calendar = ql.UnitedStates(ql.UnitedStates.NYSE)
        self.day_count = ql.Actual365Fixed()

    def calculate_xirr(self, cash_flows: List[Tuple[datetime, float]]) -> float:
        """
        Calculate XIRR (Internal Rate of Return) for irregular cash flows

        Args:
            cash_flows: List of (date, amount) tuples

        Returns:
            XIRR as a decimal (e.g., 0.15 = 15%)
        """
        # Convert to QuantLib objects
        dates = [ql.Date(cf[0].day, cf[0].month, cf[0].year) for cf in cash_flows]
        amounts = [cf[1] for cf in cash_flows]

        # Calculate IRR using NPV solver
        try:
            # Simple IRR calculation
            cash_flow_leg = [ql.SimpleCashFlow(amt, date) for amt, date in zip(amounts, dates)]

            # Use Newton's method to find IRR
            def npv_function(rate):
                settlement = dates[0]
                npv = 0.0
                for cf, date in zip(cash_flow_leg, dates):
                    years = self.day_count.yearFraction(settlement, date)
                    npv += cf.amount() / ((1 + rate) ** years)
                return npv

            # Newton-Raphson method
            rate_guess = 0.1
            for _ in range(100):
                npv = npv_function(rate_guess)
                if abs(npv) < 0.01:
                    break
                # Numerical derivative
                delta = 0.0001
                npv_delta = npv_function(rate_guess + delta)
                derivative = (npv_delta - npv) / delta
                if abs(derivative) < 1e-10:
                    break
                rate_guess = rate_guess - npv / derivative

            return rate_guess
        except Exception:
            return np.nan

    def calculate_npv(self, cash_flows: List[Tuple[datetime, float]], discount_rate: float) -> float:
        """
        Calculate Net Present Value

        Args:
            cash_flows: List of (date, amount) tuples
            discount_rate: Discount rate as decimal

        Returns:
            NPV
        """
        dates = [ql.Date(cf[0].day, cf[0].month, cf[0].year) for cf in cash_flows]
        amounts = [cf[1] for cf in cash_flows]

        # Create discount curve
        settlement_date = dates[0]
        ql.Settings.instance().evaluationDate = settlement_date

        flat_curve = ql.FlatForward(
            settlement_date,
            ql.QuoteHandle(ql.SimpleQuote(discount_rate)),
            self.day_count
        )

        # Calculate NPV
        npv = sum(
            amt / (1 + discount_rate) ** self.day_count.yearFraction(settlement_date, date)
            for date, amt in zip(dates, amounts)
        )

        return npv

    def calculate_bond_metrics(
        self,
        face_value: float,
        coupon_rate: float,
        maturity_years: float,
        yield_rate: float,
        frequency: int = 2
    ) -> Dict:
        """
        Calculate bond price, duration, and convexity

        Args:
            face_value: Bond face value
            coupon_rate: Annual coupon rate (decimal)
            maturity_years: Years to maturity
            yield_rate: Yield to maturity (decimal)
            frequency: Coupon frequency (2 = semiannual)

        Returns:
            Dictionary with bond metrics
        """
        # Setup
        today = ql.Date.todaysDate()
        ql.Settings.instance().evaluationDate = today

        maturity_date = today + ql.Period(int(maturity_years * 12), ql.Months)

        # Create bond schedule
        schedule = ql.Schedule(
            today,
            maturity_date,
            ql.Period(ql.Semiannual if frequency == 2 else ql.Annual),
            self.calendar,
            ql.Unadjusted,
            ql.Unadjusted,
            ql.DateGeneration.Backward,
            False
        )

        # Create fixed rate bond
        bond = ql.FixedRateBond(
            0,
            face_value,
            schedule,
            [coupon_rate],
            self.day_count
        )

        # Create yield curve
        flat_curve = ql.FlatForward(
            today,
            ql.QuoteHandle(ql.SimpleQuote(yield_rate)),
            self.day_count,
            ql.Compounded,
            ql.Semiannual if frequency == 2 else ql.Annual
        )

        bond_engine = ql.DiscountingBondEngine(ql.YieldTermStructureHandle(flat_curve))
        bond.setPricingEngine(bond_engine)

        # Calculate metrics
        metrics = {
            'clean_price': bond.cleanPrice(),
            'dirty_price': bond.dirtyPrice(),
            'accrued_interest': bond.accruedAmount(),
            'yield_to_maturity': bond.bondYield(self.day_count, ql.Compounded, frequency),
            'duration': ql.BondFunctions.duration(
                bond,
                yield_rate,
                self.day_count,
                ql.Compounded,
                frequency,
                ql.Duration.Macaulay
            ),
            'modified_duration': ql.BondFunctions.duration(
                bond,
                yield_rate,
                self.day_count,
                ql.Compounded,
                frequency,
                ql.Duration.Modified
            ),
            'convexity': ql.BondFunctions.convexity(
                bond,
                yield_rate,
                self.day_count,
                ql.Compounded,
                frequency
            )
        }

        return metrics

    def calculate_option_greeks(
        self,
        spot_price: float,
        strike_price: float,
        risk_free_rate: float,
        volatility: float,
        time_to_maturity: float,
        option_type: str = 'call'
    ) -> Dict:
        """
        Calculate Black-Scholes option price and Greeks

        Args:
            spot_price: Current asset price
            strike_price: Option strike price
            risk_free_rate: Risk-free rate (decimal)
            volatility: Volatility (decimal)
            time_to_maturity: Time to expiration in years
            option_type: 'call' or 'put'

        Returns:
            Dictionary with option price and Greeks
        """
        # Setup
        today = ql.Date.todaysDate()
        ql.Settings.instance().evaluationDate = today

        maturity_date = today + ql.Period(int(time_to_maturity * 365), ql.Days)

        # Market data
        spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot_price))
        flat_ts = ql.YieldTermStructureHandle(
            ql.FlatForward(today, risk_free_rate, self.day_count)
        )
        flat_vol_ts = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(today, self.calendar, volatility, self.day_count)
        )

        # Black-Scholes process
        bs_process = ql.BlackScholesMertonProcess(
            spot_handle,
            flat_ts,
            flat_ts,
            flat_vol_ts
        )

        # Create option
        payoff = ql.PlainVanillaPayoff(
            ql.Option.Call if option_type.lower() == 'call' else ql.Option.Put,
            strike_price
        )
        exercise = ql.EuropeanExercise(maturity_date)
        option = ql.VanillaOption(payoff, exercise)

        # Pricing engine
        option.setPricingEngine(ql.AnalyticEuropeanEngine(bs_process))

        # Calculate Greeks
        greeks = {
            'price': option.NPV(),
            'delta': option.delta(),
            'gamma': option.gamma(),
            'vega': option.vega() / 100,  # Per 1% change
            'theta': option.theta() / 365,  # Per day
            'rho': option.rho() / 100  # Per 1% change
        }

        return greeks


def run_quantlib_examples():
    """Run example calculations using QuantLib"""

    calculator = QuantLibFinanceCalculator()

    print("\n=== QuantLib Finance Calculations ===\n")

    # 1. XIRR Calculation
    print("1. XIRR Calculation")
    print("-" * 40)

    cash_flows = [
        (datetime(2020, 1, 1), -1000000),  # Initial investment
        (datetime(2021, 6, 15), 150000),   # Distribution
        (datetime(2022, 3, 20), 200000),   # Distribution
        (datetime(2023, 12, 10), 1500000)  # Exit
    ]

    irr = calculator.calculate_xirr(cash_flows)
    print(f"XIRR: {irr * 100:.2f}%\n")

    # 2. Bond Metrics
    print("2. Bond Metrics")
    print("-" * 40)

    bond_metrics = calculator.calculate_bond_metrics(
        face_value=1000,
        coupon_rate=0.05,
        maturity_years=10,
        yield_rate=0.04,
        frequency=2
    )

    print(f"Clean Price: ${bond_metrics['clean_price']:.2f}")
    print(f"Dirty Price: ${bond_metrics['dirty_price']:.2f}")
    print(f"Accrued Interest: ${bond_metrics['accrued_interest']:.2f}")
    print(f"YTM: {bond_metrics['yield_to_maturity'] * 100:.2f}%")
    print(f"Macaulay Duration: {bond_metrics['duration']:.2f} years")
    print(f"Modified Duration: {bond_metrics['modified_duration']:.2f}")
    print(f"Convexity: {bond_metrics['convexity']:.2f}\n")

    # 3. Option Greeks
    print("3. Black-Scholes Option Greeks")
    print("-" * 40)

    option_greeks = calculator.calculate_option_greeks(
        spot_price=100,
        strike_price=105,
        risk_free_rate=0.05,
        volatility=0.25,
        time_to_maturity=1.0,
        option_type='call'
    )

    print(f"Option Price: ${option_greeks['price']:.2f}")
    print(f"Delta: {option_greeks['delta']:.4f}")
    print(f"Gamma: {option_greeks['gamma']:.4f}")
    print(f"Vega: {option_greeks['vega']:.4f}")
    print(f"Theta: {option_greeks['theta']:.4f} (per day)")
    print(f"Rho: {option_greeks['rho']:.4f}\n")

    # Export results
    os.makedirs('python/output', exist_ok=True)

    results = {
        'xirr': float(irr),
        'bond_metrics': {k: float(v) for k, v in bond_metrics.items()},
        'option_greeks': {k: float(v) for k, v in option_greeks.items()}
    }

    with open('python/output/quantlib_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("Results exported to: python/output/quantlib_results.json")


if __name__ == "__main__":
    run_quantlib_examples()
