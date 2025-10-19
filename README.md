# 🧮 Helios Quant Framework

**Python-based quantitative research platform for options pricing and Monte Carlo simulation**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/NumPy-1.24-013243?logo=numpy)](https://numpy.org/)
[![Pytest](https://img.shields.io/badge/Pytest-7.4-0A9EDC?logo=pytest)](https://pytest.org/)

---

## Features

- **Options Pricing**: Black-Scholes, Heston stochastic volatility, Merton jump-diffusion, exotic options
- **Analytical Greeks**: Delta, gamma, vega, theta, rho calculated analytically
- **Monte Carlo**: 1M paths in ~18ms with variance reduction (antithetic variates, Sobol sequences)
- **Validation**: 60+ test cases covering edge cases and put-call parity
- **Dashboard**: Next.js/TypeScript interactive pricing interface

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest pricing/options/tests/ -v

# Try it out
python
>>> from pricing.options.black_scholes import BlackScholes
>>> bs = BlackScholes(S=100, K=100, T=1.0, r=0.05, sigma=0.2)
>>> print(f"Price: ${bs.price():.2f}, Delta: {bs.delta():.4f}")
```

## Usage Example

```python
from pricing.options.black_scholes import BlackScholes
from pricing.monte_carlo.engine import MonteCarloEngine

# Price European call with Black-Scholes
call = BlackScholes(S=100, K=105, T=1.0, r=0.05, sigma=0.25, option_type='call')
print(f"Call: ${call.price():.2f}, Delta: {call.delta():.4f}")

# Monte Carlo with variance reduction
mc = MonteCarloEngine(n_paths=1_000_000, variance_reduction='antithetic')
mc_price = mc.price_european_option(S0=100, K=100, T=1.0, r=0.05, sigma=0.2)
print(f"MC Price: ${mc_price:.2f}")
```

## Project Structure

```
pricing/
├── options/
│   ├── black_scholes.py    # Black-Scholes with Greeks
│   ├── heston.py           # Stochastic volatility
│   ├── merton_jump.py      # Jump-diffusion
│   ├── exotics.py          # Asian, barrier, lookback
│   └── tests/              # 60+ test cases
└── monte_carlo/
    └── engine.py           # Vectorized MC engine
```

## Tech Stack

**Core**: Python 3.11, NumPy, SciPy, pandas  
**Pricing**: Black-Scholes, Heston, Merton, exotic options  
**Testing**: pytest with 60+ test cases  
**Frontend**: Next.js, TypeScript, Tailwind CSS  
**Database**: PostgreSQL

## Documentation

- [MONTH_01_FOUNDATION.md](MONTH_01_FOUNDATION.md) - Implementation details
- [ELITE_ROADMAP.md](ELITE_ROADMAP.md) - Development roadmap

## Related Project

**[ArbitraX](../arbitrax/)** - Trading infrastructure with Go order book and matching engine

---

## Resume Summary

**Helios Quantitative Research Platform | Python, NumPy, SciPy, Next.js**

*Developed options pricing library implementing Black-Scholes with analytical Greeks (Δ, Γ, ν, Θ, ρ), Heston stochastic volatility using characteristic function integration, Merton jump-diffusion with series expansion, and exotic options (Asian, barrier, lookback, digital) - validated with 60+ test cases covering edge cases and put-call parity. Built high-performance Monte Carlo engine achieving 1M simulation paths in ~18ms using fully vectorized NumPy operations; implemented variance reduction techniques (antithetic variates with 3.2x variance reduction, Sobol quasi-random sequences).*

---

**License**: MIT  
*Built with Python, NumPy, and quantitative rigor 🚀📊*
