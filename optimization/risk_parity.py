"""
Risk Parity Portfolio Optimization

Risk parity allocates capital such that each asset contributes equally to
overall portfolio risk (not equal weights!).

Mathematical Foundation:
-----------------------
Risk contribution of asset i: RC_i = w_i × (Σw)_i / sqrt(w^T Σ w)
Risk parity condition: RC_1 = RC_2 = ... = RC_n

This is solved numerically since there's no closed-form solution.
"""

import numpy as np
from scipy.optimize import minimize
from typing import Dict, Optional
import warnings


class RiskParityOptimizer:
    """
    Risk parity portfolio optimization.

    Each asset contributes equally to portfolio risk, regardless of its weight.
    This approach often leads to better diversification than equal weighting.

    The optimization problem:
        Find weights w such that risk contributions are equal
        Subject to: sum(w) = 1, w >= 0

    Attributes:
        cov_matrix (np.ndarray): Covariance matrix of asset returns
        n_assets (int): Number of assets

    Example:
        >>> returns = np.random.randn(252, 10) * 0.01
        >>> cov_matrix = np.cov(returns, rowvar=False) * 252
        >>> rp = RiskParityOptimizer(cov_matrix)
        >>> result = rp.optimize()
        >>> print(result['weights'])
    """

    def __init__(self, cov_matrix: np.ndarray):
        """
        Initialize risk parity optimizer.

        Parameters:
            cov_matrix: Covariance matrix of returns (n_assets × n_assets)
        """
        self.cov_matrix = np.asarray(cov_matrix)
        self.n_assets = cov_matrix.shape[0]

        if self.cov_matrix.shape[0] != self.cov_matrix.shape[1]:
            raise ValueError("Covariance matrix must be square")

        # Check positive definite
        try:
            np.linalg.cholesky(self.cov_matrix)
        except np.linalg.LinAlgError:
            warnings.warn("Covariance matrix is not positive definite. Adding regularization.")
            self.cov_matrix += np.eye(self.n_assets) * 1e-8

    def risk_contributions(self, weights: np.ndarray) -> np.ndarray:
        """
        Calculate risk contribution of each asset.

        Risk contribution: RC_i = w_i × (Σw)_i / portfolio_volatility

        Parameters:
            weights: Portfolio weights

        Returns:
            Array of risk contributions for each asset
        """
        weights = np.asarray(weights)

        # Portfolio variance and volatility
        portfolio_variance = np.dot(weights, np.dot(self.cov_matrix, weights))
        portfolio_vol = np.sqrt(portfolio_variance)

        if portfolio_vol < 1e-10:
            return np.zeros(self.n_assets)

        # Marginal contribution to risk: ∂σ_p/∂w_i = (Σw)_i / σ_p
        marginal_contrib = np.dot(self.cov_matrix, weights) / portfolio_vol

        # Risk contribution: w_i × marginal_contrib_i
        risk_contrib = weights * marginal_contrib

        return risk_contrib

    def _risk_parity_objective(self, weights: np.ndarray) -> float:
        """
        Objective function: minimize variance of risk contributions.

        When all risk contributions are equal, variance is zero.

        Parameters:
            weights: Portfolio weights

        Returns:
            Sum of squared differences from equal risk contribution
        """
        rc = self.risk_contributions(weights)

        # Target: equal risk contribution (1/n of total risk)
        target_rc = np.mean(rc)

        # Minimize squared deviations
        return np.sum((rc - target_rc) ** 2)

    def optimize(
        self,
        initial_weights: Optional[np.ndarray] = None,
        bounds: Optional[tuple] = None
    ) -> Dict[str, any]:
        """
        Find risk parity weights.

        Parameters:
            initial_weights: Starting point (default: equal weights)
            bounds: Weight bounds (default: (0, 1))

        Returns:
            Dictionary with weights, volatility, and risk contributions
        """
        # Initial guess
        if initial_weights is None:
            x0 = np.ones(self.n_assets) / self.n_assets
        else:
            x0 = initial_weights

        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}  # Sum to 1
        ]

        # Bounds
        if bounds is None:
            bounds = [(0, 1) for _ in range(self.n_assets)]

        # Optimize
        result = minimize(
            self._risk_parity_objective,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': 1000, 'ftol': 1e-9}
        )

        if not result.success:
            warnings.warn(f"Optimization did not converge: {result.message}")

        weights = result.x

        # Calculate performance metrics
        portfolio_variance = np.dot(weights, np.dot(self.cov_matrix, weights))
        portfolio_vol = np.sqrt(portfolio_variance)
        risk_contrib = self.risk_contributions(weights)

        # Verify equal risk contribution
        rc_std = np.std(risk_contrib)

        return {
            'weights': weights,
            'volatility': portfolio_vol,
            'risk_contributions': risk_contrib,
            'rc_std_dev': rc_std,  # Should be close to 0 for perfect risk parity
            'success': result.success
        }

    def compare_to_equal_weight(self, mean_returns: Optional[np.ndarray] = None) -> Dict:
        """
        Compare risk parity to equal weighting.

        Parameters:
            mean_returns: Expected returns (optional, for return calculation)

        Returns:
            Dictionary comparing both approaches
        """
        # Risk parity
        rp_result = self.optimize()

        # Equal weight
        ew_weights = np.ones(self.n_assets) / self.n_assets
        ew_vol = np.sqrt(np.dot(ew_weights, np.dot(self.cov_matrix, ew_weights)))
        ew_rc = self.risk_contributions(ew_weights)

        comparison = {
            'risk_parity': {
                'weights': rp_result['weights'],
                'volatility': rp_result['volatility'],
                'risk_contributions': rp_result['risk_contributions'],
                'rc_std': rp_result['rc_std_dev']
            },
            'equal_weight': {
                'weights': ew_weights,
                'volatility': ew_vol,
                'risk_contributions': ew_rc,
                'rc_std': np.std(ew_rc)
            }
        }

        # Add returns if provided
        if mean_returns is not None:
            comparison['risk_parity']['return'] = np.dot(rp_result['weights'], mean_returns)
            comparison['equal_weight']['return'] = np.dot(ew_weights, mean_returns)
            comparison['risk_parity']['sharpe'] = (
                comparison['risk_parity']['return'] / rp_result['volatility']
            )
            comparison['equal_weight']['sharpe'] = (
                comparison['equal_weight']['return'] / ew_vol
            )

        return comparison


def risk_parity_analytical_2asset(
    vol1: float,
    vol2: float,
    corr: float
) -> tuple:
    """
    Analytical solution for 2-asset risk parity.

    For 2 assets, there's a closed-form solution.

    Parameters:
        vol1: Volatility of asset 1
        vol2: Volatility of asset 2
        corr: Correlation between assets

    Returns:
        Tuple of (weight1, weight2)
    """
    # Risk parity weights for 2 assets
    # w1 = σ2 / (σ1 + σ2) when correlation = 1
    # More complex for corr != 1

    if abs(corr) >= 1:
        # Perfect correlation case
        w1 = vol2 / (vol1 + vol2)
        w2 = vol1 / (vol1 + vol2)
    else:
        # Numerical solution needed for general case
        cov_matrix = np.array([
            [vol1**2, corr * vol1 * vol2],
            [corr * vol1 * vol2, vol2**2]
        ])
        rp = RiskParityOptimizer(cov_matrix)
        result = rp.optimize()
        w1, w2 = result['weights']

    return w1, w2
