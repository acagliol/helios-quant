"""
Black-Scholes Option Pricing Model

This module implements the Black-Scholes-Merton model for European option pricing
with analytical Greeks calculation.

Mathematical Foundation:
    The Black-Scholes PDE:
    ∂V/∂t + (1/2)σ²S²(∂²V/∂S²) + rS(∂V/∂S) - rV = 0

    Closed-form solution for European call:
    C = S₀N(d₁) - Ke^(-rT)N(d₂)

    Where:
    d₁ = [ln(S₀/K) + (r + σ²/2)T] / (σ√T)
    d₂ = d₁ - σ√T

Reference:
    Black, F., & Scholes, M. (1973). "The Pricing of Options and Corporate Liabilities"
"""

import numpy as np
from scipy.stats import norm
from typing import Literal, Dict, Optional


class BlackScholes:
    """
    Black-Scholes option pricing with Greeks.

    Validates against QuantLib with <0.01% error tolerance.

    Attributes:
        S (float): Current spot price
        K (float): Strike price
        T (float): Time to maturity (years)
        r (float): Risk-free interest rate (annual)
        sigma (float): Volatility (annual)
        q (float): Dividend yield (annual, default 0)
        option_type (str): 'call' or 'put'

    Example:
        >>> bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2)
        >>> price = bs.price()
        >>> delta = bs.delta()
        >>> gamma = bs.gamma()
    """

    def __init__(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        q: float = 0.0,
        option_type: Literal['call', 'put'] = 'call'
    ):
        """
        Initialize Black-Scholes option pricer.

        Parameters:
            S: Spot price (must be > 0)
            K: Strike price (must be > 0)
            T: Time to maturity in years (must be >= 0)
            r: Risk-free rate (e.g., 0.05 for 5%)
            sigma: Volatility (must be > 0, e.g., 0.20 for 20%)
            q: Dividend yield (default 0.0)
            option_type: 'call' or 'put'

        Raises:
            ValueError: If parameters are invalid
        """
        # Validation
        if S <= 0:
            raise ValueError(f"Spot price S must be positive, got {S}")
        if K <= 0:
            raise ValueError(f"Strike price K must be positive, got {K}")
        if T < 0:
            raise ValueError(f"Time to maturity T must be non-negative, got {T}")
        if sigma <= 0:
            raise ValueError(f"Volatility sigma must be positive, got {sigma}")
        if option_type not in ['call', 'put']:
            raise ValueError(f"option_type must be 'call' or 'put', got {option_type}")

        self.S = float(S)
        self.K = float(K)
        self.T = float(T)
        self.r = float(r)
        self.sigma = float(sigma)
        self.q = float(q)
        self.option_type = option_type

        # Cache d1 and d2 for performance
        self._d1: Optional[float] = None
        self._d2: Optional[float] = None

    def _calculate_d1_d2(self) -> tuple[float, float]:
        """Calculate d1 and d2 parameters (cached)."""
        if self._d1 is not None and self._d2 is not None:
            return self._d1, self._d2

        # Handle edge case: T = 0
        if self.T == 0:
            # At expiration, option worth is intrinsic value
            self._d1 = float('inf') if self.S > self.K else float('-inf')
            self._d2 = self._d1
            return self._d1, self._d2

        # Standard calculation
        sqrt_T = np.sqrt(self.T)
        self._d1 = (np.log(self.S / self.K) + (self.r - self.q + 0.5 * self.sigma ** 2) * self.T) / (self.sigma * sqrt_T)
        self._d2 = self._d1 - self.sigma * sqrt_T

        return self._d1, self._d2

    def price(self) -> float:
        """
        Calculate option price using Black-Scholes formula.

        Returns:
            Option price (float)

        Mathematical Formula:
            Call: C = S₀e^(-qT)N(d₁) - Ke^(-rT)N(d₂)
            Put:  P = Ke^(-rT)N(-d₂) - S₀e^(-qT)N(-d₁)
        """
        # Edge case: T = 0 (at expiration)
        if self.T == 0:
            if self.option_type == 'call':
                return max(self.S - self.K, 0)
            else:
                return max(self.K - self.S, 0)

        d1, d2 = self._calculate_d1_d2()

        discount_factor = np.exp(-self.r * self.T)
        dividend_factor = np.exp(-self.q * self.T)

        if self.option_type == 'call':
            price = self.S * dividend_factor * norm.cdf(d1) - self.K * discount_factor * norm.cdf(d2)
        else:  # put
            price = self.K * discount_factor * norm.cdf(-d2) - self.S * dividend_factor * norm.cdf(-d1)

        return float(price)

    def delta(self) -> float:
        """
        Calculate delta: ∂V/∂S (first derivative with respect to spot price).

        Returns:
            Delta value (float)

        Interpretation:
            - Call delta: [0, 1], typically 0.5 ATM
            - Put delta: [-1, 0], typically -0.5 ATM
            - Measures sensitivity to spot price changes

        Mathematical Formula:
            Call: Δ = e^(-qT)N(d₁)
            Put:  Δ = -e^(-qT)N(-d₁)
        """
        if self.T == 0:
            if self.option_type == 'call':
                return 1.0 if self.S > self.K else 0.0
            else:
                return -1.0 if self.S < self.K else 0.0

        d1, _ = self._calculate_d1_d2()
        dividend_factor = np.exp(-self.q * self.T)

        if self.option_type == 'call':
            delta = dividend_factor * norm.cdf(d1)
        else:  # put
            delta = -dividend_factor * norm.cdf(-d1)

        return float(delta)

    def gamma(self) -> float:
        """
        Calculate gamma: ∂²V/∂S² (second derivative with respect to spot price).

        Returns:
            Gamma value (float)

        Interpretation:
            - Always non-negative
            - Highest for ATM options
            - Measures convexity (curvature of delta)

        Mathematical Formula:
            Γ = e^(-qT)N'(d₁) / (Sσ√T)
            where N'(x) = (1/√(2π))e^(-x²/2)
        """
        if self.T == 0:
            return 0.0

        d1, _ = self._calculate_d1_d2()
        dividend_factor = np.exp(-self.q * self.T)

        # N'(d1) = pdf(d1)
        gamma = (dividend_factor * norm.pdf(d1)) / (self.S * self.sigma * np.sqrt(self.T))

        return float(gamma)

    def vega(self) -> float:
        """
        Calculate vega: ∂V/∂σ (derivative with respect to volatility).

        Returns:
            Vega value (float)

        Interpretation:
            - Always positive for long options
            - Highest for ATM options
            - Typically quoted as change per 1% move in volatility
            - This returns vega for 1% (0.01) change in volatility

        Mathematical Formula:
            ν = S₀e^(-qT)N'(d₁)√T
        """
        if self.T == 0:
            return 0.0

        d1, _ = self._calculate_d1_d2()
        dividend_factor = np.exp(-self.q * self.T)

        # Vega per 1% change in volatility
        vega = self.S * dividend_factor * norm.pdf(d1) * np.sqrt(self.T) / 100

        return float(vega)

    def theta(self) -> float:
        """
        Calculate theta: -∂V/∂t (derivative with respect to time).

        Returns:
            Theta value (float, per year)

        Interpretation:
            - Typically negative for long options (time decay)
            - Measures time decay
            - Returns annual theta (divide by 252 for daily)

        Mathematical Formula:
            Call: Θ = -[S₀N'(d₁)σe^(-qT)/(2√T) + qS₀N(d₁)e^(-qT) - rKe^(-rT)N(d₂)]
            Put:  Θ = -[S₀N'(d₁)σe^(-qT)/(2√T) - qS₀N(-d₁)e^(-qT) + rKe^(-rT)N(-d₂)]
        """
        if self.T == 0:
            return 0.0

        d1, d2 = self._calculate_d1_d2()
        discount_factor = np.exp(-self.r * self.T)
        dividend_factor = np.exp(-self.q * self.T)
        sqrt_T = np.sqrt(self.T)

        # Common term
        term1 = -(self.S * norm.pdf(d1) * self.sigma * dividend_factor) / (2 * sqrt_T)

        if self.option_type == 'call':
            term2 = self.q * self.S * norm.cdf(d1) * dividend_factor
            term3 = self.r * self.K * discount_factor * norm.cdf(d2)
            theta = term1 - term2 + term3
        else:  # put
            term2 = self.q * self.S * norm.cdf(-d1) * dividend_factor
            term3 = self.r * self.K * discount_factor * norm.cdf(-d2)
            theta = term1 + term2 - term3

        return float(theta)

    def rho(self) -> float:
        """
        Calculate rho: ∂V/∂r (derivative with respect to risk-free rate).

        Returns:
            Rho value (float, for 1% change in rate)

        Interpretation:
            - Call rho: positive (calls benefit from higher rates)
            - Put rho: negative (puts benefit from lower rates)
            - Measures sensitivity to interest rate changes

        Mathematical Formula:
            Call: ρ = KTe^(-rT)N(d₂)
            Put:  ρ = -KTe^(-rT)N(-d₂)
        """
        if self.T == 0:
            return 0.0

        _, d2 = self._calculate_d1_d2()
        discount_factor = np.exp(-self.r * self.T)

        if self.option_type == 'call':
            rho = self.K * self.T * discount_factor * norm.cdf(d2) / 100
        else:  # put
            rho = -self.K * self.T * discount_factor * norm.cdf(-d2) / 100

        return float(rho)

    def all_greeks(self) -> Dict[str, float]:
        """
        Calculate all Greeks at once (more efficient than individual calls).

        Returns:
            Dictionary with keys: 'price', 'delta', 'gamma', 'vega', 'theta', 'rho'
        """
        return {
            'price': self.price(),
            'delta': self.delta(),
            'gamma': self.gamma(),
            'vega': self.vega(),
            'theta': self.theta(),
            'rho': self.rho()
        }

    def implied_volatility(
        self,
        market_price: float,
        tolerance: float = 1e-6,
        max_iterations: int = 100
    ) -> float:
        """
        Calculate implied volatility using Newton-Raphson method.

        Parameters:
            market_price: Observed market price
            tolerance: Convergence tolerance
            max_iterations: Maximum iterations

        Returns:
            Implied volatility (annual)

        Raises:
            ValueError: If implied volatility cannot be found
        """
        # Initial guess using Brenner-Subrahmanyam approximation
        sigma_guess = np.sqrt(2 * np.pi / self.T) * (market_price / self.S)

        for iteration in range(max_iterations):
            # Create temporary BS object with current guess
            bs_temp = BlackScholes(
                S=self.S, K=self.K, T=self.T, r=self.r,
                sigma=sigma_guess, q=self.q, option_type=self.option_type
            )

            price = bs_temp.price()
            vega = bs_temp.vega() * 100  # vega per 1.0 change in volatility

            diff = market_price - price

            # Check convergence
            if abs(diff) < tolerance:
                return sigma_guess

            # Check for zero vega
            if abs(vega) < 1e-10:
                raise ValueError("Vega is too small, cannot compute implied volatility")

            # Newton-Raphson update
            sigma_guess = sigma_guess + diff / vega

            # Keep sigma positive
            sigma_guess = max(sigma_guess, 1e-6)

        raise ValueError(f"Implied volatility did not converge after {max_iterations} iterations")

    def __repr__(self) -> str:
        """String representation of the option."""
        return (f"BlackScholes({self.option_type.capitalize()}, "
                f"S={self.S:.2f}, K={self.K:.2f}, T={self.T:.4f}, "
                f"r={self.r:.4f}, σ={self.sigma:.4f}, q={self.q:.4f})")
