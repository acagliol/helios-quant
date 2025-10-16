# Getting Started with Helios Quant Framework

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- **Native Setup (Recommended)**: Go 1.21+, Node.js 20+, Python 3.11+
- OR **Docker** & **Docker Compose** (uses more disk space)

### Option 1: Native Setup (Recommended - Lightweight!)

**Why Native?** Uses ~500MB instead of ~5GB+ with Docker. Faster startup times.

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/helios-quant-framework.git
   cd helios-quant-framework
   ```

2. **Run the setup script**
   ```bash
   chmod +x scripts/setup-native.sh
   ./scripts/setup-native.sh
   ```
   This will:
   - Install PostgreSQL and Redis
   - Create the database and user
   - Load the schema

3. **Copy environment variables**
   ```bash
   cp .env.example .env
   # Edit .env to add your API keys (optional for basic functionality)
   ```

4. **Install application dependencies**
   ```bash
   # Frontend
   cd web && npm install && cd ..

   # Go backend
   cd go && go mod download && cd ..

   # Python (optional)
   cd python && pip install -r requirements.txt && cd ..
   ```

5. **Start all services**
   ```bash
   ./scripts/start-dev.sh
   ```

6. **Access the application**
   - **Frontend**: http://localhost:3000
   - **API**: http://localhost:8080
   - **API Health**: http://localhost:8080/api/v1/health

7. **View logs**
   ```bash
   tail -f logs/api.log
   tail -f logs/web.log
   ```

8. **Stop services**
   ```bash
   ./scripts/stop-dev.sh
   ```

---

### Option 2: Docker Setup (Uses more disk space)

#### Step 1: Install Dependencies

**Go Backend:**
```bash
cd go
go mod download
```

**Python Analytics:**
```bash
cd python
pip install -r requirements.txt
```

**R Analytics:**
```r
install.packages(c(
  "quantmod", "PerformanceAnalytics", "ggplot2",
  "quadprog", "DBI", "RPostgres", "jsonlite", "MASS", "moments"
))
```

**Frontend:**
```bash
cd web
npm install
```

#### Step 2: Setup PostgreSQL

```bash
# Create database
createdb helios_quant

# Run schema
psql -d helios_quant -f sql/schema.sql
```

#### Step 3: Start Services

**Terminal 1 - Go API:**
```bash
cd go
export DATABASE_URL="postgres://localhost/helios_quant?sslmode=disable"
export PORT=8080
go run main.go
```

**Terminal 2 - Frontend:**
```bash
cd web
npm run dev
```

**Terminal 3 - Python Service (optional):**
```bash
cd python
python kafka_consumer.py
```

---

## 📚 Project Structure

```
helios-quant-framework/
├── go/                          # Go backend API
│   ├── main.go                  # API server and Monte Carlo engine
│   ├── go.mod                   # Go dependencies
│   └── Dockerfile               # Docker build for Go service
│
├── web/                         # Next.js frontend
│   ├── app/
│   │   ├── page.tsx             # Main dashboard
│   │   ├── portfolio/page.tsx   # Portfolio management
│   │   └── layout.tsx           # Root layout
│   ├── package.json
│   └── Dockerfile
│
├── python/                      # Python analytics
│   ├── ml_forecast.py           # ML forecasting
│   ├── quantlib_models.py       # QuantLib calculations
│   ├── distributed_sim.py       # Ray-based simulations (Month 2)
│   ├── kafka_consumer.py        # Kafka event consumer (Month 2)
│   ├── requirements.txt
│   └── Dockerfile
│
├── r/                           # R statistical analysis
│   ├── portfolio_analysis.R     # Portfolio metrics
│   ├── optimization.R           # Markowitz optimization
│   └── risk_models.R            # VaR/CVaR
│
├── sql/                         # Database
│   ├── schema.sql               # Database schema
│   └── queries/
│       └── common_queries.sql
│
├── monitoring/                  # Observability (Month 4)
│   ├── prometheus.yml
│   └── grafana/
│
├── scripts/                     # Utility scripts
│   └── seed_data.py             # Generate demo data
│
├── docs/                        # Documentation
│   ├── API.md
│   └── ARCHITECTURE.md
│
├── .github/                     # CI/CD (Month 4)
│   └── workflows/
│       └── ci.yml
│
├── docker-compose.yml           # Multi-service orchestration
├── .env.example                 # Environment template
├── .dockerignore
├── README.md
├── PROJECT_OVERVIEW.md          # Comprehensive project docs
├── IMPLEMENTATION_ROADMAP.md    # 4-month improvement plan
└── GETTING_STARTED.md           # This file
```

---

## 🧪 Running Tests

### Go Tests
```bash
cd go
go test -v -cover ./...
```

### Python Tests
```bash
cd python
pytest -v --cov=.
```

### Frontend Tests
```bash
cd web
npm test
```

### Run All Tests
```bash
# If using Docker Compose
docker-compose exec api go test -v ./...
docker-compose exec python-service pytest
docker-compose exec web npm test
```

---

## 🔧 Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Edit code in your IDE
- Hot reload works for Next.js and Go (with `air`)

### 3. Test Your Changes
```bash
# Run specific service tests
cd go && go test -v ./...
cd python && pytest
cd web && npm test
```

### 4. Commit with Conventional Commits
```bash
git add .
git commit -m "feat: add distributed Monte Carlo simulation"
# Or: fix:, docs:, style:, refactor:, test:, chore:
```

### 5. Push and Create PR
```bash
git push origin feature/your-feature-name
# Create pull request on GitHub
```

---

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### Port Already in Use
```bash
# Find process using port 8080
lsof -i :8080
# Or
sudo netstat -tulpn | grep :8080

# Kill process
kill -9 <PID>
```

### Node Modules Issues
```bash
cd web
rm -rf node_modules package-lock.json
npm install
```

### Go Module Issues
```bash
cd go
go clean -modcache
go mod download
```

### Docker Issues
```bash
# Rebuild containers
docker-compose build --no-cache

# Remove all containers and volumes
docker-compose down -v

# Prune unused Docker resources
docker system prune -a
```

---

## 📊 Monitoring and Debugging

### View API Logs
```bash
docker-compose logs -f api
```

### View Database Queries
```bash
docker-compose exec postgres psql -U helios -d helios_quant

# Inside psql:
SELECT * FROM portfolio_data LIMIT 10;
\q
```

### Check Redis Cache
```bash
docker-compose exec redis redis-cli

# Inside redis-cli:
KEYS *
GET portfolio:1
```

### Monitor Kafka Topics
```bash
docker-compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9093 \
  --topic portfolio_updates \
  --from-beginning
```

---

## 🌐 Accessing Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | N/A |
| **API** | http://localhost:8080 | N/A |
| **API Health** | http://localhost:8080/api/v1/health | N/A |
| **Grafana** | http://localhost:3001 | admin/admin |
| **Prometheus** | http://localhost:9090 | N/A |
| **PostgreSQL** | localhost:5432 | helios/helios_dev_password |
| **Redis** | localhost:6379 | No password |
| **Kafka** | localhost:9092 | N/A |

---

## 📝 Common Tasks

### Seed Database with Demo Data
```bash
docker-compose exec python-service python scripts/seed_data.py
```

### Run Monte Carlo Simulation (10k iterations)
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

### Get Portfolio Data
```bash
curl http://localhost:8080/api/v1/portfolio
```

### Run ML Forecasting
```bash
docker-compose exec python-service python ml_forecast.py
```

### Run R Portfolio Analysis
```bash
docker-compose exec python-service Rscript r/portfolio_analysis.R
```

---

## 🔐 Security Notes

### For Development:
- Default credentials are in `.env.example`
- JWT secrets are weak (change for production)
- No authentication enabled (add in Month 2)

### For Production:
- Use strong, randomly generated secrets
- Enable JWT authentication
- Use HTTPS for all endpoints
- Set proper CORS policies
- Enable rate limiting
- Use managed services (AWS RDS, ElastiCache)

---

## 📦 Deploying to Production

### Frontend (Vercel - Free Tier)
```bash
cd web
vercel --prod
```

### Backend (Heroku - Free Tier)
```bash
heroku create helios-api
heroku addons:create heroku-postgresql:essential-0
heroku addons:create heroku-redis:hobby-dev
git subtree push --prefix go heroku main
```

### Full Stack (Docker + AWS ECS/EKS)
See `docs/DEPLOYMENT.md` for detailed instructions (Month 4)

---

## 🆘 Getting Help

1. **Check Documentation**: `docs/` folder
2. **Search Issues**: [GitHub Issues](https://github.com/yourusername/helios-quant-framework/issues)
3. **Create Issue**: Include logs, error messages, and steps to reproduce
4. **Review Code**: All code is commented with explanations

---

## 🎓 Learning Resources

### Go
- [Go by Example](https://gobyexample.com/)
- [Effective Go](https://golang.org/doc/effective_go)

### Python
- [Python for Data Science](https://www.datacamp.com/courses/intro-to-python-for-data-science)
- [QuantLib Python Docs](https://quantlib-python-docs.readthedocs.io/)

### R
- [R for Data Science](https://r4ds.hadley.nz/)
- [PerformanceAnalytics Vignette](https://cran.r-project.org/web/packages/PerformanceAnalytics/)

### Next.js/React
- [Next.js Docs](https://nextjs.org/docs)
- [React Docs](https://react.dev/)

### Docker
- [Docker Get Started](https://docs.docker.com/get-started/)
- [Docker Compose Docs](https://docs.docker.com/compose/)

---

## 📅 What's Next?

Follow the **IMPLEMENTATION_ROADMAP.md** to:
- **Month 2**: Add Ray, Kafka, LSTM
- **Month 3**: Integrate real-time APIs, polish UI
- **Month 4**: Add monitoring, CI/CD, launch

---

**Happy Coding! 🚀**
