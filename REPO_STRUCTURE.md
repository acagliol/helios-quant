# Repository Structure Reorganization

## 🎯 Goal
Transform the repository into a clean, maintainable, production-grade structure following industry best practices.

## 📁 New Structure

```
helios-quant-framework/
│
├── .github/                          # GitHub specific files
│   ├── workflows/                    # CI/CD pipelines
│   │   ├── ci.yml                   # Main CI pipeline
│   │   ├── deploy-frontend.yml      # Frontend deployment
│   │   └── deploy-backend.yml       # Backend deployment
│   ├── ISSUE_TEMPLATE/              # Issue templates
│   ├── PULL_REQUEST_TEMPLATE.md     # PR template
│   └── dependabot.yml               # Dependency updates
│
├── docs/                             # Documentation
│   ├── architecture/
│   │   ├── SYSTEM_DESIGN.md
│   │   ├── DATA_FLOW.md
│   │   └── diagrams/
│   ├── api/
│   │   ├── API_REFERENCE.md
│   │   └── WEBSOCKET_API.md
│   ├── deployment/
│   │   ├── DOCKER.md
│   │   ├── KUBERNETES.md
│   │   └── AWS_DEPLOYMENT.md
│   └── guides/
│       ├── DEVELOPMENT.md
│       ├── TESTING.md
│       └── MONITORING.md
│
├── services/                         # Microservices (organized by domain)
│   │
│   ├── api/                         # Go Backend API
│   │   ├── cmd/                     # Application entry points
│   │   │   └── server/
│   │   │       └── main.go
│   │   ├── internal/                # Private application code
│   │   │   ├── config/              # Configuration
│   │   │   ├── models/              # Data models
│   │   │   ├── handlers/            # HTTP handlers
│   │   │   ├── middleware/          # HTTP middleware
│   │   │   ├── services/            # Business logic
│   │   │   │   ├── montecarlo/
│   │   │   │   ├── portfolio/
│   │   │   │   └── analytics/
│   │   │   ├── repository/          # Data access layer
│   │   │   └── utils/               # Utilities
│   │   ├── pkg/                     # Public reusable packages
│   │   │   ├── validator/
│   │   │   ├── logger/
│   │   │   └── cache/
│   │   ├── tests/                   # Integration tests
│   │   ├── Dockerfile
│   │   ├── go.mod
│   │   ├── go.sum
│   │   └── README.md
│   │
│   ├── analytics/                   # Python Analytics Service
│   │   ├── src/
│   │   │   ├── ml/                  # Machine Learning
│   │   │   │   ├── models/
│   │   │   │   │   ├── random_forest.py
│   │   │   │   │   ├── lstm.py
│   │   │   │   │   └── xgboost_model.py
│   │   │   │   ├── forecaster.py
│   │   │   │   ├── explainer.py    # SHAP
│   │   │   │   └── preprocessor.py
│   │   │   ├── quant/               # QuantLib calculations
│   │   │   │   ├── bond_pricing.py
│   │   │   │   ├── option_pricing.py
│   │   │   │   ├── irr_calculator.py
│   │   │   │   └── npv_calculator.py
│   │   │   ├── distributed/         # Ray-based distributed computing
│   │   │   │   ├── ray_monte_carlo.py
│   │   │   │   └── ray_cluster.py
│   │   │   ├── market_data/         # External API integrations
│   │   │   │   ├── alpha_vantage.py
│   │   │   │   ├── polygon_client.py
│   │   │   │   └── coingecko.py
│   │   │   ├── messaging/           # Kafka consumers
│   │   │   │   ├── kafka_consumer.py
│   │   │   │   └── event_handlers.py
│   │   │   ├── config/
│   │   │   └── utils/
│   │   ├── tests/
│   │   │   ├── test_ml/
│   │   │   ├── test_quant/
│   │   │   └── test_distributed/
│   │   ├── scripts/                 # Utility scripts
│   │   │   ├── seed_data.py
│   │   │   └── migrate_data.py
│   │   ├── requirements/
│   │   │   ├── base.txt
│   │   │   ├── dev.txt
│   │   │   └── prod.txt
│   │   ├── Dockerfile
│   │   ├── setup.py
│   │   └── README.md
│   │
│   ├── statistical/                 # R Statistical Service
│   │   ├── src/
│   │   │   ├── portfolio/
│   │   │   │   ├── analysis.R
│   │   │   │   └── metrics.R
│   │   │   ├── optimization/
│   │   │   │   ├── markowitz.R
│   │   │   │   ├── nsga2.R
│   │   │   │   └── cvxpy_wrapper.R
│   │   │   ├── risk/
│   │   │   │   ├── var_cvar.R
│   │   │   │   ├── drawdown.R
│   │   │   │   └── stress_test.R
│   │   │   ├── utils/
│   │   │   └── config.R
│   │   ├── tests/
│   │   ├── output/                  # Generated plots/results
│   │   ├── Dockerfile
│   │   ├── renv.lock               # R dependency lock
│   │   └── README.md
│   │
│   └── web/                         # Next.js Frontend
│       ├── src/
│       │   ├── app/                 # App router (Next.js 15)
│       │   │   ├── (dashboard)/     # Dashboard layout group
│       │   │   │   ├── page.tsx
│       │   │   │   └── layout.tsx
│       │   │   ├── portfolio/
│       │   │   │   ├── page.tsx
│       │   │   │   └── [id]/
│       │   │   ├── market-data/     # New: Real-time market data
│       │   │   ├── analytics/       # New: Advanced analytics
│       │   │   ├── reports/         # New: PDF reports
│       │   │   ├── api/             # API routes
│       │   │   ├── layout.tsx
│       │   │   └── globals.css
│       │   ├── components/          # Reusable components
│       │   │   ├── ui/              # Base UI components
│       │   │   │   ├── Button.tsx
│       │   │   │   ├── Card.tsx
│       │   │   │   ├── Input.tsx
│       │   │   │   └── Modal.tsx
│       │   │   ├── charts/          # Chart components
│       │   │   │   ├── LineChart.tsx
│       │   │   │   ├── BarChart.tsx
│       │   │   │   └── PieChart.tsx
│       │   │   ├── dashboard/       # Dashboard-specific
│       │   │   │   ├── StatsCard.tsx
│       │   │   │   ├── MonteCarloPanel.tsx
│       │   │   │   └── PerformanceChart.tsx
│       │   │   ├── portfolio/       # Portfolio-specific
│       │   │   │   ├── FundTable.tsx
│       │   │   │   ├── FundForm.tsx
│       │   │   │   └── FundDetails.tsx
│       │   │   └── layout/          # Layout components
│       │   │       ├── Header.tsx
│       │   │       ├── Sidebar.tsx
│       │   │       └── Footer.tsx
│       │   ├── lib/                 # Utilities and helpers
│       │   │   ├── api/             # API client
│       │   │   │   ├── client.ts
│       │   │   │   ├── endpoints.ts
│       │   │   │   └── websocket.ts
│       │   │   ├── hooks/           # Custom React hooks
│       │   │   │   ├── usePortfolio.ts
│       │   │   │   ├── useSimulation.ts
│       │   │   │   └── useMarketData.ts
│       │   │   ├── utils/
│       │   │   │   ├── formatters.ts
│       │   │   │   ├── validators.ts
│       │   │   │   └── calculations.ts
│       │   │   └── types/           # TypeScript types
│       │   │       ├── fund.ts
│       │   │       ├── simulation.ts
│       │   │       └── api.ts
│       │   └── styles/              # Global styles
│       ├── public/                  # Static assets
│       │   ├── images/
│       │   └── icons/
│       ├── tests/
│       │   ├── unit/
│       │   ├── integration/
│       │   └── e2e/
│       ├── Dockerfile
│       ├── next.config.ts
│       ├── tailwind.config.ts
│       ├── tsconfig.json
│       ├── package.json
│       └── README.md
│
├── infrastructure/                   # Infrastructure as Code
│   ├── docker/                      # Docker configurations
│   │   ├── docker-compose.yml
│   │   ├── docker-compose.dev.yml
│   │   └── docker-compose.prod.yml
│   ├── kubernetes/                  # K8s manifests
│   │   ├── base/
│   │   ├── overlays/
│   │   │   ├── development/
│   │   │   ├── staging/
│   │   │   └── production/
│   │   └── helm/                    # Helm charts
│   ├── terraform/                   # Terraform for AWS/GCP
│   └── monitoring/
│       ├── prometheus/
│       │   └── prometheus.yml
│       └── grafana/
│           └── dashboards/
│
├── database/                         # Database related
│   ├── migrations/                  # SQL migrations
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_add_market_data.sql
│   │   └── 003_add_ml_predictions.sql
│   ├── seeds/                       # Seed data
│   │   ├── funds.sql
│   │   └── cash_flows.sql
│   └── queries/                     # Common queries
│       └── analytics_queries.sql
│
├── scripts/                          # Utility scripts
│   ├── setup/
│   │   ├── setup_dev.sh
│   │   └── install_dependencies.sh
│   ├── deploy/
│   │   ├── deploy_to_vercel.sh
│   │   └── deploy_to_heroku.sh
│   ├── data/
│   │   ├── generate_test_data.py
│   │   └── backup_database.sh
│   └── utils/
│       └── cleanup.sh
│
├── config/                           # Configuration files
│   ├── development.env
│   ├── staging.env
│   └── production.env
│
├── tests/                            # End-to-end tests
│   └── e2e/
│       ├── api/
│       └── ui/
│
├── .github/                          # Already covered above
├── .vscode/                         # VS Code settings
│   └── settings.json
├── .gitignore
├── .dockerignore
├── .env.example
├── docker-compose.yml               # Main compose file
├── README.md                        # Main README
├── CONTRIBUTING.md                  # Contribution guide
├── LICENSE                          # MIT License
├── CHANGELOG.md                     # Version history
├── CODE_OF_CONDUCT.md              # Community guidelines
│
└── docs/ (detailed)                 # Already covered above
```

---

## 🔄 Migration Steps

### Phase 1: Backend Reorganization (Go)

**From:**
```
go/
├── main.go
├── montecarlo/
│   └── simulator.go
├── go.mod
└── go.sum
```

**To:**
```
services/api/
├── cmd/server/main.go
├── internal/
│   ├── handlers/
│   ├── services/montecarlo/
│   ├── models/
│   └── repository/
├── pkg/
├── tests/
├── go.mod
└── Dockerfile
```

### Phase 2: Python Reorganization

**From:**
```
python/
├── ml_forecast.py
├── quantlib_models.py
└── output/
```

**To:**
```
services/analytics/
├── src/
│   ├── ml/models/
│   ├── quant/
│   ├── distributed/
│   └── market_data/
├── tests/
├── scripts/
└── requirements/
```

### Phase 3: Frontend Reorganization

**From:**
```
web/
├── app/
│   ├── page.tsx
│   ├── portfolio/page.tsx
│   └── layout.tsx
└── package.json
```

**To:**
```
services/web/
├── src/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── styles/
├── public/
├── tests/
└── package.json
```

---

## 🎯 Benefits

### 1. **Clear Separation of Concerns**
- Each service is self-contained
- Easy to understand and navigate
- Reduces coupling between components

### 2. **Scalability**
- Add new services without touching existing code
- Microservices-ready architecture
- Easy to deploy independently

### 3. **Maintainability**
- Clear folder structure
- Easy to find code
- Consistent organization across services

### 4. **Testing**
- Tests colocated with code
- Easy to run tests for specific services
- Clear test structure (unit/integration/e2e)

### 5. **Developer Experience**
- Intuitive structure
- Easy onboarding
- IDE-friendly (better autocomplete, navigation)

### 6. **Production-Ready**
- Infrastructure as Code
- CI/CD friendly
- Environment-specific configs

---

## 📝 Implementation Checklist

- [ ] Create new directory structure
- [ ] Move Go files to services/api
- [ ] Move Python files to services/analytics
- [ ] Move R files to services/statistical
- [ ] Move web files to services/web
- [ ] Update import paths
- [ ] Update Dockerfiles
- [ ] Update docker-compose.yml
- [ ] Update documentation
- [ ] Test all services
- [ ] Update CI/CD pipelines

---

## ⚠️ Notes

- Keep backward compatibility during migration
- Test thoroughly after each phase
- Update documentation as you go
- Use git branches for large refactors
- Keep old structure until new one is tested

---

**Status:** Ready to implement
**Estimated Time:** 2-3 hours
**Priority:** High (improves all future development)
