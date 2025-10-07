"""
Helios Quant Framework - ML Forecasting Module
Machine learning models for predicting IRR, returns, and volatility
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
import json
from typing import Dict, List, Tuple
import os


class PortfolioMLForecaster:
    """Machine learning forecasting for portfolio metrics"""

    def __init__(self, model_type='random_forest'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_importance = None

    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and target for ML model"""
        feature_cols = ['vintage', 'committed_capital', 'benchmark_return', 'volatility']

        # Create additional features
        df['vintage_age'] = 2025 - df['vintage']
        df['risk_premium'] = df['irr'] - df['benchmark_return']
        df['sharpe_proxy'] = df['irr'] / df['volatility']

        # Encode sector
        sector_dummies = pd.get_dummies(df['sector'], prefix='sector')
        df = pd.concat([df, sector_dummies], axis=1)

        feature_cols.extend(['vintage_age', 'sharpe_proxy'] + list(sector_dummies.columns))

        X = df[feature_cols].values
        y = df['irr'].values

        return X, y

    def train_model(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train the forecasting model"""
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)

        # Initialize model
        if self.model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=200,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )

        # Train model
        self.model.fit(X_train_scaled, y_train)

        # Get feature importance
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance = self.model.feature_importances_

    def predict(self, X_test: np.ndarray) -> np.ndarray:
        """Make predictions"""
        X_test_scaled = self.scaler.transform(X_test)
        return self.model.predict(X_test_scaled)

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """Evaluate model performance"""
        y_pred = self.predict(X_test)

        metrics = {
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2_score': r2_score(y_test, y_pred),
            'mean_error': np.mean(y_pred - y_test),
            'std_error': np.std(y_pred - y_test)
        }

        return metrics


def train_irr_forecaster(data_file='portfolio_data.csv') -> Dict:
    """Train IRR forecasting model and return results"""

    # Load data (or generate synthetic data for demo)
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
    else:
        # Generate synthetic portfolio data
        np.random.seed(42)
        n_samples = 200

        df = pd.DataFrame({
            'fund_id': range(1, n_samples + 1),
            'vintage': np.random.randint(2015, 2025, n_samples),
            'sector': np.random.choice(['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer'], n_samples),
            'committed_capital': np.random.uniform(50, 500, n_samples),
            'benchmark_return': np.random.normal(0.08, 0.02, n_samples),
            'volatility': np.random.uniform(0.15, 0.35, n_samples)
        })

        # Generate IRR based on features with some noise
        df['irr'] = (
            0.05 +
            (2025 - df['vintage']) * 0.005 +
            df['benchmark_return'] * 0.8 +
            np.random.normal(0, 0.03, n_samples)
        )

    # Initialize forecaster
    forecaster = PortfolioMLForecaster(model_type='random_forest')

    # Prepare features
    X, y = forecaster.prepare_features(df)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train model
    forecaster.train_model(X_train, y_train)

    # Evaluate
    metrics = forecaster.evaluate(X_test, y_test)

    # Cross-validation
    X_scaled = forecaster.scaler.transform(X)
    cv_scores = cross_val_score(forecaster.model, X_scaled, y, cv=5, scoring='r2')
    metrics['cv_r2_mean'] = cv_scores.mean()
    metrics['cv_r2_std'] = cv_scores.std()

    # Make predictions on test set
    y_pred = forecaster.predict(X_test)

    # Create visualization
    create_forecast_plots(y_test, y_pred, forecaster.feature_importance)

    print("\n=== ML Forecasting Results ===")
    print(f"Model: {forecaster.model_type}")
    print(f"RMSE: {metrics['rmse']:.4f}")
    print(f"MAE: {metrics['mae']:.4f}")
    print(f"R² Score: {metrics['r2_score']:.4f}")
    print(f"CV R² Mean: {metrics['cv_r2_mean']:.4f} (+/- {metrics['cv_r2_std']:.4f})")

    # Export results
    os.makedirs('python/output', exist_ok=True)
    with open('python/output/ml_forecast_results.json', 'w') as f:
        json.dump(metrics, f, indent=2)

    return metrics


def create_forecast_plots(y_true: np.ndarray, y_pred: np.ndarray, feature_importance: np.ndarray = None):
    """Create visualization plots for forecasting results"""

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('ML Forecasting Results - Helios Quant Framework', fontsize=16, fontweight='bold')

    # 1. Actual vs Predicted
    axes[0, 0].scatter(y_true * 100, y_pred * 100, alpha=0.6, edgecolors='k')
    axes[0, 0].plot([y_true.min() * 100, y_true.max() * 100],
                    [y_true.min() * 100, y_true.max() * 100], 'r--', lw=2)
    axes[0, 0].set_xlabel('Actual IRR (%)', fontsize=11)
    axes[0, 0].set_ylabel('Predicted IRR (%)', fontsize=11)
    axes[0, 0].set_title('Actual vs Predicted IRR', fontsize=12, fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3)

    # 2. Residuals distribution
    residuals = (y_pred - y_true) * 100
    axes[0, 1].hist(residuals, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
    axes[0, 1].axvline(x=0, color='red', linestyle='--', linewidth=2)
    axes[0, 1].set_xlabel('Prediction Error (%)', fontsize=11)
    axes[0, 1].set_ylabel('Frequency', fontsize=11)
    axes[0, 1].set_title('Prediction Error Distribution', fontsize=12, fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3)

    # 3. Residuals vs Predicted
    axes[1, 0].scatter(y_pred * 100, residuals, alpha=0.6, edgecolors='k')
    axes[1, 0].axhline(y=0, color='red', linestyle='--', linewidth=2)
    axes[1, 0].set_xlabel('Predicted IRR (%)', fontsize=11)
    axes[1, 0].set_ylabel('Residuals (%)', fontsize=11)
    axes[1, 0].set_title('Residual Plot', fontsize=12, fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)

    # 4. Feature importance (if available)
    if feature_importance is not None:
        feature_names = ['Vintage', 'Capital', 'Benchmark', 'Volatility', 'Age', 'Sharpe', 'Sector_*']
        importance = feature_importance[:len(feature_names)]

        axes[1, 1].barh(range(len(importance)), importance, color='teal', alpha=0.7)
        axes[1, 1].set_yticks(range(len(importance)))
        axes[1, 1].set_yticklabels(feature_names[:len(importance)])
        axes[1, 1].set_xlabel('Importance Score', fontsize=11)
        axes[1, 1].set_title('Feature Importance', fontsize=12, fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3, axis='x')
    else:
        axes[1, 1].text(0.5, 0.5, 'Feature importance\nnot available',
                        ha='center', va='center', fontsize=12)
        axes[1, 1].axis('off')

    plt.tight_layout()

    # Save plot
    os.makedirs('python/output', exist_ok=True)
    plt.savefig('python/output/ml_forecast_plots.png', dpi=300, bbox_inches='tight')
    print("Forecast plots saved to: python/output/ml_forecast_plots.png")


if __name__ == "__main__":
    train_irr_forecaster()
