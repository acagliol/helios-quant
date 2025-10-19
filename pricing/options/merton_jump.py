"""
Merton Jump-Diffusion Model

This module implements the Merton (1976) jump-diffusion model for option pricing.

Mathematical Foundation:
    The Merton model assumes asset price follows:

    dS_t = μS_t dt + σS_t dW_t + S_t dJ_t

    Where:
    - μ: Drift
    - σ: Diffusion volatility
    - W_t: Brownian motion
    - J_t: Jump process (compound Poisson)

    Jumps arrive with intensity λ and have log-normal size:
    ln(1 + k) ~ N(μ_j, σ_j²)

Pricing Method:
    Uses series expansion, pricing as weighted sum of Black-Scholes prices
    with adjusted parameters.

Reference:
    Merton, R. C. (1976). "Option Pricing When Underlying Stock Returns
    Are Discontinuous"
"""

import numpy as np
from scipy.stats import norm
from scipy.special import factorial
from typing import Literal
from .black_scholes import BlackScholes


class MertonJumpDiffusion:
    """
    Merton jump-diffusion model for option pricing.

    Extends Black-Scholes by adding jumps to capture sudden price movements
    (e.g., earnings announcements, market crashes).

    Attributes:
        S (float): Current spot price
        K (float): Strike price
        T (float): Time to maturity
        r (float): Risk-free rate
        sigma (float): Diffusion volatility
        lambda_jump (float): Jump intensity (jumps per year)
        mu_jump (float): Mean of log-jump size
        sigma_jump (float): Std deviation of log-jump size
        q (float): Dividend yield

    Example:
        >>> merton = MertonJumpDiffusion(
        ...     S=100, K=100, T=1.0, r=0.05, sigma=0.15,
        ...     lambda_jump=0.5, mu_jump=-0.05, sigma_jump=0.10
        ... )
        >>> call_price = merton.price('call')
        >>> put_price = merton.price('put')
    """

    def __init__(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        lambda_jump: float,
        mu_jump: float,
        sigma_jump: float,
        q: float = 0.0,
        max_jumps: int = 50
    ):
        """
        Initialize Merton jump-diffusion model.

        Parameters:
            S: Current spot price (> 0)
            K: Strike price (> 0)
            T: Time to maturity (> 0)
            r: Risk-free rate
            sigma: Diffusion volatility (> 0)
            lambda_jump: Jump intensity, jumps per year (>= 0)
            mu_jump: Mean of log-jump size
            sigma_jump: Std deviation of log-jump size (>= 0)
            q: Dividend yield (default 0)
            max_jumps: Maximum number of jumps to consider (default 50)

        Raises:
            ValueError: If parameters are invalid
        """
        # Validation
        if S <= 0:
            raise ValueError(f"Spot price S must be positive, got {S}")
        if K <= 0:
            raise ValueError(f"Strike price K must be positive, got {K}")
        if T <= 0:
            raise ValueError(f"Time to maturity T must be positive, got {T}")
        if sigma <= 0:
            raise ValueError(f"Volatility sigma must be positive, got {sigma}")
        if lambda_jump < 0:
            raise ValueError(f"Jump intensity lambda_jump must be non-negative, got {lambda_jump}")
        if sigma_jump < 0:
            raise ValueError(f"Jump volatility sigma_jump must be non-negative, got {sigma_jump}")

        self.S = float(S)
        self.K = float(K)
        self.T = float(T)
        self.r = float(r)
        self.sigma = float(sigma)
        self.lambda_jump = float(lambda_jump)
        self.mu_jump = float(mu_jump)
        self.sigma_jump = float(sigma_jump)
        self.q = float(q)
        self.max_jumps = int(max_jumps)

        # Calculate expected jump size for drift adjustment
        self.k = np.exp(mu_jump + 0.5 * sigma_jump ** 2) - 1

    def price(self, option_type: Literal['call', 'put'] = 'call') -> float:
        """
        Price option using Merton jump-diffusion model.

        Uses series expansion: prices as weighted sum of Black-Scholes prices
        where each term assumes exactly n jumps occur.

        Parameters:
            option_type: 'call' or 'put'

        Returns:
            Option price

        Formula:
            Price = Σ P(n jumps) * BS_price(adjusted parameters)
            where P(n jumps) follows Poisson distribution
        """
        total_price = 0.0

        # Calculate lambda prime (adjusted intensity)
        lambda_prime = self.lambda_jump * (1 + self.k)

        for n in range(self.max_jumps + 1):
            # Poisson probability of n jumps
            poisson_prob = (np.exp(-lambda_prime * self.T) *
                           (lambda_prime * self.T) ** n / factorial(n))

            # Adjusted parameters for n jumps
            sigma_n = np.sqrt(
                self.sigma ** 2 + n * self.sigma_jump ** 2 / self.T
            )

            r_n = (self.r - self.lambda_jump * self.k +
                   n * (self.mu_jump + 0.5 * self.sigma_jump ** 2) / self.T)

            # Price with Black-Scholes using adjusted parameters
            bs = BlackScholes(
                S=self.S,
                K=self.K,
                T=self.T,
                r=r_n,
                sigma=sigma_n,
                q=self.q,
                option_type=option_type
            )

            bs_price = bs.price()

            # Add weighted price
            total_price += poisson_prob * bs_price

            # Early termination if contribution becomes negligible
            if poisson_prob < 1e-10 and n > 10:
                break

        return float(total_price)

    def price_call(self) -> float:
        """Price call option."""
        return self.price('call')

    def price_put(self) -> float:
        """Price put option."""
        return self.price('put')

    def delta(self, option_type: Literal['call', 'put'] = 'call') -> float:
        """
        Calculate delta using finite difference.

        Parameters:
            option_type: 'call' or 'put'

        Returns:
            Delta (∂V/∂S)
        """
        dS = self.S * 0.01  # 1% bump

        # Create bumped models
        model_up = MertonJumpDiffusion(
            S=self.S + dS,
            K=self.K,
            T=self.T,
            r=self.r,
            sigma=self.sigma,
            lambda_jump=self.lambda_jump,
            mu_jump=self.mu_jump,
            sigma_jump=self.sigma_jump,
            q=self.q,
            max_jumps=self.max_jumps
        )

        model_down = MertonJumpDiffusion(
            S=self.S - dS,
            K=self.K,
            T=self.T,
            r=self.r,
            sigma=self.sigma,
            lambda_jump=self.lambda_jump,
            mu_jump=self.mu_jump,
            sigma_jump=self.sigma_jump,
            q=self.q,
            max_jumps=self.max_jumps
        )

        # Central difference
        delta = (model_up.price(option_type) - model_down.price(option_type)) / (2 * dS)

        return float(delta)

    def gamma(self, option_type: Literal['call', 'put'] = 'call') -> float:
        """
        Calculate gamma using finite difference.

        Parameters:
            option_type: 'call' or 'put'

        Returns:
            Gamma (∂²V/∂S²)
        """
        dS = self.S * 0.01

        model_up = MertonJumpDiffusion(
            S=self.S + dS, K=self.K, T=self.T, r=self.r, sigma=self.sigma,
            lambda_jump=self.lambda_jump, mu_jump=self.mu_jump,
            sigma_jump=self.sigma_jump, q=self.q, max_jumps=self.max_jumps
        )

        model_down = MertonJumpDiffusion(
            S=self.S - dS, K=self.K, T=self.T, r=self.r, sigma=self.sigma,
            lambda_jump=self.lambda_jump, mu_jump=self.mu_jump,
            sigma_jump=self.sigma_jump, q=self.q, max_jumps=self.max_jumps
        )

        price_center = self.price(option_type)

        gamma = (model_up.price(option_type) - 2 * price_center +
                model_down.price(option_type)) / (dS ** 2)

        return float(gamma)

    def vega(self, option_type: Literal['call', 'put'] = 'call') -> float:
        """
        Calculate vega (sensitivity to diffusion volatility).

        Parameters:
            option_type: 'call' or 'put'

        Returns:
            Vega (∂V/∂σ) per 1% change in volatility
        """
        dsigma = 0.01

        model_up = MertonJumpDiffusion(
            S=self.S, K=self.K, T=self.T, r=self.r, sigma=self.sigma + dsigma,
            lambda_jump=self.lambda_jump, mu_jump=self.mu_jump,
            sigma_jump=self.sigma_jump, q=self.q, max_jumps=self.max_jumps
        )

        vega = model_up.price(option_type) - self.price(option_type)

        return float(vega)

    def __repr__(self) -> str:
        """String representation."""
        return (f"MertonJumpDiffusion(S={self.S:.2f}, K={self.K:.2f}, T={self.T:.2f}, "
                f"r={self.r:.4f}, σ={self.sigma:.2f}, λ={self.lambda_jump:.2f}, "
                f"μ_j={self.mu_jump:.3f}, σ_j={self.sigma_jump:.2f})")
