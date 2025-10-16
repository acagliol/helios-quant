# Native Setup Guide - No Docker Required!

## Why Choose Native Setup?

**Space Savings**: ~500MB vs ~5-7GB with Docker
- No container images to download
- No Docker volumes
- Direct access to services

**Performance Benefits**:
- Faster startup times
- Lower memory usage
- Direct filesystem access
- No containerization overhead

**Development Experience**:
- Easier debugging
- Direct access to logs
- Simpler service management
- Better IDE integration

---

## What Gets Installed?

| Service | Size | Purpose |
|---------|------|---------|
| **PostgreSQL 16** | ~100MB | Database for portfolio data |
| **Redis 7** | ~3MB | Caching and pub/sub |
| **Total** | ~500MB | With all dependencies |

**What We Skip** (saves ~5GB):
- ❌ Docker images
- ❌ Kafka + Zookeeper (~2GB)
- ❌ Prometheus + Grafana (~1GB)
- ❌ Container overhead

---

## Quick Start

### 1. Run Setup Script

```bash
./scripts/setup-native.sh
```

This script will:
- Install PostgreSQL and Redis via apt
- Create `helios` database user
- Create `helios_quant` database
- Load database schema
- Start services
- Enable services to start on boot

### 2. Install App Dependencies

```bash
# Frontend
cd web && npm install && cd ..

# Backend
cd go && go mod download && cd ..

# Python (optional)
cd python && pip install -r requirements.txt && cd ..
```

### 3. Start Development

```bash
./scripts/start-dev.sh
```

This will:
- Check that PostgreSQL and Redis are running
- Start the Go API (port 8080)
- Start the Next.js frontend (port 3000)
- Tail logs from both services

### 4. Stop Development

```bash
./scripts/stop-dev.sh
```

Or manually:
```bash
kill $(cat logs/api.pid)
kill $(cat logs/web.pid)
```

---

## Service Management

### PostgreSQL

```bash
# Start
sudo systemctl start postgresql

# Stop
sudo systemctl stop postgresql

# Status
sudo systemctl status postgresql

# Connect to database
psql -U helios -d helios_quant

# Run queries
psql -U helios -d helios_quant -c "SELECT * FROM portfolio_data;"
```

### Redis

```bash
# Start
sudo systemctl start redis-server

# Stop
sudo systemctl stop redis-server

# Status
sudo systemctl status redis-server

# Connect to Redis CLI
redis-cli

# Inside redis-cli
KEYS *
GET some_key
```

---

## Configuration

### Database Connection

Edit `.env`:
```bash
DATABASE_URL=postgres://helios:helios_dev_password@localhost:5432/helios_quant?sslmode=disable
```

### Redis Connection

```bash
REDIS_URL=redis://localhost:6379
```

---

## Troubleshooting

### PostgreSQL Won't Start

```bash
# Check status
sudo systemctl status postgresql

# View logs
sudo journalctl -u postgresql -n 50

# Restart
sudo systemctl restart postgresql
```

### Redis Won't Start

```bash
# Check status
sudo systemctl status redis-server

# View logs
sudo journalctl -u redis-server -n 50

# Restart
sudo systemctl restart redis-server
```

### Port Already in Use

```bash
# Find what's using port 8080
lsof -i :8080

# Kill it
kill -9 <PID>

# Or use the cleanup in stop script
./scripts/stop-dev.sh
```

### Database Permission Issues

```bash
# Reset database user
sudo -u postgres psql -c "DROP USER IF EXISTS helios;"
sudo -u postgres psql -c "CREATE USER helios WITH PASSWORD 'helios_dev_password';"
sudo -u postgres psql -c "ALTER DATABASE helios_quant OWNER TO helios;"
```

---

## Uninstall

If you want to remove everything:

```bash
# Stop services
./scripts/stop-dev.sh

# Stop system services
sudo systemctl stop postgresql redis-server

# Disable auto-start
sudo systemctl disable postgresql redis-server

# Remove packages
sudo apt remove --purge postgresql postgresql-contrib redis-server

# Remove data (optional)
sudo rm -rf /var/lib/postgresql
sudo rm -rf /var/lib/redis
```

---

## Comparison: Native vs Docker

| Feature | Native | Docker |
|---------|--------|--------|
| **Disk Space** | ~500MB | ~5-7GB |
| **Startup Time** | ~3s | ~30s |
| **Memory Usage** | ~200MB | ~1GB+ |
| **Debugging** | Direct | Through containers |
| **IDE Integration** | Native | Port forwarding |
| **Log Access** | Direct files | docker logs |
| **Setup Complexity** | Low | Medium |
| **Production Ready** | ✅ | ✅ |

---

## When to Use Docker Instead?

Use Docker if you:
- Need exact production parity
- Want Kafka/Zookeeper for messaging
- Need Prometheus/Grafana monitoring
- Are deploying to Kubernetes
- Have multiple team members with different OSes

Otherwise, **native setup is perfect for development**.

---

## Production Deployment

For production, consider:
- **Native**: Deploy to a VPS with PostgreSQL + Redis installed
- **Docker**: Use Docker Compose on a VPS or container orchestration
- **Managed Services**: Use AWS RDS + ElastiCache (recommended)

---

**Happy coding! 🚀**
