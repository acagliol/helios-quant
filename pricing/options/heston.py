"""
Heston Stochastic Volatility Model

This module implements the Heston (1993) model for option pricing with stochastic volatility.

Mathematical Foundation:
    The Heston model assumes the following dynamics:

    dS_t = rS_t dt + √v_t S_t dW_1
    dv_t = κ(θ - v_t) dt + σ√v_t dW_2

    Where:
    - S_t: Asset price
    - v_t: Instantaneous variance
    - κ: Mean reversion speed
    - θ: Long-term variance
    - σ: Volatility of volatility
    - ρ: Correlation between W_1 and W_2

Pricing Method:
    Uses characteristic function approach with semi-analytical solution.

Reference:
    Heston, S. (1993). "A Closed-Form Solution for Options with Stochastic Volatility
    with Applications to Bond and Currency Options"
"""

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from typing import Literal, Tuple, Optional
import warnings


class HestonModel:
    """
    Heston model for pricing European options with stochastic volatility.

    The model captures volatility smile/skew observed in markets by allowing
    volatility to be stochastic and correlated with returns.

    Attributes:
        S0 (float): Current spot price
        v0 (float): Current variance
        kappa (float): Mean reversion speed
        theta (float): Long-term variance
        sigma (float): Volatility of volatility (vol of vol)
        rho (float): Correlation between asset and variance
        r (float): Risk-free rate
        T (float): Time to maturity
        K (float): Strike price

    Example:
        >>> heston = HestonModel(
        ...     S0=100, v0=0.04, kappa=2.0, theta=0.04,
        ...     sigma=0.3, rho=-0.7, r=0.05, T=1.0, K=100
        ... )
        >>> call_price = heston.price_call()
        >>> put_price = heston.price_put()
    """

    def __init__(
        self,
        S0: float,
        v0: float,
        kappa: float,
        theta: float,
        sigma: float,
        rho: float,
        r: float,
        T: float,
        K: float,
        q: float = 0.0
    ):
        """
        Initialize Heston model.

        Parameters:
            S0: Current spot price (> 0)
            v0: Current variance (> 0)
            kappa: Mean reversion speed (> 0)
            theta: Long-term variance (> 0)
            sigma: Volatility of volatility (> 0)
            rho: Correlation between asset and variance [-1, 1]
            r: Risk-free rate
            T: Time to maturity (> 0)
            K: Strike price (> 0)
            q: Dividend yield (default 0)

        Raises:
            ValueError: If parameters are invalid
        """
        # Validation
        if S0 <= 0:
            raise ValueError(f"Spot price S0 must be positive, got {S0}")
        if v0 <= 0:
            raise ValueError(f"Current variance v0 must be positive, got {v0}")
        if kappa <= 0:
            raise ValueError(f"Mean reversion kappa must be positive, got {kappa}")
        if theta <= 0:
            raise ValueError(f"Long-term variance theta must be positive, got {theta}")
        if sigma <= 0:
            raise ValueError(f"Vol of vol sigma must be positive, got {sigma}")
        if not -1 <= rho <= 1:
            raise ValueError(f"Correlation rho must be in [-1, 1], got {rho}")
        if T <= 0:
            raise ValueError(f"Time to maturity T must be positive, got {T}")
        if K <= 0:
            raise ValueError(f"Strike price K must be positive, got {K}")

        # Feller condition check (ensures variance stays positive)
        if 2 * kappa * theta < sigma ** 2:
            warnings.warn(
                f"Feller condition violated: 2κθ = {2*kappa*theta:.4f} < σ² = {sigma**2:.4f}. "
                "Variance can reach zero, which may cause numerical issues.",
                UserWarning
            )

        self.S0 = float(S0)
        self.v0 = float(v0)
        self.kappa = float(kappa)
        self.theta = float(theta)
        self.sigma = float(sigma)
        self.rho = float(rho)
        self.r = float(r)
        self.T = float(T)
        self.K = float(K)
        self.q = float(q)

    def _characteristic_function(self, u: complex, j: int) -> complex:
        """
        Heston characteristic function.

        Parameters:
            u: Complex argument
            j: 1 for first characteristic function, 2 for second

        Returns:
            Complex characteristic function value
        """
        if j == 1:
            b = self.kappa - self.rho * self.sigma
        else:
            b = self.kappa

        a = self.kappa * self.theta

        # Calculate d
        d = np.sqrt((self.rho * self.sigma * u * 1j - b) ** 2 +
                    self.sigma ** 2 * (u * 1j + u ** 2))

        # Calculate g
        g = (b - self.rho * self.sigma * u * 1j - d) / \
            (b - self.rho * self.sigma * u * 1j + d)

        # Calculate C and D
        C = self.r * u * 1j * self.T + \
            (a / self.sigma ** 2) * \
            ((b - self.rho * self.sigma * u * 1j - d) * self.T -
             2 * np.log((1 - g * np.exp(-d * self.T)) / (1 - g)))

        D = ((b - self.rho * self.sigma * u * 1j - d) / self.sigma ** 2) * \
            ((1 - np.exp(-d * self.T)) / (1 - g * np.exp(-d * self.T)))

        # Characteristic function
        cf = np.exp(C + D * self.v0 + 1j * u * np.log(self.S0))

        return cf

    def _P(self, j: int) -> float:
        """
        Calculate probability P_j using characteristic function.

        Parameters:
            j: 1 or 2 for respective probabilities

        Returns:
            Probability value
        """
        def integrand(u: float) -> float:
            """Integrand for probability calculation."""
            try:
                cf = self._characteristic_function(u, j)
                numerator = np.exp(-1j * u * np.log(self.K)) * cf
                denominator = 1j * u
                result = (numerator / denominator).real
                return result
            except:
                return 0.0

        # Numerical integration
        integral, _ = quad(integrand, 0, 100, limit=100)

        return 0.5 + (1 / np.pi) * integral

    def price_call(self) -> float:
        """
        Price European call option using Heston model.

        Returns:
            Call option price

        Formula:
            C = S₀P₁ - Ke^(-rT)P₂
            where P₁ and P₂ are probabilities from characteristic functions
        """
        P1 = self._P(1)
        P2 = self._P(2)

        call_price = self.S0 * np.exp(-self.q * self.T) * P1 - \
                     self.K * np.exp(-self.r * self.T) * P2

        return float(call_price)

    def price_put(self) -> float:
        """
        Price European put option using Heston model.

        Returns:
            Put option price

        Uses put-call parity:
            P = C - S₀e^(-qT) + Ke^(-rT)
        """
        call_price = self.price_call()
        put_price = call_price - self.S0 * np.exp(-self.q * self.T) + \
                    self.K * np.exp(-self.r * self.T)

        return float(put_price)

    def price(self, option_type: Literal['call', 'put'] = 'call') -> float:
        """
        Price option using Heston model.

        Parameters:
            option_type: 'call' or 'put'

        Returns:
            Option price
        """
        if option_type == 'call':
            return self.price_call()
        elif option_type == 'put':
            return self.price_put()
        else:
            raise ValueError(f"option_type must be 'call' or 'put', got {option_type}")

    def implied_volatility(
        self,
        option_type: Literal['call', 'put'] = 'call'
    ) -> float:
        """
        Calculate implied volatility from Heston model price.

        This is the Black-Scholes implied volatility that would produce
        the same price as the Heston model.

        Parameters:
            option_type: 'call' or 'put'

        Returns:
            Implied volatility (annualized)
        """
        from .black_scholes import BlackScholes

        heston_price = self.price(option_type)

        # Use Black-Scholes to find IV
        bs = BlackScholes(
            S=self.S0,
            K=self.K,
            T=self.T,
            r=self.r,
            sigma=np.sqrt(self.v0),  # initial guess
            q=self.q,
            option_type=option_type
        )

        try:
            iv = bs.implied_volatility(heston_price)
            return iv
        except ValueError:
            # If IV calculation fails, return sqrt of current variance
            return np.sqrt(self.v0)

    def __repr__(self) -> str:
        """String representation."""
        return (f"HestonModel(S0={self.S0:.2f}, v0={self.v0:.4f}, "
                f"κ={self.kappa:.2f}, θ={self.theta:.4f}, "
                f"σ={self.sigma:.2f}, ρ={self.rho:.2f}, "
                f"r={self.r:.4f}, T={self.T:.2f}, K={self.K:.2f})")


def build_volatility_surface(
    S0: float,
    r: float,
    heston_params: dict,
    strikes: np.ndarray,
    maturities: np.ndarray,
    q: float = 0.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build implied volatility surface using Heston model.

    Parameters:
        S0: Current spot price
        r: Risk-free rate
        heston_params: Dict with keys: v0, kappa, theta, sigma, rho
        strikes: Array of strike prices
        maturities: Array of maturities (in years)
        q: Dividend yield

    Returns:
        Tuple of (strike_mesh, maturity_mesh, iv_surface)
        where iv_surface[i, j] is IV for strikes[i] and maturities[j]

    Example:
        >>> strikes = np.linspace(80, 120, 10)
        >>> maturities = np.array([0.25, 0.5, 1.0, 2.0])
        >>> params = {'v0': 0.04, 'kappa': 2.0, 'theta': 0.04,
        ...           'sigma': 0.3, 'rho': -0.7}
        >>> K_mesh, T_mesh, iv_surf = build_volatility_surface(
        ...     S0=100, r=0.05, heston_params=params,
        ...     strikes=strikes, maturities=maturities
        ... )
    """
    # Create meshgrid
    K_mesh, T_mesh = np.meshgrid(strikes, maturities)
    iv_surface = np.zeros_like(K_mesh)

    # Calculate IV for each (K, T) pair
    for i, T in enumerate(maturities):
        for j, K in enumerate(strikes):
            heston = HestonModel(
                S0=S0,
                v0=heston_params['v0'],
                kappa=heston_params['kappa'],
                theta=heston_params['theta'],
                sigma=heston_params['sigma'],
                rho=heston_params['rho'],
                r=r,
                T=T,
                K=K,
                q=q
            )

            try:
                iv_surface[i, j] = heston.implied_volatility('call')
            except:
                # If calculation fails, use sqrt of long-term variance
                iv_surface[i, j] = np.sqrt(heston_params['theta'])

    return K_mesh, T_mesh, iv_surface
