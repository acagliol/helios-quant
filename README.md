# 🧮 Helios Quant Framework

**A multi-language quantitative analytics and AI forecasting engine for private equity and investment analysis**

[![Go](https://img.shields.io/badge/Go-1.21-00ADD8?logo=go)](https://go.dev/)
[![R](https://img.shields.io/badge/R-4.3-276DC3?logo=r)](https://www.r-project.org/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)](https://www.postgresql.org/)

---

## 🎯 Overview

Helios Quant Framework is a modular quantitative analytics platform that combines **Go**, **R**, **Python**, and **SQL** to deliver institutional-grade portfolio analysis, risk modeling, and AI-powered forecasting. Built for private equity funds, hedge funds, and quantitative researchers, it demonstrates mastery of:

- **Go** → High-performance concurrent computing and API infrastructure
- **R** → Classical quantitative finance (CAPM, portfolio optimization, risk metrics)
- **Python** → Machine learning forecasting and QuantLib financial modeling
- **PostgreSQL** → Centralized analytical data warehouse

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│                    HELIOS FRAMEWORK                  │
│------------------------------------------------------│
│ Go (Backend Engine)                                  │
│ - REST/gRPC API endpoints                            │
│ - Parallel Monte Carlo simulations                   │
│ - Data ingestion & orchestration                     │
│------------------------------------------------------│
│ R (Statistical Core)                                 │
│ - Regression models (OLS, CAPM, ARIMA)               │
│ - Markowitz portfolio optimization                   │
│ - Risk decomposition (VaR, CVaR, Beta, Sharpe)       │
│------------------------------------------------------│
│ Python (AI/ML & Finance Layer)                       │
│ - ML models: Random Forest, XGBoost, TensorFlow      │
│ - QuantLib: IRR, NPV, bond pricing, option Greeks    │
│ - Matplotlib/Seaborn visualizations                  │
│------------------------------------------------------│
│ SQL (PostgreSQL)                                     │
│ - Portfolio performance data                         │
│ - Cash flows, market data, risk metrics              │
│ - ML predictions & simulation results                │
└──────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
helios-quant-framework/
├── go/
│   ├── main.go                 # API server and orchestration
│   ├── montecarlo/
│   │   └── simulator.go        # Parallel Monte Carlo simulations
│   ├── datafetch/              # Market data ingestion (placeholder)
│   └── go.mod
├── r/
│   ├── portfolio_analysis.R    # Sharpe, Sortino, CAPM, Alpha/Beta
│   ├── risk_models.R           # VaR, CVaR, max drawdown
│   └── optimization.R          # Markowitz, efficient frontier
├── python/
│   ├── ml_forecast.py          # Random Forest / XGBoost IRR forecasting
│   ├── quantlib_models.py      # QuantLib: XIRR, bond metrics, option Greeks
│   ├── requirements.txt
│   └── output/                 # Generated plots and results
├── sql/
│   ├── schema.sql              # PostgreSQL database schema
│   └── queries/
│       └── common_queries.sql  # Analytical SQL queries
├── docs/                       # Additional documentation
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Go** 1.21+
- **R** 4.3+ with packages: `quantmod`, `PerformanceAnalytics`, `ggplot2`, `quadprog`, `DBI`, `RPostgres`
- **Python** 3.11+ with libraries: `numpy`, `pandas`, `scikit-learn`, `QuantLib`, `matplotlib`, `psycopg2`
- **PostgreSQL** 15+

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/helios-quant-framework.git
   cd helios-quant-framework
   ```

2. **Set up PostgreSQL database**
   ```bash
   psql -U postgres -c "CREATE DATABASE helios_quant;"
   psql -U postgres -d helios_quant -f sql/schema.sql
   ```

3. **Install Go dependencies**
   ```bash
   cd go
   go mod download
   ```

4. **Install R packages**
   ```R
   install.packages(c("quantmod", "PerformanceAnalytics", "ggplot2", "quadprog", "DBI", "RPostgres", "jsonlite", "MASS", "moments"))
   ```

5. **Install Python dependencies**
   ```bash
   cd python
   pip install -r requirements.txt
   ```

6. **Configure environment variables**
   ```bash
   export DATABASE_URL="postgres://localhost/helios_quant?sslmode=disable"
   export PORT=8080
   ```

---

## 💻 Usage

### 1. Start the Go API Server

```bash
cd go
go run main.go montecarlo/simulator.go
```

The API will be available at `http://localhost:8080`

**Available Endpoints:**
- `GET /api/v1/health` - Health check
- `GET /api/v1/portfolio` - Get portfolio data
- `POST /api/v1/simulate/montecarlo` - Run Monte Carlo simulation
- `POST /api/v1/analytics/trigger` - Trigger R/Python analytics

### 2. Run R Statistical Analysis

```bash
cd r
Rscript portfolio_analysis.R
Rscript risk_models.R
Rscript optimization.R
```

**Outputs:**
- `r/output/portfolio_metrics.json` - Portfolio performance metrics
- `r/output/risk_metrics.json` - Risk analysis results
- `r/output/efficient_frontier.png` - Markowitz efficient frontier plot
- `r/output/optimization_results.json` - Optimal portfolio weights

### 3. Run Python ML Forecasting

```bash
cd python
python ml_forecast.py
python quantlib_models.py
```

**Outputs:**
- `python/output/ml_forecast_results.json` - ML model metrics (RMSE, R², MAE)
- `python/output/ml_forecast_plots.png` - Visualization of predictions
- `python/output/quantlib_results.json` - XIRR, bond pricing, option Greeks

### 4. Query SQL Database

```bash
psql -U postgres -d helios_quant -f sql/queries/common_queries.sql
```

---

## 🧮 Core Quantitative Models

| Model | Language | Description |
|-------|----------|-------------|
| **Monte Carlo Simulation** | Go | Parallel portfolio return simulation using goroutines |
| **CAPM / Beta Regression** | R | Capital Asset Pricing Model and systematic risk |
| **Markowitz Optimization** | R | Mean-variance optimization and efficient frontier |
| **Value at Risk (VaR)** | R, Python | Parametric and historical VaR calculations |
| **Random Forest Forecasting** | Python | ML-based IRR prediction using `scikit-learn` |
| **QuantLib XIRR** | Python | Exact IRR calculation for irregular cash flows |
| **Bond Pricing & Duration** | Python | Fixed income analytics using QuantLib |
| **Black-Scholes Greeks** | Python | Option pricing and risk sensitivity metrics |

---

## 📊 Example Outputs

### Monte Carlo Simulation (Go)
```json
{
  "mean": 0.1245,
  "std_dev": 0.0823,
  "percentile": [0.0312, 0.0685, 0.1205, 0.1782, 0.2451],
  "iterations": 10000
}
```

### Portfolio Optimization (R)
```json
{
  "max_sharpe_portfolio": {
    "weights": {"Asset_1": 0.25, "Asset_2": 0.30, "Asset_3": 0.20, "Asset_4": 0.15, "Asset_5": 0.10},
    "expected_return": 0.0952,
    "volatility": 0.1834,
    "sharpe_ratio": 0.4138
  }
}
```

### ML Forecasting (Python)
```json
{
  "rmse": 0.0234,
  "mae": 0.0189,
  "r2_score": 0.8756,
  "cv_r2_mean": 0.8432,
  "cv_r2_std": 0.0321
}
```

---

## 🔬 Technical Highlights

### Go: Concurrent Monte Carlo Simulations
```go
func runMonteCarloSimulation(iterations int, mean, stdDev float64, jobs int) SimulationResult {
    results := make([]float64, iterations)
    var wg sync.WaitGroup

    for i := 0; i < jobs; i++ {
        wg.Add(1)
        go func(start, end int) {
            defer wg.Done()
            for j := start; j < end; j++ {
                results[j] = simulatePortfolioReturn(mean, stdDev, rng)
            }
        }(start, end)
    }
    wg.Wait()
    return calculateStatistics(results)
}
```

### R: Markowitz Portfolio Optimization
```r
markowitz_optimization <- function(expected_returns, cov_matrix, target_return) {
    Dmat <- 2 * cov_matrix
    dvec <- rep(0, n_assets)
    Amat <- cbind(rep(1, n_assets), expected_returns, diag(n_assets))
    bvec <- c(1, target_return, rep(0, n_assets))
    result <- solve.QP(Dmat, dvec, Amat, bvec, meq = 2)
    return(result$solution)
}
```

### Python: ML Forecasting with Feature Engineering
```python
class PortfolioMLForecaster:
    def prepare_features(self, df):
        df['vintage_age'] = 2025 - df['vintage']
        df['sharpe_proxy'] = df['irr'] / df['volatility']
        sector_dummies = pd.get_dummies(df['sector'], prefix='sector')
        X = pd.concat([df[base_features], sector_dummies], axis=1)
        return X, df['irr']
```

### Python: QuantLib XIRR Calculation
```python
def calculate_xirr(self, cash_flows: List[Tuple[datetime, float]]) -> float:
    dates = [ql.Date(cf[0].day, cf[0].month, cf[0].year) for cf in cash_flows]
    amounts = [cf[1] for cf in cash_flows]
    irr = ql.CashFlows.irr(
        [ql.SimpleCashFlow(amt, date) for amt, date in zip(amounts, dates)],
        self.day_count, ql.Compounded, ql.Annual
    )
    return irr
```

---

## 🧪 Data Pipeline Flow

```
1. PostgreSQL stores portfolio & market data
           ↓
2. Go API fetches data and orchestrates jobs
           ↓
3. R performs statistical analysis → exports JSON
           ↓
4. Python runs ML models & QuantLib → exports JSON + plots
           ↓
5. Results stored back in PostgreSQL
           ↓
6. Matplotlib/ggplot2 generate investor-grade visualizations
```

---

## 📈 Future Enhancements

| Feature | Language | Description |
|---------|----------|-------------|
| **Risk Attribution Engine** | R | Decompose portfolio risk by sector/geography |
| **Parallel Backtesting** | Go | Run 10k+ strategy simulations concurrently |
| **gRPC Inter-Service Communication** | Go | Replace REST with gRPC for R/Python calls |
| **LSTM Time Series Forecasting** | Python + TensorFlow | Deep learning for NAV prediction |
| **Real-Time Market Data** | Go | WebSocket integration with Bloomberg/Reuters |
| **LLM Report Generation** | Python | AI-generated investor summaries using GPT-4 |

---

## 📝 Resume Summary

**Helios Quant Framework | Go, R, Python (QuantLib, TensorFlow), PostgreSQL, Matplotlib**

*Built a multi-language quantitative analytics platform integrating Go-based parallel Monte Carlo simulations (10k+ concurrent iterations), R-based Markowitz portfolio optimization and CAPM analysis, and Python machine learning models (Random Forest, XGBoost) for IRR forecasting. Implemented QuantLib integration for XIRR, bond pricing, and option Greeks calculations. Designed PostgreSQL analytical warehouse with 9 normalized tables supporting time-series queries, risk decomposition, and cross-language data interchange via JSON/REST APIs. Generated institutional-grade visualizations using Matplotlib and ggplot2.*

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Go 1.21, gorilla/mux, lib/pq |
| **Statistics** | R 4.3, quantmod, PerformanceAnalytics, quadprog |
| **ML/AI** | Python 3.11, scikit-learn, XGBoost, TensorFlow, QuantLib |
| **Database** | PostgreSQL 15, SQL views & triggers |
| **Visualization** | Matplotlib, Seaborn, ggplot2 |
| **Deployment** | Docker (future), systemd, cron jobs |

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

Inspired by quantitative frameworks used at:
- **BlackRock** (Aladdin platform)
- **Two Sigma** (multi-language quant research)
- **Citadel** (high-performance risk systems)
- **QuantLib** (open-source financial modeling)

---

## 📧 Contact

**Project Lead:** Your Name
**GitHub:** [@yourusername](https://github.com/yourusername)
**LinkedIn:** [linkedin.com/in/yourprofile](https://linkedin.com/in/yourprofile)

---

*Built with precision, performance, and quantitative rigor. 🚀📊*
