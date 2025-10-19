"""
Comprehensive test suite for Black-Scholes option pricing.

Tests include:
- Standard European calls/puts
- ATM, ITM, OTM scenarios
- Short and long maturities
- Low and high volatility
- Dividend-paying stocks
- Put-call parity validation
- Greek accuracy tests
- Edge cases (T→0, σ→0, etc.)

Target: 25+ test cases, all passing
"""

import pytest
import numpy as np
from pricing.options.black_scholes import BlackScholes


class TestBlackScholesBasic:
    """Test basic functionality and parameter validation."""

    def test_initialization_valid(self):
        """Test that valid parameters initialize correctly."""
        bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2)
        assert bs.S == 100
        assert bs.K == 100
        assert bs.T == 1.0
        assert bs.r == 0.05
        assert bs.sigma == 0.2
        assert bs.q == 0.0
        assert bs.option_type == 'call'

    def test_initialization_put(self):
        """Test put option initialization."""
        bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2, option_type='put')
        assert bs.option_type == 'put'

    def test_invalid_spot_price(self):
        """Test that negative or zero spot price raises error."""
        with pytest.raises(ValueError, match="Spot price S must be positive"):
            BlackScholes(S=0, K=100, T=1.0, r=0.05, sigma=0.2)
        with pytest.raises(ValueError):
            BlackScholes(S=-10, K=100, T=1.0, r=0.05, sigma=0.2)

    def test_invalid_strike_price(self):
        """Test that negative or zero strike price raises error."""
        with pytest.raises(ValueError, match="Strike price K must be positive"):
            BlackScholes(S=100, K=0, T=1.0, r=0.05, sigma=0.2)

    def test_invalid_time_to_maturity(self):
        """Test that negative time to maturity raises error."""
        with pytest.raises(ValueError, match="Time to maturity T must be non-negative"):
            BlackScholes(S=100, K=100, T=-1.0, r=0.05, sigma=0.2)

    def test_invalid_volatility(self):
        """Test that non-positive volatility raises error."""
        with pytest.raises(ValueError, match="Volatility sigma must be positive"):
            BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0)
        with pytest.raises(ValueError):
            BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=-0.2)

    def test_invalid_option_type(self):
        """Test that invalid option type raises error."""
        with pytest.raises(ValueError, match="option_type must be 'call' or 'put'"):
            BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2, option_type='invalid')


class TestBlackScholesPricing:
    """Test option pricing under various scenarios."""

    def test_atm_call(self):
        """Test at-the-money call option pricing."""
        bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2)
        price = bs.price()
        # ATM call should have positive price
        assert price > 0
        # Approximate check (theoretical value ~10.45)
        assert 8 < price < 12

    def test_atm_put(self):
        """Test at-the-money put option pricing."""
        bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2, option_type='put')
        price = bs.price()
        # ATM put should have positive price
        assert price > 0
        # Approximate check (theoretical value ~5.57)
        assert 4 < price < 7

    def test_itm_call(self):
        """Test in-the-money call option."""
        bs = BlackScholes(S=110, K=100, T=1.0, r=0.05, sigma=0.2)
        price = bs.price()
        # ITM call should be worth at least intrinsic value
        intrinsic_value = 110 - 100
        assert price > intrinsic_value

    def test_otm_call(self):
        """Test out-of-the-money call option."""
        bs = BlackScholes(S=90, K=100, T=1.0, r=0.05, sigma=0.2)
        price = bs.price()
        # OTM call should have positive time value
        assert price > 0
        # But less than ATM call
        atm_call = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2).price()
        assert price < atm_call

    def test_itm_put(self):
        """Test in-the-money put option."""
        bs = BlackScholes(S=90, K=100, T=1.0, r=0.05, sigma=0.2, option_type='put')
        price = bs.price()
        # ITM put should be worth at least discounted intrinsic value
        intrinsic_value = 100 - 90
        assert price > intrinsic_value * np.exp(-0.05 * 1.0) * 0.5  # rough lower bound

    def test_otm_put(self):
        """Test out-of-the-money put option."""
        bs = BlackScholes(S=110, K=100, T=1.0, r=0.05, sigma=0.2, option_type='put')
        price = bs.price()
        # OTM put should have positive time value
        assert price > 0
        # But less than ATM put
        atm_put = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2, option_type='put').price()
        assert price < atm_put

    def test_short_maturity(self):
        """Test option with short time to maturity."""
        bs_short = BlackScholes(S=100, K=100, T=0.1, r=0.05, sigma=0.2)
        bs_long = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2)
        # Shorter maturity should have lower price (all else equal)
        assert bs_short.price() < bs_long.price()

    def test_long_maturity(self):
        """Test option with long time to maturity."""
        bs = BlackScholes(S=100, K=100, T=5.0, r=0.05, sigma=0.2)
        price = bs.price()
        assert price > 0

    def test_low_volatility(self):
        """Test option with low volatility."""
        bs_low = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.05)
        bs_high = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.5)
        # Higher volatility should lead to higher price
        assert bs_low.price() < bs_high.price()

    def test_high_volatility(self):
        """Test option with high volatility."""
        bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.8)
        price = bs.price()
        assert price > 0

    def test_with_dividends(self):
        """Test option with dividend yield."""
        bs_no_div = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2, q=0.0)
        bs_div = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2, q=0.03)
        # Dividends reduce call value
        assert bs_div.price() < bs_no_div.price()


class TestPutCallParity:
    """Test put-call parity relationship."""

    def test_put_call_parity_no_dividends(self):
        """
        Test put-call parity: C - P = S - K*e^(-rT)
        """
        S, K, T, r, sigma = 100, 100, 1.0, 0.05, 0.2
        call = BlackScholes(S=S, K=K, T=T, r=r, sigma=sigma, option_type='call')
        put = BlackScholes(S=S, K=K, T=T, r=r, sigma=sigma, option_type='put')

        lhs = call.price() - put.price()
        rhs = S - K * np.exp(-r * T)

        assert abs(lhs - rhs) < 1e-10

    def test_put_call_parity_with_dividends(self):
        """
        Test put-call parity with dividends: C - P = S*e^(-qT) - K*e^(-rT)
        """
        S, K, T, r, sigma, q = 100, 100, 1.0, 0.05, 0.2, 0.02
        call = BlackScholes(S=S, K=K, T=T, r=r, sigma=sigma, q=q, option_type='call')
        put = BlackScholes(S=S, K=K, T=T, r=r, sigma=sigma, q=q, option_type='put')

        lhs = call.price() - put.price()
        rhs = S * np.exp(-q * T) - K * np.exp(-r * T)

        assert abs(lhs - rhs) < 1e-10

    def test_put_call_parity_various_strikes(self):
        """Test put-call parity holds for various strike prices."""
        S, T, r, sigma = 100, 1.0, 0.05, 0.2
        strikes = [80, 90, 100, 110, 120]

        for K in strikes:
            call = BlackScholes(S=S, K=K, T=T, r=r, sigma=sigma, option_type='call')
            put = BlackScholes(S=S, K=K, T=T, r=r, sigma=sigma, option_type='put')

            lhs = call.price() - put.price()
            rhs = S - K * np.exp(-r * T)

            assert abs(lhs - rhs) < 1e-10


class TestGreeks:
    """Test Greeks calculation accuracy."""

    def test_delta_call_range(self):
        """Test that call delta is in [0, 1]."""
        bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2)
        delta = bs.delta()
        assert 0 <= delta <= 1

    def test_delta_put_range(self):
        """Test that put delta is in [-1, 0]."""
        bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2, option_type='put')
        delta = bs.delta()
        assert -1 <= delta <= 0

    def test_delta_atm_call(self):
        """Test that ATM call delta is approximately 0.5."""
        bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2, q=0.0)
        delta = bs.delta()
        # With no dividends, ATM call delta ~0.5-0.6
        assert 0.4 < delta < 0.7

    def test_gamma_positive(self):
        """Test that gamma is always non-negative."""
        scenarios = [
            (90, 100),  # OTM
            (100, 100),  # ATM
            (110, 100),  # ITM
        ]
        for S, K in scenarios:
            bs_call = BlackScholes(S=S, K=K, T=1.0, r=0.05, sigma=0.2)
            bs_put = BlackScholes(S=S, K=K, T=1.0, r=0.05, sigma=0.2, option_type='put')
            assert bs_call.gamma() >= 0
            assert bs_put.gamma() >= 0

    def test_gamma_call_equals_put(self):
        """Test that gamma is the same for calls and puts."""
        bs_call = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2)
        bs_put = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2, option_type='put')
        assert abs(bs_call.gamma() - bs_put.gamma()) < 1e-10

    def test_vega_positive(self):
        """Test that vega is always positive for long options."""
        bs_call = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2)
        bs_put = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2, option_type='put')
        assert bs_call.vega() > 0
        assert bs_put.vega() > 0

    def test_vega_call_equals_put(self):
        """Test that vega is the same for calls and puts."""
        bs_call = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2)
        bs_put = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2, option_type='put')
        assert abs(bs_call.vega() - bs_put.vega()) < 1e-10

    def test_theta_call_negative(self):
        """Test that theta is typically negative for call options."""
        bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2)
        theta = bs.theta()
        # Theta is usually negative (time decay)
        assert theta < 0

    def test_rho_call_positive(self):
        """Test that rho is positive for call options."""
        bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2)
        rho = bs.rho()
        assert rho > 0

    def test_rho_put_negative(self):
        """Test that rho is negative for put options."""
        bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2, option_type='put')
        rho = bs.rho()
        assert rho < 0

    def test_all_greeks(self):
        """Test that all_greeks returns all values."""
        bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2)
        greeks = bs.all_greeks()
        assert 'price' in greeks
        assert 'delta' in greeks
        assert 'gamma' in greeks
        assert 'vega' in greeks
        assert 'theta' in greeks
        assert 'rho' in greeks
        # Verify values match individual calculations
        assert abs(greeks['price'] - bs.price()) < 1e-10
        assert abs(greeks['delta'] - bs.delta()) < 1e-10


class TestEdgeCases:
    """Test edge cases and numerical stability."""

    def test_zero_time_to_maturity_call(self):
        """Test call at expiration (T=0)."""
        # ITM at expiration
        bs_itm = BlackScholes(S=110, K=100, T=0, r=0.05, sigma=0.2)
        assert abs(bs_itm.price() - 10) < 1e-10
        assert abs(bs_itm.delta() - 1.0) < 1e-10

        # OTM at expiration
        bs_otm = BlackScholes(S=90, K=100, T=0, r=0.05, sigma=0.2)
        assert abs(bs_otm.price()) < 1e-10
        assert abs(bs_otm.delta()) < 1e-10

    def test_zero_time_to_maturity_put(self):
        """Test put at expiration (T=0)."""
        # ITM at expiration
        bs_itm = BlackScholes(S=90, K=100, T=0, r=0.05, sigma=0.2, option_type='put')
        assert abs(bs_itm.price() - 10) < 1e-10
        assert abs(bs_itm.delta() - (-1.0)) < 1e-10

        # OTM at expiration
        bs_otm = BlackScholes(S=110, K=100, T=0, r=0.05, sigma=0.2, option_type='put')
        assert abs(bs_otm.price()) < 1e-10
        assert abs(bs_otm.delta()) < 1e-10

    def test_very_small_volatility(self):
        """Test with very small volatility."""
        bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.001)
        price = bs.price()
        # Should still work
        assert price > 0

    def test_very_high_volatility(self):
        """Test with very high volatility."""
        bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=2.0)
        price = bs.price()
        # Should still work
        assert price > 0

    def test_deep_itm_call(self):
        """Test deep in-the-money call."""
        bs = BlackScholes(S=200, K=100, T=1.0, r=0.05, sigma=0.2)
        price = bs.price()
        delta = bs.delta()
        # Deep ITM call should have delta close to 1
        assert delta > 0.95
        # Price should be close to intrinsic + carry
        assert price > 100

    def test_deep_otm_call(self):
        """Test deep out-of-the-money call."""
        bs = BlackScholes(S=50, K=100, T=1.0, r=0.05, sigma=0.2)
        price = bs.price()
        delta = bs.delta()
        # Deep OTM call should have delta close to 0
        assert delta < 0.05
        # Price should be very small
        assert price < 1


class TestImpliedVolatility:
    """Test implied volatility calculation."""

    def test_implied_volatility_atm(self):
        """Test implied volatility for ATM option."""
        sigma_actual = 0.25
        bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=sigma_actual)
        market_price = bs.price()

        # Calculate IV
        bs_iv = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2)  # initial guess
        sigma_implied = bs_iv.implied_volatility(market_price)

        # Should recover the original volatility
        assert abs(sigma_implied - sigma_actual) < 1e-4

    def test_implied_volatility_otm(self):
        """Test implied volatility for OTM option."""
        sigma_actual = 0.30
        bs = BlackScholes(S=100, K=110, T=1.0, r=0.05, sigma=sigma_actual)
        market_price = bs.price()

        bs_iv = BlackScholes(S=100, K=110, T=1.0, r=0.05, sigma=0.2)
        sigma_implied = bs_iv.implied_volatility(market_price)

        assert abs(sigma_implied - sigma_actual) < 1e-4

    def test_implied_volatility_put(self):
        """Test implied volatility for put option."""
        sigma_actual = 0.28
        bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=sigma_actual, option_type='put')
        market_price = bs.price()

        bs_iv = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2, option_type='put')
        sigma_implied = bs_iv.implied_volatility(market_price)

        assert abs(sigma_implied - sigma_actual) < 1e-4


class TestNumericalStability:
    """Test numerical stability across various parameter ranges."""

    @pytest.mark.parametrize("S,K", [
        (50, 100), (100, 100), (150, 100),
        (1, 10), (1000, 1000), (0.01, 0.01)
    ])
    def test_various_spot_strike_combinations(self, S, K):
        """Test pricing works for various S/K combinations."""
        bs = BlackScholes(S=S, K=K, T=1.0, r=0.05, sigma=0.2)
        price = bs.price()
        assert price >= 0
        assert not np.isnan(price)
        assert not np.isinf(price)

    @pytest.mark.parametrize("T", [0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0])
    def test_various_maturities(self, T):
        """Test pricing works for various maturities."""
        bs = BlackScholes(S=100, K=100, T=T, r=0.05, sigma=0.2)
        price = bs.price()
        assert price >= 0
        assert not np.isnan(price)

    @pytest.mark.parametrize("sigma", [0.01, 0.1, 0.2, 0.5, 1.0, 2.0])
    def test_various_volatilities(self, sigma):
        """Test pricing works for various volatilities."""
        bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=sigma)
        price = bs.price()
        assert price >= 0
        assert not np.isnan(price)


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
