# Helios Quant

Python-based quantitative research platform for options pricing and Monte Carlo simulation.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org/)

## Features

- **Options Pricing** – Black-Scholes, Heston, Merton jump-diffusion, exotic options
- **Greeks** – Analytical delta, gamma, vega, theta, rho
- **Monte Carlo** – Vectorized engine with variance reduction techniques
- **Testing** – 60+ test cases with put-call parity validation

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Test
pytest pricing/options/tests/ -v
```

## Usage

```python
from pricing.options.black_scholes import BlackScholes

# Price a call option
option = BlackScholes(S=100, K=105, T=1.0, r=0.05, sigma=0.25, option_type='call')
print(f"Price: ${option.price():.2f}")
print(f"Delta: {option.delta():.4f}")
```

```python
from pricing.monte_carlo.engine import MonteCarloEngine

# Monte Carlo pricing with variance reduction
mc = MonteCarloEngine(n_paths=1_000_000, variance_reduction='antithetic')
price = mc.price_european_option(S0=100, K=100, T=1.0, r=0.05, sigma=0.2)
print(f"Price: ${price:.2f}")
```

## Project Structure

```
pricing/
├── options/
│   ├── black_scholes.py
│   ├── heston.py
│   ├── merton_jump.py
│   ├── exotics.py
│   └── tests/
└── monte_carlo/
    └── engine.py
```

## Tech Stack

- **Backend**: Python 3.11, NumPy, SciPy, pandas
- **Testing**: pytest
- **Frontend**: Next.js, TypeScript, Tailwind CSS

## License

MIT
