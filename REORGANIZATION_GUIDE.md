# Repository Reorganization Guide

## 🎯 Quick Reorganization

### Step 1: Run the Script
```bash
./scripts/utils/reorganize_repo.sh
```

### Step 2: Update Import Paths
After running the script, update these files:

**Go (`services/api/cmd/server/main.go`):**
```go
module helios/services/api
```

**Python (add to files):**
```python
import sys
sys.path.insert(0, '/app/src')
```

**Docker Compose:**
Update paths in `infrastructure/docker/docker-compose.yml`

### Step 3: Test
```bash
cd services/api && go run cmd/server/main.go
cd services/web && npm run dev
```

## 📁 New Structure
```
services/
├── api/          # Go backend
├── analytics/    # Python
├── statistical/  # R
└── web/          # Next.js

infrastructure/   # Docker, K8s
database/         # SQL
scripts/          # Utils
docs/            # Docs
```

That's it! Simple and clean.
