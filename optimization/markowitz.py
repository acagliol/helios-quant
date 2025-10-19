"""
Markowitz Mean-Variance Portfolio Optimization

Implements modern portfolio theory with efficient frontier construction
and various optimization objectives.

Mathematical Foundation:
-----------------------
Portfolio return: μ_p = w^T μ
Portfolio variance: σ_p^2 = w^T Σ w
Sharpe ratio: (μ_p - r_f) / σ_p

Optimization problems:
1. Minimum variance: min w^T Σ w
2. Maximum Sharpe: max (w^T μ - r_f) / sqrt(w^T Σ w)
3. Target return: min w^T Σ w  s.t. w^T μ = μ_target
"""

import numpy as np
from scipy.optimize import minimize, LinearConstraint, Bounds
from typing import Dict, List, Optional, Tuple
import warnings


class MarkowitzOptimizer:
    """
    Mean-variance portfolio optimizer using Markowitz framework.

    Supports:
    - Efficient frontier construction
    - Maximum Sharpe ratio portfolio
    - Minimum variance portfolio
    - Target return optimization
    - Custom constraints (sector limits, position limits, etc.)

    Attributes:
        returns (np.ndarray): Historical returns matrix (n_periods × n_assets)
        risk_free_rate (float): Annual risk-free rate
        mean_returns (np.ndarray): Expected returns for each asset
        cov_matrix (np.ndarray): Covariance matrix of returns
        n_assets (int): Number of assets

    Example:
        >>> returns = np.random.randn(252, 10) * 0.01  # 10 assets, 1 year daily
        >>> optimizer = MarkowitzOptimizer(returns, risk_free_rate=0.02)
        >>> max_sharpe_weights = optimizer.max_sharpe_ratio()
        >>> frontier = optimizer.efficient_frontier(n_points=50)
    """

    def __init__(
        self,
        returns: np.ndarray,
        risk_free_rate: float = 0.02,
        frequency: int = 252  # trading days per year
    ):
        """
        Initialize Markowitz optimizer.

        Parameters:
            returns: Historical returns matrix (n_periods × n_assets)
            risk_free_rate: Annual risk-free rate (default 2%)
            frequency: Number of periods per year for annualization (default 252 for daily)
        """
        self.returns = np.asarray(returns)
        self.risk_free_rate = risk_free_rate
        self.frequency = frequency

        # Calculate expected returns and covariance
        self.mean_returns = np.mean(returns, axis=0) * frequency  # Annualized
        self.cov_matrix = np.cov(returns, rowvar=False) * frequency  # Annualized
        self.n_assets = returns.shape[1]

        # Validation
        if self.n_assets < 2:
            raise ValueError("Need at least 2 assets for portfolio optimization")

        # Check for positive definite covariance matrix
        try:
            np.linalg.cholesky(self.cov_matrix)
        except np.linalg.LinAlgError:
            warnings.warn("Covariance matrix is not positive definite. Adding regularization.")
            self.cov_matrix += np.eye(self.n_assets) * 1e-8

    def portfolio_performance(self, weights: np.ndarray) -> Tuple[float, float, float]:
        """
        Calculate portfolio performance metrics.

        Parameters:
            weights: Portfolio weights (must sum to 1)

        Returns:
            Tuple of (return, volatility, sharpe_ratio)
        """
        weights = np.asarray(weights)

        portfolio_return = np.dot(weights, self.mean_returns)
        portfolio_variance = np.dot(weights, np.dot(self.cov_matrix, weights))
        portfolio_vol = np.sqrt(portfolio_variance)

        sharpe = (portfolio_return - self.risk_free_rate) / portfolio_vol if portfolio_vol > 0 else 0.0

        return portfolio_return, portfolio_vol, sharpe

    def min_variance(
        self,
        allow_short: bool = False,
        constraints: Optional[List] = None
    ) -> Dict[str, any]:
        """
        Find minimum variance portfolio.

        Parameters:
            allow_short: Allow short positions (negative weights)
            constraints: Additional constraints (list of dicts)

        Returns:
            Dictionary with weights, return, volatility, and Sharpe ratio
        """
        def objective(weights):
            return np.dot(weights, np.dot(self.cov_matrix, weights))

        # Initial guess: equal weighting
        x0 = np.ones(self.n_assets) / self.n_assets

        # Constraints
        cons = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]  # Weights sum to 1
        if constraints:
            cons.extend(constraints)

        # Bounds
        if allow_short:
            bounds = None  # No bounds
        else:
            bounds = Bounds(0, 1)  # No shorting

        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=cons,
            options={'maxiter': 1000}
        )

        if not result.success:
            warnings.warn(f"Optimization did not converge: {result.message}")

        weights = result.x
        ret, vol, sharpe = self.portfolio_performance(weights)

        return {
            'weights': weights,
            'return': ret,
            'volatility': vol,
            'sharpe_ratio': sharpe
        }

    def max_sharpe_ratio(
        self,
        allow_short: bool = False,
        constraints: Optional[List] = None
    ) -> Dict[str, any]:
        """
        Find portfolio with maximum Sharpe ratio.

        This is the tangency portfolio on the efficient frontier.

        Parameters:
            allow_short: Allow short positions
            constraints: Additional constraints

        Returns:
            Dictionary with weights, return, volatility, and Sharpe ratio
        """
        def objective(weights):
            ret, vol, sharpe = self.portfolio_performance(weights)
            return -sharpe  # Negative because we're minimizing

        x0 = np.ones(self.n_assets) / self.n_assets

        cons = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
        if constraints:
            cons.extend(constraints)

        if allow_short:
            bounds = None
        else:
            bounds = Bounds(0, 1)

        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=cons,
            options={'maxiter': 1000}
        )

        if not result.success:
            warnings.warn(f"Optimization did not converge: {result.message}")

        weights = result.x
        ret, vol, sharpe = self.portfolio_performance(weights)

        return {
            'weights': weights,
            'return': ret,
            'volatility': vol,
            'sharpe_ratio': sharpe
        }

    def target_return(
        self,
        target: float,
        allow_short: bool = False,
        constraints: Optional[List] = None
    ) -> Dict[str, any]:
        """
        Find minimum variance portfolio for a target return.

        Parameters:
            target: Target annual return
            allow_short: Allow short positions
            constraints: Additional constraints

        Returns:
            Dictionary with weights, return, volatility, and Sharpe ratio
        """
        def objective(weights):
            return np.dot(weights, np.dot(self.cov_matrix, weights))

        x0 = np.ones(self.n_assets) / self.n_assets

        cons = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},  # Sum to 1
            {'type': 'eq', 'fun': lambda w: np.dot(w, self.mean_returns) - target}  # Target return
        ]
        if constraints:
            cons.extend(constraints)

        if allow_short:
            bounds = None
        else:
            bounds = Bounds(0, 1)

        result = minimize(
            objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=cons,
            options={'maxiter': 1000}
        )

        if not result.success:
            warnings.warn(f"Optimization did not converge: {result.message}")

        weights = result.x
        ret, vol, sharpe = self.portfolio_performance(weights)

        return {
            'weights': weights,
            'return': ret,
            'volatility': vol,
            'sharpe_ratio': sharpe
        }

    def efficient_frontier(
        self,
        n_points: int = 100,
        allow_short: bool = False
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute the efficient frontier.

        Parameters:
            n_points: Number of points on the frontier
            allow_short: Allow short positions

        Returns:
            Tuple of (returns, volatilities, sharpe_ratios)
        """
        # Get min and max return portfolios
        min_var = self.min_variance(allow_short=allow_short)
        max_sharpe = self.max_sharpe_ratio(allow_short=allow_short)

        min_ret = min_var['return']
        max_ret = max_sharpe['return'] * 1.5  # Go beyond max Sharpe for full frontier

        # Generate target returns
        target_returns = np.linspace(min_ret, max_ret, n_points)

        frontier_returns = []
        frontier_vols = []
        frontier_sharpes = []
        frontier_weights = []

        for target in target_returns:
            try:
                result = self.target_return(target, allow_short=allow_short)
                frontier_returns.append(result['return'])
                frontier_vols.append(result['volatility'])
                frontier_sharpes.append(result['sharpe_ratio'])
                frontier_weights.append(result['weights'])
            except:
                continue  # Skip if optimization fails

        return (
            np.array(frontier_returns),
            np.array(frontier_vols),
            np.array(frontier_sharpes),
            np.array(frontier_weights)
        )

    def optimize_with_constraints(
        self,
        objective: str = 'max_sharpe',
        weight_bounds: Optional[Tuple[float, float]] = None,
        sector_limits: Optional[Dict[str, Tuple[List[int], float, float]]] = None,
        turnover_limit: Optional[float] = None,
        current_weights: Optional[np.ndarray] = None
    ) -> Dict[str, any]:
        """
        Optimize portfolio with custom constraints.

        Parameters:
            objective: 'max_sharpe', 'min_variance', or target return value
            weight_bounds: (min_weight, max_weight) for each asset
            sector_limits: Dict of sector constraints
                Format: {'sector_name': ([asset_indices], min_weight, max_weight)}
            turnover_limit: Maximum portfolio turnover from current_weights
            current_weights: Current portfolio weights (for turnover constraint)

        Returns:
            Dictionary with weights, return, volatility, and Sharpe ratio
        """
        constraints = []

        # Sector constraints
        if sector_limits:
            for sector_name, (indices, min_w, max_w) in sector_limits.items():
                # Min constraint
                constraints.append({
                    'type': 'ineq',
                    'fun': lambda w, idx=indices, m=min_w: np.sum(w[idx]) - m
                })
                # Max constraint
                constraints.append({
                    'type': 'ineq',
                    'fun': lambda w, idx=indices, m=max_w: m - np.sum(w[idx])
                })

        # Turnover constraint
        if turnover_limit is not None and current_weights is not None:
            constraints.append({
                'type': 'ineq',
                'fun': lambda w: turnover_limit - np.sum(np.abs(w - current_weights))
            })

        # Determine objective
        if objective == 'max_sharpe':
            return self.max_sharpe_ratio(allow_short=False, constraints=constraints)
        elif objective == 'min_variance':
            return self.min_variance(allow_short=False, constraints=constraints)
        elif isinstance(objective, (int, float)):
            return self.target_return(objective, allow_short=False, constraints=constraints)
        else:
            raise ValueError(f"Unknown objective: {objective}")


def generate_sample_returns(
    n_assets: int = 10,
    n_periods: int = 252,
    seed: Optional[int] = None
) -> np.ndarray:
    """
    Generate sample returns for testing.

    Parameters:
        n_assets: Number of assets
        n_periods: Number of time periods
        seed: Random seed for reproducibility

    Returns:
        Returns matrix (n_periods × n_assets)
    """
    if seed is not None:
        np.random.seed(seed)

    # Generate correlated returns
    # Create correlation matrix
    corr = np.random.uniform(0.1, 0.5, (n_assets, n_assets))
    corr = (corr + corr.T) / 2  # Make symmetric
    np.fill_diagonal(corr, 1.0)

    # Make positive semi-definite
    eigenvalues, eigenvectors = np.linalg.eigh(corr)
    eigenvalues = np.maximum(eigenvalues, 0.01)  # Ensure positive
    corr = eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T

    # Generate returns
    mean_returns = np.random.uniform(0.00005, 0.0005, n_assets)  # Daily returns
    vols = np.random.uniform(0.01, 0.03, n_assets)  # Daily volatility

    # Cholesky decomposition
    L = np.linalg.cholesky(corr)

    # Generate correlated random returns
    returns = np.random.randn(n_periods, n_assets) @ L.T
    returns = returns * vols + mean_returns

    return returns
