#!/bin/bash

# Helios Quant Framework - Repository Reorganization Script
# This script reorganizes the repository into a clean, production-grade structure

set -e  # Exit on error

echo "🚀 Starting repository reorganization..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "📁 Project root: $PROJECT_ROOT"
echo ""

# Function to safely move files
safe_move() {
    local src=$1
    local dest=$2

    if [ -f "$src" ] || [ -d "$src" ]; then
        echo "  ✓ Moving: $src → $dest"
        mkdir -p "$(dirname "$dest")"
        mv "$src" "$dest"
    else
        echo "  ⚠ Skipping (not found): $src"
    fi
}

# Function to safely copy files
safe_copy() {
    local src=$1
    local dest=$2

    if [ -f "$src" ] || [ -d "$src" ]; then
        echo "  ✓ Copying: $src → $dest"
        mkdir -p "$(dirname "$dest")"
        cp -r "$src" "$dest"
    else
        echo "  ⚠ Skipping (not found): $src"
    fi
}

echo "📦 Phase 1: Reorganizing Go Backend (services/api)"
echo "=================================================="
safe_move "go/main.go" "services/api/cmd/server/main.go"
safe_move "go/montecarlo" "services/api/internal/services/montecarlo"
safe_move "go/go.mod" "services/api/go.mod"
safe_move "go/go.sum" "services/api/go.sum"
safe_move "go/Dockerfile" "services/api/Dockerfile"
safe_copy "go/.gitignore" "services/api/.gitignore"
echo ""

echo "🐍 Phase 2: Reorganizing Python Analytics (services/analytics)"
echo "============================================================="
safe_move "python/ml_forecast.py" "services/analytics/src/ml/forecaster.py"
safe_move "python/quantlib_models.py" "services/analytics/src/quant/quantlib_models.py"
safe_move "python/output" "services/analytics/output"
safe_move "python/Dockerfile" "services/analytics/Dockerfile"
safe_move "python/requirements.txt" "services/analytics/requirements/base.txt"
echo ""

echo "📊 Phase 3: Reorganizing R Statistical (services/statistical)"
echo "============================================================="
safe_move "r/portfolio_analysis.R" "services/statistical/src/portfolio/analysis.R"
safe_move "r/optimization.R" "services/statistical/src/optimization/markowitz.R"
safe_move "r/risk_models.R" "services/statistical/src/risk/var_cvar.R"
safe_copy "r/output" "services/statistical/output"
echo ""

echo "🌐 Phase 4: Reorganizing Next.js Frontend (services/web)"
echo "========================================================"
# Note: We'll keep web structure mostly as-is since Next.js has conventions
# Just ensure it's in services/web
if [ -d "web" ] && [ ! -d "services/web/src" ]; then
    echo "  ✓ Moving web files to services/web"
    # Copy critical files only, preserve existing structure
    mkdir -p services/web
    rsync -av --exclude='node_modules' --exclude='.next' web/ services/web/
fi
echo ""

echo "🗄️  Phase 5: Reorganizing Database (database/)"
echo "=============================================="
safe_move "sql/schema.sql" "database/migrations/001_initial_schema.sql"
safe_move "sql/queries" "database/queries"
echo ""

echo "🐳 Phase 6: Reorganizing Infrastructure (infrastructure/)"
echo "=========================================================="
safe_move "docker-compose.yml" "infrastructure/docker/docker-compose.yml"
safe_copy "monitoring" "infrastructure/monitoring"
echo ""

echo "📚 Phase 7: Organizing Documentation (docs/)"
echo "============================================"
# Documentation is already in docs/, just organize better
mkdir -p docs/{architecture,api,deployment,guides}
echo "  ✓ Documentation structure created"
echo ""

echo "🔧 Phase 8: Creating Service README files"
echo "=========================================="

# Create README for each service
cat > services/api/README.md << 'EOF'
# Helios API Service (Go)

Backend API service for the Helios Quant Framework.

## Structure
- `cmd/server/` - Application entry point
- `internal/` - Private application code
- `pkg/` - Public reusable packages
- `tests/` - Integration tests

## Running
```bash
go run cmd/server/main.go
```

## Testing
```bash
go test -v ./...
```
EOF

cat > services/analytics/README.md << 'EOF'
# Helios Analytics Service (Python)

Python-based analytics service for ML, QuantLib, and distributed computing.

## Structure
- `src/ml/` - Machine learning models
- `src/quant/` - QuantLib financial calculations
- `src/distributed/` - Ray-based distributed computing
- `src/market_data/` - External API integrations

## Running
```bash
python -m src.ml.forecaster
```

## Testing
```bash
pytest tests/
```
EOF

cat > services/statistical/README.md << 'EOF'
# Helios Statistical Service (R)

R-based statistical analysis service for portfolio optimization and risk modeling.

## Structure
- `src/portfolio/` - Portfolio analysis
- `src/optimization/` - Markowitz, NSGA-II
- `src/risk/` - VaR, CVaR, stress testing

## Running
```bash
Rscript src/portfolio/analysis.R
```
EOF

cat > services/web/README.md << 'EOF'
# Helios Web Frontend (Next.js)

Modern web frontend for the Helios Quant Framework.

## Structure
- `src/app/` - Next.js app router
- `src/components/` - Reusable React components
- `src/lib/` - Utilities, hooks, and types

## Running
```bash
npm run dev
```

## Building
```bash
npm run build
npm start
```
EOF

echo ""
echo "📝 Phase 9: Creating Configuration Files"
echo "========================================"

# Create environment-specific configs
cat > config/development.env << 'EOF'
# Development Environment Configuration
ENV=development
DEBUG=true

# Database
DATABASE_URL=postgres://helios:helios_dev_password@localhost:5432/helios_quant?sslmode=disable

# Redis
REDIS_URL=redis://localhost:6379

# Kafka
KAFKA_BROKERS=localhost:9092

# API
PORT=8080
API_BASE_URL=http://localhost:8080
EOF

cat > config/production.env.example << 'EOF'
# Production Environment Configuration (EXAMPLE - DO NOT COMMIT WITH REAL VALUES)
ENV=production
DEBUG=false

# Database (use managed service)
DATABASE_URL=postgres://user:password@prod-db.example.com:5432/helios_quant?sslmode=require

# Redis (use managed service)
REDIS_URL=redis://prod-redis.example.com:6379

# Kafka (use managed service)
KAFKA_BROKERS=kafka-1.example.com:9092,kafka-2.example.com:9092

# API
PORT=8080
API_BASE_URL=https://api.helios-quant.com

# External APIs (get your own keys)
ALPHA_VANTAGE_API_KEY=your_production_key
POLYGON_API_KEY=your_production_key

# Security
JWT_SECRET=generate_strong_secret_here
SESSION_SECRET=generate_strong_secret_here
EOF

echo ""
echo "✅ Phase 10: Cleaning Up Old Directories"
echo "========================================"
echo "  ⚠ Skipping cleanup for safety. Old directories preserved."
echo "  💡 Manually remove old directories after verifying new structure works:"
echo "     - rm -rf go/"
echo "     - rm -rf python/"
echo "     - rm -rf r/"
echo "     - rm -rf sql/"
echo ""

echo ""
echo "${GREEN}✅ Repository reorganization complete!${NC}"
echo ""
echo "📋 Next Steps:"
echo "  1. Update import paths in Go files"
echo "  2. Update Python imports"
echo "  3. Update docker-compose.yml paths"
echo "  4. Test each service"
echo "  5. Update documentation"
echo "  6. Commit changes with: git add . && git commit -m 'refactor: reorganize repository structure'"
echo ""
echo "📁 New Structure:"
echo "  services/api/          - Go backend"
echo "  services/analytics/    - Python analytics"
echo "  services/statistical/  - R statistical"
echo "  services/web/          - Next.js frontend"
echo "  database/              - SQL migrations and queries"
echo "  infrastructure/        - Docker, K8s, monitoring"
echo "  scripts/               - Utility scripts"
echo "  docs/                  - Documentation"
echo ""
echo "🚀 Happy coding!"
