# Docker Setup (Optional)

> **Note**: Native setup is recommended for development. Docker setup uses 5-7GB of disk space vs ~500MB for native setup.

## When to Use Docker

Use Docker setup if you:
- Need exact production environment parity
- Want to use Kafka/Zookeeper
- Need Prometheus/Grafana monitoring
- Are testing deployment configurations
- Have multiple team members on different OSes

## Restore Docker Setup

The docker-compose.yml file has been backed up. To use it:

```bash
# Restore docker-compose.yml
mv docker-compose.yml.backup docker-compose.yml

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Docker Services Included

The full Docker setup includes:

| Service | Image | Ports | Disk Usage |
|---------|-------|-------|------------|
| PostgreSQL | postgres:16 | 5432 | ~400MB |
| Redis | redis:7.2-alpine | 6379 | ~50MB |
| Zookeeper | confluentinc/cp-zookeeper | 2181 | ~800MB |
| Kafka | confluentinc/cp-kafka | 9092, 9093 | ~1.2GB |
| Go API | Custom build | 8080 | ~500MB |
| Next.js Web | Custom build | 3000 | ~800MB |
| Python Service | Custom build | - | ~600MB |
| Prometheus | prom/prometheus | 9090 | ~300MB |
| Grafana | grafana/grafana | 3001 | ~400MB |
| **Total** | | | **~5-7GB** |

## Alternative: Hybrid Setup

You can mix native and Docker services:

### Use Native DB + Redis with Docker Frontend

```bash
# Start native services
sudo systemctl start postgresql redis-server

# Use only web/api containers
docker-compose up -d api web
```

### Use Native Everything Except Kafka

```bash
# Start native services
sudo systemctl start postgresql redis-server

# Start only Kafka stack
docker-compose up -d zookeeper kafka
```

## Clean Up Docker Resources

If you want to free up space:

```bash
# Stop all containers
docker-compose down -v

# Remove all unused images
docker image prune -a

# Remove all unused volumes
docker volume prune

# Remove all unused containers
docker container prune

# Full cleanup (WARNING: removes everything)
docker system prune -a --volumes
```

---

For native setup instructions, see [NATIVE_SETUP.md](NATIVE_SETUP.md)
