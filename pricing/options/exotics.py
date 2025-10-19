"""
Exotic Options Pricing

This module implements pricing for exotic options that don't have simple closed-form
solutions and require Monte Carlo simulation or other numerical methods.

Implemented Options:
- Asian Options (arithmetic and geometric average)
- Barrier Options (knock-in, knock-out)
- Lookback Options (floating and fixed strike)
- Digital (Binary) Options

Pricing Method:
    Primarily uses Monte Carlo simulation with variance reduction techniques.
"""

import numpy as np
from typing import Literal, Optional
from dataclasses import dataclass


@dataclass
class SimulationParams:
    """Parameters for Monte Carlo simulation."""
    n_paths: int = 100000
    n_steps: int = 252
    antithetic: bool = True
    seed: Optional[int] = None


class AsianOption:
    """
    Asian option pricing (arithmetic and geometric average).

    Asian options have payoffs that depend on the average price of the
    underlying asset over the option's life, making them less susceptible
    to price manipulation.

    Attributes:
        S (float): Current spot price
        K (float): Strike price
        T (float): Time to maturity
        r (float): Risk-free rate
        sigma (float): Volatility
        option_type (str): 'call' or 'put'
        average_type (str): 'arithmetic' or 'geometric'
        q (float): Dividend yield

    Example:
        >>> asian = AsianOption(
        ...     S=100, K=100, T=1.0, r=0.05, sigma=0.2,
        ...     option_type='call', average_type='arithmetic'
        ... )
        >>> price = asian.price()
    """

    def __init__(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: Literal['call', 'put'] = 'call',
        average_type: Literal['arithmetic', 'geometric'] = 'arithmetic',
        q: float = 0.0
    ):
        """
        Initialize Asian option.

        Parameters:
            S: Current spot price
            K: Strike price
            T: Time to maturity
            r: Risk-free rate
            sigma: Volatility
            option_type: 'call' or 'put'
            average_type: 'arithmetic' or 'geometric'
            q: Dividend yield
        """
        self.S = float(S)
        self.K = float(K)
        self.T = float(T)
        self.r = float(r)
        self.sigma = float(sigma)
        self.option_type = option_type
        self.average_type = average_type
        self.q = float(q)

    def price(self, sim_params: Optional[SimulationParams] = None) -> float:
        """
        Price Asian option using Monte Carlo simulation.

        Parameters:
            sim_params: Simulation parameters (default: 100k paths, antithetic)

        Returns:
            Option price
        """
        if sim_params is None:
            sim_params = SimulationParams()

        if sim_params.seed is not None:
            np.random.seed(sim_params.seed)

        # Time step
        dt = self.T / sim_params.n_steps

        # Number of paths (doubled if antithetic)
        n_paths = sim_params.n_paths
        if sim_params.antithetic:
            n_paths = n_paths // 2

        # Generate random numbers
        Z = np.random.standard_normal((n_paths, sim_params.n_steps))

        if sim_params.antithetic:
            Z = np.concatenate([Z, -Z], axis=0)

        # Simulate paths
        S_paths = np.zeros((Z.shape[0], sim_params.n_steps + 1))
        S_paths[:, 0] = self.S

        for t in range(1, sim_params.n_steps + 1):
            S_paths[:, t] = S_paths[:, t-1] * np.exp(
                (self.r - self.q - 0.5 * self.sigma**2) * dt +
                self.sigma * np.sqrt(dt) * Z[:, t-1]
            )

        # Calculate averages
        if self.average_type == 'arithmetic':
            averages = np.mean(S_paths[:, 1:], axis=1)
        else:  # geometric
            averages = np.exp(np.mean(np.log(S_paths[:, 1:]), axis=1))

        # Calculate payoffs
        if self.option_type == 'call':
            payoffs = np.maximum(averages - self.K, 0)
        else:  # put
            payoffs = np.maximum(self.K - averages, 0)

        # Discount and average
        price = np.exp(-self.r * self.T) * np.mean(payoffs)

        return float(price)

    def __repr__(self) -> str:
        return (f"AsianOption({self.average_type.capitalize()}, {self.option_type.capitalize()}, "
                f"S={self.S:.2f}, K={self.K:.2f}, T={self.T:.2f})")


class BarrierOption:
    """
    Barrier option pricing (knock-in and knock-out).

    Barrier options activate (knock-in) or deactivate (knock-out) when the
    underlying price hits a specified barrier level.

    Attributes:
        S (float): Current spot price
        K (float): Strike price
        T (float): Time to maturity
        r (float): Risk-free rate
        sigma (float): Volatility
        barrier (float): Barrier level
        barrier_type (str): 'down-and-out', 'down-and-in', 'up-and-out', 'up-and-in'
        option_type (str): 'call' or 'put'
        q (float): Dividend yield

    Example:
        >>> barrier = BarrierOption(
        ...     S=100, K=100, T=1.0, r=0.05, sigma=0.2,
        ...     barrier=120, barrier_type='up-and-out', option_type='call'
        ... )
        >>> price = barrier.price()
    """

    def __init__(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        barrier: float,
        barrier_type: Literal['down-and-out', 'down-and-in', 'up-and-out', 'up-and-in'],
        option_type: Literal['call', 'put'] = 'call',
        q: float = 0.0
    ):
        """Initialize barrier option."""
        self.S = float(S)
        self.K = float(K)
        self.T = float(T)
        self.r = float(r)
        self.sigma = float(sigma)
        self.barrier = float(barrier)
        self.barrier_type = barrier_type
        self.option_type = option_type
        self.q = float(q)

        # Validate barrier level
        if 'up' in barrier_type and barrier <= S:
            raise ValueError(f"Up barrier must be > spot price: {barrier} <= {S}")
        if 'down' in barrier_type and barrier >= S:
            raise ValueError(f"Down barrier must be < spot price: {barrier} >= {S}")

    def price(self, sim_params: Optional[SimulationParams] = None) -> float:
        """
        Price barrier option using Monte Carlo simulation.

        Parameters:
            sim_params: Simulation parameters

        Returns:
            Option price
        """
        if sim_params is None:
            sim_params = SimulationParams()

        if sim_params.seed is not None:
            np.random.seed(sim_params.seed)

        dt = self.T / sim_params.n_steps

        n_paths = sim_params.n_paths
        if sim_params.antithetic:
            n_paths = n_paths // 2

        Z = np.random.standard_normal((n_paths, sim_params.n_steps))

        if sim_params.antithetic:
            Z = np.concatenate([Z, -Z], axis=0)

        # Simulate paths
        S_paths = np.zeros((Z.shape[0], sim_params.n_steps + 1))
        S_paths[:, 0] = self.S

        for t in range(1, sim_params.n_steps + 1):
            S_paths[:, t] = S_paths[:, t-1] * np.exp(
                (self.r - self.q - 0.5 * self.sigma**2) * dt +
                self.sigma * np.sqrt(dt) * Z[:, t-1]
            )

        # Check barrier hits
        if 'up' in self.barrier_type:
            barrier_hit = np.max(S_paths, axis=1) >= self.barrier
        else:  # down
            barrier_hit = np.min(S_paths, axis=1) <= self.barrier

        # Calculate payoffs
        final_prices = S_paths[:, -1]

        if self.option_type == 'call':
            intrinsic = np.maximum(final_prices - self.K, 0)
        else:  # put
            intrinsic = np.maximum(self.K - final_prices, 0)

        # Apply barrier logic
        if 'out' in self.barrier_type:
            # Knock-out: payoff only if barrier NOT hit
            payoffs = intrinsic * (~barrier_hit)
        else:  # knock-in
            # Knock-in: payoff only if barrier WAS hit
            payoffs = intrinsic * barrier_hit

        # Discount and average
        price = np.exp(-self.r * self.T) * np.mean(payoffs)

        return float(price)

    def __repr__(self) -> str:
        return (f"BarrierOption({self.barrier_type}, {self.option_type}, "
                f"S={self.S:.2f}, K={self.K:.2f}, B={self.barrier:.2f})")


class LookbackOption:
    """
    Lookback option pricing (floating and fixed strike).

    Lookback options have payoffs that depend on the maximum or minimum
    price achieved during the option's life.

    Types:
    - Floating strike call: payoff = S_T - S_min
    - Floating strike put: payoff = S_max - S_T
    - Fixed strike call: payoff = max(S_max - K, 0)
    - Fixed strike put: payoff = max(K - S_min, 0)

    Attributes:
        S (float): Current spot price
        K (float): Strike price (for fixed strike) or None (for floating)
        T (float): Time to maturity
        r (float): Risk-free rate
        sigma (float): Volatility
        option_type (str): 'call' or 'put'
        strike_type (str): 'fixed' or 'floating'
        q (float): Dividend yield

    Example:
        >>> lookback = LookbackOption(
        ...     S=100, K=None, T=1.0, r=0.05, sigma=0.2,
        ...     option_type='call', strike_type='floating'
        ... )
        >>> price = lookback.price()
    """

    def __init__(
        self,
        S: float,
        K: Optional[float],
        T: float,
        r: float,
        sigma: float,
        option_type: Literal['call', 'put'] = 'call',
        strike_type: Literal['fixed', 'floating'] = 'floating',
        q: float = 0.0
    ):
        """Initialize lookback option."""
        self.S = float(S)
        self.K = float(K) if K is not None else None
        self.T = float(T)
        self.r = float(r)
        self.sigma = float(sigma)
        self.option_type = option_type
        self.strike_type = strike_type
        self.q = float(q)

        if strike_type == 'fixed' and K is None:
            raise ValueError("Fixed strike lookback requires strike K")

    def price(self, sim_params: Optional[SimulationParams] = None) -> float:
        """
        Price lookback option using Monte Carlo simulation.

        Parameters:
            sim_params: Simulation parameters

        Returns:
            Option price
        """
        if sim_params is None:
            sim_params = SimulationParams()

        if sim_params.seed is not None:
            np.random.seed(sim_params.seed)

        dt = self.T / sim_params.n_steps

        n_paths = sim_params.n_paths
        if sim_params.antithetic:
            n_paths = n_paths // 2

        Z = np.random.standard_normal((n_paths, sim_params.n_steps))

        if sim_params.antithetic:
            Z = np.concatenate([Z, -Z], axis=0)

        # Simulate paths
        S_paths = np.zeros((Z.shape[0], sim_params.n_steps + 1))
        S_paths[:, 0] = self.S

        for t in range(1, sim_params.n_steps + 1):
            S_paths[:, t] = S_paths[:, t-1] * np.exp(
                (self.r - self.q - 0.5 * self.sigma**2) * dt +
                self.sigma * np.sqrt(dt) * Z[:, t-1]
            )

        # Calculate extremes
        S_max = np.max(S_paths, axis=1)
        S_min = np.min(S_paths, axis=1)
        S_T = S_paths[:, -1]

        # Calculate payoffs based on type
        if self.strike_type == 'floating':
            if self.option_type == 'call':
                # Floating strike call: S_T - S_min
                payoffs = S_T - S_min
            else:  # put
                # Floating strike put: S_max - S_T
                payoffs = S_max - S_T
        else:  # fixed strike
            if self.option_type == 'call':
                # Fixed strike call: max(S_max - K, 0)
                payoffs = np.maximum(S_max - self.K, 0)
            else:  # put
                # Fixed strike put: max(K - S_min, 0)
                payoffs = np.maximum(self.K - S_min, 0)

        # Discount and average
        price = np.exp(-self.r * self.T) * np.mean(payoffs)

        return float(price)

    def __repr__(self) -> str:
        strike_str = f"K={self.K:.2f}" if self.K is not None else "Floating"
        return (f"LookbackOption({self.strike_type.capitalize()}, {self.option_type}, "
                f"S={self.S:.2f}, {strike_str})")


class DigitalOption:
    """
    Digital (Binary) option pricing.

    Digital options pay a fixed amount if the option is in-the-money at expiration,
    otherwise nothing.

    Types:
    - Cash-or-nothing: Pays fixed cash amount Q if ITM
    - Asset-or-nothing: Pays asset value S_T if ITM

    Attributes:
        S (float): Current spot price
        K (float): Strike price
        T (float): Time to maturity
        r (float): Risk-free rate
        sigma (float): Volatility
        option_type (str): 'call' or 'put'
        payout_type (str): 'cash' or 'asset'
        payout_amount (float): Fixed payout for cash-or-nothing
        q (float): Dividend yield

    Example:
        >>> digital = DigitalOption(
        ...     S=100, K=100, T=1.0, r=0.05, sigma=0.2,
        ...     option_type='call', payout_type='cash', payout_amount=10
        ... )
        >>> price = digital.price()
    """

    def __init__(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: Literal['call', 'put'] = 'call',
        payout_type: Literal['cash', 'asset'] = 'cash',
        payout_amount: float = 1.0,
        q: float = 0.0
    ):
        """Initialize digital option."""
        self.S = float(S)
        self.K = float(K)
        self.T = float(T)
        self.r = float(r)
        self.sigma = float(sigma)
        self.option_type = option_type
        self.payout_type = payout_type
        self.payout_amount = float(payout_amount)
        self.q = float(q)

    def price(self) -> float:
        """
        Price digital option using closed-form Black-Scholes formula.

        Returns:
            Option price
        """
        from scipy.stats import norm

        # Calculate d1 and d2
        d1 = (np.log(self.S / self.K) + (self.r - self.q + 0.5 * self.sigma**2) * self.T) / \
             (self.sigma * np.sqrt(self.T))
        d2 = d1 - self.sigma * np.sqrt(self.T)

        if self.payout_type == 'cash':
            if self.option_type == 'call':
                # Cash-or-nothing call: Q * e^(-rT) * N(d2)
                price = self.payout_amount * np.exp(-self.r * self.T) * norm.cdf(d2)
            else:  # put
                # Cash-or-nothing put: Q * e^(-rT) * N(-d2)
                price = self.payout_amount * np.exp(-self.r * self.T) * norm.cdf(-d2)
        else:  # asset
            if self.option_type == 'call':
                # Asset-or-nothing call: S * e^(-qT) * N(d1)
                price = self.S * np.exp(-self.q * self.T) * norm.cdf(d1)
            else:  # put
                # Asset-or-nothing put: S * e^(-qT) * N(-d1)
                price = self.S * np.exp(-self.q * self.T) * norm.cdf(-d1)

        return float(price)

    def __repr__(self) -> str:
        return (f"DigitalOption({self.payout_type.capitalize()}-or-nothing, {self.option_type}, "
                f"S={self.S:.2f}, K={self.K:.2f})")
