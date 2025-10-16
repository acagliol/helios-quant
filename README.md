# 🧮 Helios Quant Framework

**A production-grade, multi-language quantitative analytics platform for institutional finance**

[![Go](https://img.shields.io/badge/Go-1.21-00ADD8?logo=go)](https://go.dev/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://www.python.org/)
[![R](https://img.shields.io/badge/R-4.3-276DC3?logo=r)](https://www.r-project.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](https://www.docker.com/)

---

## 🎯 Overview

Helios Quant Framework is a modular quantitative analytics platform combining **Go**, **R**, **Python**, and **SQL** to deliver institutional-grade portfolio analysis, risk modeling, and AI-powered forecasting.

**Key Features:**
- **Go** → High-performance concurrent Monte Carlo simulations (10k+ iterations)
- **R** → Classical quant finance (CAPM, Markowitz optimization, VaR/CVaR)
- **Python** → ML forecasting (Random Forest, XGBoost) + QuantLib integration
- **PostgreSQL** → Normalized analytical data warehouse
- **Next.js** → Modern dashboard with real-time visualizations

---

## 🚀 Quick Start

### Native Setup (Recommended - Lightweight!)

**Space efficient: ~500MB vs ~5GB+ with Docker**

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/helios-quant-framework.git
cd helios-quant-framework

# 2. Run setup script (installs PostgreSQL + Redis)
./scripts/setup-native.sh

# 3. Install dependencies
cd web && npm install && cd ..
cd go && go mod download && cd ..
cd python && pip install -r requirements.txt && cd ..

# 4. Start all services
./scripts/start-dev.sh

# 5. Access the application
# Frontend: http://localhost:3000
# API: http://localhost:8080/api/v1/health
```

### Docker Setup (Optional - if you prefer containers)

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/helios-quant-framework.git
cd helios-quant-framework
cp .env.example .env

# 2. Start Docker daemon (if not running)
sudo systemctl start docker

# 3. Launch all services
docker-compose up -d

# 4. Access the application
# Frontend: http://localhost:3000
# API: http://localhost:8080/api/v1/health
# Grafana: http://localhost:3001 (admin/admin)
```

See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed instructions.

---

## 📂 Project Structure

```
helios-quant-framework/
├── go/              # Go API backend (REST + Monte Carlo)
├── web/             # Next.js frontend dashboard
├── python/          # ML models & QuantLib analytics
├── r/               # R statistical analysis
├── sql/             # PostgreSQL schema & queries
├── docs/            # Documentation
│   ├── PROJECT_OVERVIEW.md
│   ├── IMPLEMENTATION_ROADMAP.md
│   └── archive/
└── docker-compose.yml
```

---

## 🧮 Core Capabilities

| Feature | Language | Description |
|---------|----------|-------------|
| **Monte Carlo Simulation** | Go | Parallel portfolio return simulations |
| **Markowitz Optimization** | R | Efficient frontier & optimal weights |
| **CAPM / Beta Analysis** | R | Systematic risk modeling |
| **VaR / CVaR** | R, Python | Value at Risk calculations |
| **ML Forecasting** | Python | Random Forest/XGBoost IRR prediction |
| **QuantLib Integration** | Python | XIRR, bond pricing, option Greeks |
| **Real-Time Dashboard** | Next.js | Interactive visualizations |

---

## 📊 Example Usage

### Run Monte Carlo Simulation
```bash
curl -X POST http://localhost:8080/api/v1/simulate/montecarlo \
  -H "Content-Type: application/json" \
  -d '{
    "iterations": 10000,
    "mean": 0.12,
    "std_dev": 0.08,
    "jobs": 4
  }'
```

### Run ML Forecasting
```bash
docker-compose exec python-service python ml_forecast.py
```

### Run Portfolio Optimization
```bash
docker-compose exec python-service Rscript r/optimization.R
```

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | Go 1.21, gorilla/mux, lib/pq |
| **Frontend** | Next.js 15, React, TypeScript, Tailwind CSS |
| **Statistics** | R 4.3, quantmod, PerformanceAnalytics, quadprog |
| **ML/AI** | Python 3.11, scikit-learn, XGBoost, QuantLib |
| **Database** | PostgreSQL 15 |
| **Infrastructure** | Docker, Kafka, Redis, Prometheus, Grafana |

---

## 📚 Documentation

- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Setup instructions & troubleshooting
- **[docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md)** - Complete technical documentation
- **[docs/IMPLEMENTATION_ROADMAP.md](docs/IMPLEMENTATION_ROADMAP.md)** - 4-month development plan

---

## 🧪 Development

```bash
# Run tests
cd go && go test -v ./...
cd python && pytest -v
cd web && npm test

# View logs
docker-compose logs -f api
docker-compose logs -f web

# Stop services
docker-compose down
```

---

## 📈 Roadmap

- **Month 1**: Core infrastructure, testing, documentation ✅
- **Month 2**: Ray distributed computing, Kafka pipeline, LSTM models
- **Month 3**: Real-time market data, advanced UI, PDF reports
- **Month 4**: Monitoring, CI/CD, production deployment

See [docs/IMPLEMENTATION_ROADMAP.md](docs/IMPLEMENTATION_ROADMAP.md) for details.

---

## 📝 Resume Summary

**Helios Quant Framework | Go, R, Python (QuantLib, TensorFlow), PostgreSQL, Next.js**

*Built a multi-language quantitative analytics platform with Go-based parallel Monte Carlo simulations (10k+ concurrent iterations), R-based Markowitz portfolio optimization and CAPM analysis, Python ML models (Random Forest, XGBoost) for IRR forecasting, and QuantLib integration for XIRR and option pricing. Designed PostgreSQL analytical warehouse with 9 normalized tables. Implemented Next.js dashboard with real-time visualizations.*

---

## 📄 License

MIT License

---

*Built with precision, performance, and quantitative rigor. 🚀📊*
