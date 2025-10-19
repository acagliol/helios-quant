# 📅 Month 1: Mathematical Foundation

**Timeline**: Weeks 1-4
**Focus**: Options pricing, performance optimization, portfolio theory
**Goal**: Build rigorous quantitative finance foundations

---

## 🎯 Month 1 Objectives

By end of Month 1, you will have:
- ✅ Production-quality options pricing library (10+ models)
- ✅ Optimized Monte Carlo engine (<50ms for 1M paths)
- ✅ Mean-variance portfolio optimizer
- ✅ All code validated against QuantLib
- ✅ Comprehensive test suite (>80% coverage)
- ✅ Performance benchmarks documented

---

## 📚 REQUIRED READING (Before Week 1)

### Critical
1. **John Hull - "Options, Futures, and Other Derivatives"**
   - Chapters 1-13: Fundamentals through Black-Scholes
   - Chapters 15-17: Greeks and volatility
   - Chapter 19: Basic numerical procedures

2. **Paul Wilmott - "Paul Wilmott on Quantitative Finance"**
   - Vol 1, Ch 5-7: Black-Scholes, Greeks

### Supplementary
3. **Python for Finance** by Yves Hilpisch (Ch 6-8)
4. **Computational Finance** by Klaus Sandmann

### Academic Papers
- Black, F., & Scholes, M. (1973). "The Pricing of Options and Corporate Liabilities"
- Heston, S. (1993). "A Closed-Form Solution for Options with Stochastic Volatility"

---

## 🗓️ WEEK 1: Black-Scholes & Greeks

### Learning Objectives
- Understand Black-Scholes PDE derivation
- Implement closed-form solution
- Calculate all Greeks analytically
- Validate numerical accuracy

### Deliverables

#### 1. `pricing/options/black_scholes.py`
```python
class BlackScholes:
    """
    Black-Scholes option pricing with Greeks.

    Validates against QuantLib with <0.01% error tolerance.
    """

    def __init__(self, S, K, T, r, sigma, option_type='call'):
        """
        Parameters:
        - S: Spot price
        - K: Strike price
        - T: Time to maturity (years)
        - r: Risk-free rate
        - sigma: Volatility
        - option_type: 'call' or 'put'
        """
        pass

    def price(self) -> float:
        """Calculate option price."""
        pass

    def delta(self) -> float:
        """First derivative wrt spot."""
        pass

    def gamma(self) -> float:
        """Second derivative wrt spot."""
        pass

    def vega(self) -> float:
        """Derivative wrt volatility."""
        pass

    def theta(self) -> float:
        """Derivative wrt time."""
        pass

    def rho(self) -> float:
        """Derivative wrt risk-free rate."""
        pass
```

#### 2. `pricing/options/tests/test_black_scholes.py`
Test cases must include:
- Standard European calls/puts
- ATM, ITM, OTM scenarios
- Short and long maturities
- Low and high volatility
- Dividend-paying stocks
- Put-call parity validation
- Greek accuracy tests
- Edge cases (T→0, σ→0, etc.)

**Target**: 25+ test cases, all passing

#### 3. `pricing/options/docs/black_scholes.md`
Documentation must include:
- Mathematical derivation (Black-Scholes PDE)
- Closed-form solution
- Greeks formulas
- Numerical implementation details
- Validation methodology
- Known limitations

#### 4. Validation Report
Compare against QuantLib for 100+ scenarios:
- Max error: <0.01%
- Mean absolute error
- Standard deviation of errors
- Performance comparison

### Week 1 Success Criteria
- [ ] All formulas implemented correctly
- [ ] <0.01% error vs QuantLib on 100+ test cases
- [ ] All Greeks computed analytically (no numerical differentiation)
- [ ] Edge cases handled gracefully
- [ ] Full documentation with math

### Time Estimate
- Reading & understanding: 8-10 hours
- Implementation: 6-8 hours
- Testing & validation: 4-6 hours
- Documentation: 2-4 hours
- **Total**: 20-28 hours

---

## 🗓️ WEEK 2: Advanced Option Models

### Learning Objectives
- Stochastic volatility (Heston model)
- Jump diffusion (Merton model)
- Exotic options (Asian, Barrier)
- Numerical methods for pricing

### Deliverables

#### 1. `pricing/options/heston.py`
Heston stochastic volatility model:
```python
class HestonModel:
    """
    Heston model with stochastic volatility.

    dS = μS dt + √v S dW1
    dv = κ(θ - v) dt + σ √v dW2
    """

    def __init__(self, S0, v0, kappa, theta, sigma, rho, r, T, K):
        pass

    def price_call(self) -> float:
        """Price using characteristic function."""
        pass

    def price_put(self) -> float:
        """Price using characteristic function."""
        pass

    def implied_volatility_surface(self):
        """Generate volatility surface."""
        pass
```

#### 2. `pricing/options/merton_jump.py`
Merton jump-diffusion model:
```python
class MertonJumpDiffusion:
    """
    Merton model with jumps in asset price.

    dS = μS dt + σS dW + J dN
    """

    def price(self, option_type='call') -> float:
        """Price using series expansion."""
        pass
```

#### 3. `pricing/options/exotics.py`
Exotic options:
```python
class AsianOption:
    """Arithmetic average Asian option."""
    def price(self) -> float:
        pass

class BarrierOption:
    """Knock-in/knock-out barrier options."""
    def price(self) -> float:
        pass

class LookbackOption:
    """Lookback option (floating strike)."""
    def price(self) -> float:
        pass
```

#### 4. Implied Volatility Surface
```python
def build_volatility_surface(market_prices, strikes, maturities):
    """
    Construct implied volatility surface from market data.

    Returns:
    - IV surface as 2D array
    - Interpolation function
    """
    pass
```

### Week 2 Success Criteria
- [ ] Heston model implemented with characteristic function
- [ ] Merton jump-diffusion working
- [ ] 3+ exotic options priced
- [ ] Volatility surface construction
- [ ] All validated against QuantLib/academic papers
- [ ] Test coverage >85%

### Time Estimate
- Research & learning: 10-12 hours
- Implementation: 10-12 hours
- Testing: 6-8 hours
- **Total**: 26-32 hours

---

## 🗓️ WEEK 3: High-Performance Monte Carlo

### Learning Objectives
- Variance reduction techniques
- Vectorization with NumPy
- Performance profiling
- Numerical optimization

### Deliverables

#### 1. `pricing/monte_carlo/engine.py`
Optimized Monte Carlo engine:
```python
class MonteCarloEngine:
    """
    High-performance Monte Carlo pricer.

    Techniques:
    - Antithetic variates
    - Control variates
    - Importance sampling
    - Quasi-Monte Carlo (Sobol sequences)
    """

    def __init__(self, n_paths, n_steps, variance_reduction='antithetic'):
        pass

    def simulate_gbm(self, S0, mu, sigma, T):
        """Simulate Geometric Brownian Motion paths."""
        pass

    def price_option(self, payoff_func, S0, K, T, r, sigma):
        """Price option using MC simulation."""
        pass

    def price_with_greeks(self, payoff_func, S0, K, T, r, sigma):
        """Price and compute Greeks using pathwise method."""
        pass
```

#### 2. Variance Reduction Implementations

**Antithetic Variates**:
```python
def antithetic_variates(paths):
    """Generate antithetic paths: -Z instead of Z."""
    pass
```

**Control Variates**:
```python
def control_variates(mc_prices, control_prices, control_exact):
    """
    Reduce variance using known pricing formula.

    E.g., use European option as control for Asian option.
    """
    pass
```

**Quasi-Monte Carlo**:
```python
def sobol_sequences(n_paths, n_dims):
    """Generate Sobol low-discrepancy sequences."""
    pass
```

#### 3. Performance Benchmarks

Create `benchmarks/monte_carlo_performance.py`:
```python
def benchmark_monte_carlo():
    """
    Benchmark different configurations.

    Test matrix:
    - Paths: 10k, 100k, 1M, 10M
    - Variance reduction: None, Antithetic, Control, Sobol
    - Vectorization: Loop vs NumPy

    Measure:
    - Time to solution
    - Memory usage
    - Convergence rate
    """
    pass
```

#### 4. Optimization Report

Document in `docs/monte_carlo_optimization.md`:
- Baseline performance (naive implementation)
- Each optimization and speedup achieved
- Final performance vs baseline
- Memory profiling results
- Comparison to analytical solutions

### Week 3 Success Criteria
- [ ] 1M paths in <50ms (vectorized)
- [ ] 10M paths in <500ms
- [ ] Antithetic variates: 2x variance reduction
- [ ] Control variates: additional 2-5x reduction
- [ ] Sobol sequences: faster convergence than pseudo-random
- [ ] Profiling shows >90% time in NumPy (not Python loops)

### Performance Targets

| Paths | Baseline | Optimized | Speedup |
|-------|----------|-----------|---------|
| 10k   | 40ms     | 2ms       | 20x     |
| 100k  | 400ms    | 10ms      | 40x     |
| 1M    | 4000ms   | 50ms      | 80x     |
| 10M   | 40000ms  | 500ms     | 80x     |

### Time Estimate
- Implementation: 8-10 hours
- Optimization & profiling: 10-12 hours
- Benchmarking: 4-6 hours
- Documentation: 2-3 hours
- **Total**: 24-31 hours

---

## 🗓️ WEEK 4: Portfolio Optimization

### Learning Objectives
- Modern portfolio theory (Markowitz)
- Efficient frontier construction
- Constrained optimization
- Risk models (VaR, CVaR)

### Deliverables

#### 1. `optimization/markowitz.py`
Classic mean-variance optimization:
```python
class MarkowitzOptimizer:
    """
    Mean-variance portfolio optimization.

    min: w^T Σ w  (portfolio variance)
    s.t.: w^T μ = μ_target  (target return)
          w^T 1 = 1  (fully invested)
          w_i >= 0  (no short-selling, optional)
    """

    def __init__(self, returns, risk_free_rate=0.02):
        """
        Parameters:
        - returns: Historical returns (n_periods × n_assets)
        - risk_free_rate: Annual risk-free rate
        """
        pass

    def efficient_frontier(self, n_points=100):
        """
        Compute efficient frontier.

        Returns:
        - Array of (risk, return) points
        - Corresponding portfolio weights
        """
        pass

    def max_sharpe_ratio(self):
        """Find portfolio with maximum Sharpe ratio."""
        pass

    def min_variance(self):
        """Find minimum variance portfolio."""
        pass

    def optimize_with_constraints(self, constraints):
        """
        Optimize with custom constraints.

        Constraints can include:
        - Sector limits
        - Turnover constraints
        - Position limits
        """
        pass
```

#### 2. `optimization/black_litterman.py`
Black-Litterman model:
```python
class BlackLitterman:
    """
    Black-Litterman model for combining views with market equilibrium.

    Blends:
    - Market-implied expected returns (from CAPM)
    - Investor views with confidence levels
    """

    def __init__(self, market_caps, cov_matrix, risk_free_rate):
        pass

    def add_view(self, view_vector, view_return, confidence):
        """Add investor view."""
        pass

    def posterior_returns(self):
        """Compute posterior expected returns."""
        pass

    def optimal_weights(self, risk_aversion):
        """Compute optimal portfolio weights."""
        pass
```

#### 3. `optimization/risk_parity.py`
Risk parity portfolio:
```python
class RiskParity:
    """
    Risk parity: allocate based on risk contribution, not weights.

    Each asset contributes equally to portfolio risk.
    """

    def optimize(self, cov_matrix):
        """Find risk parity weights."""
        pass
```

#### 4. `optimization/cvar_optimizer.py`
CVaR (Conditional Value at Risk) optimization:
```python
class CVaROptimizer:
    """
    Minimize CVaR instead of variance.

    Better for tail risk management.
    """

    def optimize(self, returns, alpha=0.95):
        """
        Minimize CVaR at confidence level alpha.

        Returns:
        - Optimal weights
        - Expected CVaR
        """
        pass
```

#### 5. Visualization Dashboard

Create `optimization/visualize.py`:
```python
def plot_efficient_frontier(optimizer):
    """Plot efficient frontier with special portfolios marked."""
    pass

def plot_asset_allocation(weights, asset_names):
    """Pie chart of portfolio allocation."""
    pass

def plot_risk_contribution(weights, cov_matrix):
    """Bar chart of marginal risk contribution."""
    pass

def plot_correlation_matrix(returns):
    """Heatmap of asset correlations."""
    pass
```

### Week 4 Success Criteria
- [ ] Markowitz optimizer working with constraints
- [ ] Black-Litterman implementation
- [ ] Risk parity optimization
- [ ] CVaR optimizer
- [ ] All optimizations validated on real data
- [ ] Efficient frontier plots
- [ ] Handle 100+ asset portfolios in <1 second
- [ ] Test coverage >80%

### Test Portfolio
Use historical data (2010-2023):
- 10 US equities (various sectors)
- 3 bonds (short, medium, long duration)
- 2 commodities (gold, oil)
- 1 crypto (BTC)

Validate:
- Optimal weights sum to 1
- Returns match ex-post performance
- Risk measures accurate
- Constraints satisfied

### Time Estimate
- Learning portfolio theory: 6-8 hours
- Implementation: 12-15 hours
- Testing & validation: 4-6 hours
- Visualization: 3-4 hours
- **Total**: 25-33 hours

---

## 📊 MONTH 1 DELIVERABLES SUMMARY

### Code
```
pricing/
├── options/
│   ├── black_scholes.py       ✅ Week 1
│   ├── heston.py              ✅ Week 2
│   ├── merton_jump.py         ✅ Week 2
│   ├── exotics.py             ✅ Week 2
│   ├── volatility_surface.py  ✅ Week 2
│   └── tests/
│       ├── test_black_scholes.py
│       ├── test_heston.py
│       └── test_exotics.py
│
├── monte_carlo/
│   ├── engine.py              ✅ Week 3
│   ├── variance_reduction.py  ✅ Week 3
│   └── tests/
│       └── test_monte_carlo.py
│
└── docs/
    ├── black_scholes.md
    ├── heston_model.md
    └── monte_carlo_optimization.md

optimization/
├── markowitz.py               ✅ Week 4
├── black_litterman.py         ✅ Week 4
├── risk_parity.py             ✅ Week 4
├── cvar_optimizer.py          ✅ Week 4
├── visualize.py               ✅ Week 4
└── tests/
    ├── test_markowitz.py
    ├── test_black_litterman.py
    └── test_risk_parity.py

benchmarks/
└── monte_carlo_performance.py ✅ Week 3
```

### Documentation
- Mathematical derivations for all models
- Implementation notes
- Validation methodology
- Performance benchmarks
- API documentation

### Tests
- 100+ unit tests
- Integration tests
- Validation against QuantLib
- Performance regression tests
- Test coverage >80%

---

## ✅ MONTH 1 SUCCESS METRICS

### Quantitative
- [ ] Options pricing: <0.01% error vs QuantLib (100+ scenarios)
- [ ] Monte Carlo: 1M paths in <50ms
- [ ] Portfolio optimizer: 100+ assets in <1 second
- [ ] Test coverage: >80%
- [ ] All code type-hinted and documented

### Qualitative
- [ ] Code is readable and maintainable
- [ ] Math is clearly documented
- [ ] Edge cases handled gracefully
- [ ] Performance benchmarks documented
- [ ] Can explain all algorithms in interview

---

## 🚨 RED FLAGS TO WATCH

### If by Week 2 you haven't:
- Implemented Black-Scholes correctly
- Validated against QuantLib
- Written comprehensive tests
→ **Reassess timeline and scope**

### If by Week 4 you haven't:
- Completed all pricing models
- Achieved performance targets
- Built portfolio optimizer
→ **Consider extending Month 1 or simplifying Month 2**

---

## 📚 ADDITIONAL RESOURCES

### Books
- "Numerical Methods in Finance with C++" - Duffy
- "Monte Carlo Methods in Financial Engineering" - Glasserman
- "Quantitative Risk Management" - McNeil, Frey, Embrechts

### Online
- QuantLib documentation (www.quantlib.org)
- Wilmott forums (www.wilmott.com)
- SSRN papers on option pricing

### Validation Data
- QuantLib Python bindings
- Bloomberg Terminal (if available)
- Public option chains (Yahoo Finance, CBOE)

---

## 🎯 WEEK-BY-WEEK CHECKLIST

### Week 1: Black-Scholes ✓
- [ ] Read Hull Ch 1-13
- [ ] Implement Black-Scholes
- [ ] Calculate all Greeks
- [ ] Write 25+ tests
- [ ] Validate vs QuantLib (<0.01% error)
- [ ] Document mathematics

### Week 2: Advanced Models ✓
- [ ] Heston model implemented
- [ ] Merton jump-diffusion
- [ ] 3+ exotic options
- [ ] Volatility surface construction
- [ ] All tests passing
- [ ] Validation complete

### Week 3: Monte Carlo ✓
- [ ] Baseline MC implementation
- [ ] Antithetic variates
- [ ] Control variates
- [ ] Sobol sequences
- [ ] Achieve <50ms for 1M paths
- [ ] Benchmark report written

### Week 4: Portfolio Optimization ✓
- [ ] Markowitz optimizer
- [ ] Black-Litterman model
- [ ] Risk parity
- [ ] CVaR optimization
- [ ] Visualization dashboard
- [ ] Real data validation

---

## 🚀 STARTING MONTH 1

### Day 1 Actions
1. Set up Python environment
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install numpy scipy pandas matplotlib pytest quantlib-python
   ```

2. Create project structure
   ```bash
   mkdir -p pricing/options/tests
   mkdir -p pricing/monte_carlo/tests
   mkdir -p optimization/tests
   mkdir -p benchmarks
   mkdir -p docs
   ```

3. Start reading Hull's book (Ch 1-5)

4. Create first file: `pricing/options/black_scholes.py`

### Daily Commitment
- **Weekdays**: 3-4 hours/day
- **Weekends**: 6-8 hours/day
- **Total**: 20-30 hours/week

### Weekly Check-ins
Every Sunday, review:
- What was completed
- What's blocked
- Adjust next week's plan

---

**Ready to start? Go to Week 1 and begin with Black-Scholes!** 🚀

**Questions or stuck? Document your blockers and research solutions. This is real quant work - it's supposed to be challenging.**
