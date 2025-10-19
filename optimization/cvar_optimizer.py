"""
CVaR (Conditional Value at Risk) Portfolio Optimization

CVaR measures the expected loss in the worst α% of cases.
It's also called Expected Shortfall (ES) or Average Value at Risk (AVaR).

Mathematical Foundation:
-----------------------
VaR_α: Value at Risk at confidence level α
CVaR_α: E[Loss | Loss > VaR_α]

CVaR is:
- More conservative than VaR
- Coherent risk measure (unlike VaR)
- Better for tail risk management
- Convex optimization problem
"""

import numpy as np
from scipy.optimize import minimize, linprog
from typing import Dict, Optional, Tuple
import warnings


class CVaROptimizer:
    """
    Portfolio optimization minimizing Conditional Value at Risk (CVaR).

    CVaR is the expected loss in the worst α% of scenarios.
    For example, CVaR_95 is the average loss in the worst 5% of outcomes.

    Advantages over variance:
    - Focuses on tail risk
    - Asymmetric loss treatment
    - Coherent risk measure

    Attributes:
        returns (np.ndarray): Historical returns (n_periods × n_assets)
        alpha (float): Confidence level (e.g., 0.95 for 95% CVaR)
        n_assets (int): Number of assets
        n_scenarios (int): Number of historical scenarios

    Example:
        >>> returns = np.random.randn(252, 10) * 0.01
        >>> cvar = CVaROptimizer(returns, alpha=0.95)
        >>> result = cvar.optimize()
        >>> print(f"CVaR 95%: {result['cvar']:.4f}")
    """

    def __init__(
        self,
        returns: np.ndarray,
        alpha: float = 0.95,
        frequency: int = 252
    ):
        """
        Initialize CVaR optimizer.

        Parameters:
            returns: Historical returns matrix (n_periods × n_assets)
            alpha: Confidence level (default 0.95 for 95% CVaR)
            frequency: Periods per year for annualization
        """
        self.returns = np.asarray(returns)
        self.alpha = alpha
        self.frequency = frequency

        self.n_scenarios, self.n_assets = returns.shape

        if alpha <= 0 or alpha >= 1:
            raise ValueError("Alpha must be between 0 and 1")

        if self.n_scenarios < 50:
            warnings.warn(f"Only {self.n_scenarios} scenarios - CVaR estimate may be unreliable")

    def calculate_cvar(
        self,
        weights: np.ndarray,
        returns: Optional[np.ndarray] = None
    ) -> Tuple[float, float]:
        """
        Calculate VaR and CVaR for given weights.

        Parameters:
            weights: Portfolio weights
            returns: Returns matrix (default: use self.returns)

        Returns:
            Tuple of (VaR, CVaR)
        """
        if returns is None:
            returns = self.returns

        weights = np.asarray(weights)

        # Portfolio returns for each scenario
        portfolio_returns = np.dot(returns, weights)

        # Sort returns (ascending, so worst losses first)
        sorted_returns = np.sort(portfolio_returns)

        # VaR: α-quantile of loss distribution
        var_index = int(np.floor((1 - self.alpha) * len(sorted_returns)))
        var = -sorted_returns[var_index]  # Negative because we want loss

        # CVaR: mean of returns worse than VaR
        cvar_returns = sorted_returns[:var_index+1]
        cvar = -np.mean(cvar_returns) if len(cvar_returns) > 0 else 0.0

        return var, cvar

    def _cvar_objective(self, weights: np.ndarray) -> float:
        """
        Objective function: CVaR to minimize.

        Parameters:
            weights: Portfolio weights

        Returns:
            CVaR value
        """
        _, cvar = self.calculate_cvar(weights)
        return cvar

    def optimize(
        self,
        target_return: Optional[float] = None,
        allow_short: bool = False
    ) -> Dict[str, any]:
        """
        Minimize portfolio CVaR.

        Parameters:
            target_return: Minimum required return (optional)
            allow_short: Allow short positions

        Returns:
            Dictionary with weights, return, CVaR, VaR
        """
        # Initial guess
        x0 = np.ones(self.n_assets) / self.n_assets

        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}  # Sum to 1
        ]

        # Add return constraint if specified
        if target_return is not None:
            mean_returns = np.mean(self.returns, axis=0) * self.frequency
            constraints.append({
                'type': 'ineq',
                'fun': lambda w: np.dot(w, mean_returns) - target_return
            })

        # Bounds
        if allow_short:
            bounds = None
        else:
            bounds = [(0, 1) for _ in range(self.n_assets)]

        # Optimize
        result = minimize(
            self._cvar_objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000}
        )

        if not result.success:
            warnings.warn(f"Optimization did not converge: {result.message}")

        weights = result.x

        # Calculate metrics
        var, cvar = self.calculate_cvar(weights)
        portfolio_return = np.mean(np.dot(self.returns, weights)) * self.frequency
        portfolio_vol = np.std(np.dot(self.returns, weights)) * np.sqrt(self.frequency)

        return {
            'weights': weights,
            'return': portfolio_return,
            'volatility': portfolio_vol,
            'var': var,
            'cvar': cvar,
            'cvar_ratio': portfolio_return / cvar if cvar > 0 else 0.0,  # Similar to Sharpe
            'success': result.success
        }

    def efficient_frontier_cvar(
        self,
        n_points: int = 50,
        allow_short: bool = False
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute CVaR-based efficient frontier.

        Instead of risk-return, this shows CVaR-return tradeoff.

        Parameters:
            n_points: Number of points on frontier
            allow_short: Allow short positions

        Returns:
            Tuple of (returns, cvars, weights)
        """
        mean_returns = np.mean(self.returns, axis=0) * self.frequency

        # Min and max return
        min_ret = np.min(mean_returns)
        max_ret = np.max(mean_returns)

        target_returns = np.linspace(min_ret, max_ret, n_points)

        frontier_returns = []
        frontier_cvars = []
        frontier_weights = []

        for target in target_returns:
            try:
                result = self.optimize(target_return=target, allow_short=allow_short)
                frontier_returns.append(result['return'])
                frontier_cvars.append(result['cvar'])
                frontier_weights.append(result['weights'])
            except:
                continue

        return (
            np.array(frontier_returns),
            np.array(frontier_cvars),
            np.array(frontier_weights)
        )

    def compare_to_variance(self) -> Dict:
        """
        Compare CVaR optimization to variance optimization.

        Returns:
            Dictionary comparing both approaches
        """
        from .markowitz import MarkowitzOptimizer

        # CVaR optimization
        cvar_result = self.optimize()

        # Variance optimization
        mv_optimizer = MarkowitzOptimizer(self.returns, frequency=self.frequency)
        mv_result = mv_optimizer.min_variance()

        # Evaluate CVaR for variance-optimal portfolio
        var_mv, cvar_mv = self.calculate_cvar(mv_result['weights'])

        # Evaluate variance for CVaR-optimal portfolio
        cvar_portfolio_returns = np.dot(self.returns, cvar_result['weights'])
        vol_cvar = np.std(cvar_portfolio_returns) * np.sqrt(self.frequency)

        return {
            'cvar_optimal': {
                'weights': cvar_result['weights'],
                'return': cvar_result['return'],
                'volatility': vol_cvar,
                'cvar': cvar_result['cvar'],
                'var': cvar_result['var']
            },
            'variance_optimal': {
                'weights': mv_result['weights'],
                'return': mv_result['return'],
                'volatility': mv_result['volatility'],
                'cvar': cvar_mv,
                'var': var_mv
            }
        }


def calculate_historical_cvar(
    returns: np.ndarray,
    alpha: float = 0.95
) -> Tuple[float, float]:
    """
    Calculate historical VaR and CVaR for a return series.

    Parameters:
        returns: 1D array of returns
        alpha: Confidence level

    Returns:
        Tuple of (VaR, CVaR)
    """
    returns = np.asarray(returns)
    sorted_returns = np.sort(returns)

    var_index = int(np.floor((1 - alpha) * len(sorted_returns)))
    var = -sorted_returns[var_index]

    cvar_returns = sorted_returns[:var_index+1]
    cvar = -np.mean(cvar_returns) if len(cvar_returns) > 0 else 0.0

    return var, cvar


def parametric_cvar(
    mean: float,
    std: float,
    alpha: float = 0.95
) -> Tuple[float, float]:
    """
    Calculate parametric (normal distribution) VaR and CVaR.

    Assumes returns are normally distributed.

    Parameters:
        mean: Expected return
        std: Standard deviation
        alpha: Confidence level

    Returns:
        Tuple of (VaR, CVaR)
    """
    from scipy.stats import norm

    # Z-score for alpha confidence
    z_alpha = norm.ppf(1 - alpha)

    # VaR
    var = -(mean + z_alpha * std)

    # CVaR for normal distribution
    # CVaR = -mean + std * φ(z_α) / (1 - α)
    # where φ is the standard normal PDF
    pdf_z = norm.pdf(z_alpha)
    cvar = -(mean - std * pdf_z / (1 - alpha))

    return var, cvar
