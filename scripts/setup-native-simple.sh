#!/bin/bash

# Simplified Helios setup - installs only PostgreSQL and Redis
# Skips apt update to avoid repository issues

set -e

echo "🚀 Helios Quant Framework - Simple Native Setup"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}📦 Installing PostgreSQL and Redis...${NC}"
echo ""

# Check if already installed
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL already installed${NC}"
else
    echo "Installing PostgreSQL..."
    sudo apt install -y postgresql postgresql-contrib
    echo -e "${GREEN}✅ PostgreSQL installed${NC}"
fi

if command -v redis-server &> /dev/null; then
    echo -e "${GREEN}✅ Redis already installed${NC}"
else
    echo "Installing Redis..."
    sudo apt install -y redis-server
    echo -e "${GREEN}✅ Redis installed${NC}"
fi

echo ""
echo -e "${YELLOW}🔧 Starting services...${NC}"

# Start services
sudo systemctl start postgresql 2>/dev/null || echo "PostgreSQL already running"
sudo systemctl start redis-server 2>/dev/null || echo "Redis already running"

# Enable on boot
sudo systemctl enable postgresql
sudo systemctl enable redis-server

echo -e "${GREEN}✅ Services started${NC}"
echo ""

# Setup database
echo -e "${YELLOW}🗄️  Setting up PostgreSQL database...${NC}"

# Create user if doesn't exist
sudo -u postgres psql -tc "SELECT 1 FROM pg_user WHERE usename = 'helios'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER helios WITH PASSWORD 'helios_dev_password';"

# Create database if doesn't exist
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = 'helios_quant'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE helios_quant OWNER helios;"

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE helios_quant TO helios;"

echo -e "${GREEN}✅ Database created${NC}"
echo ""

# Run schema if exists
if [ -f "sql/schema.sql" ]; then
    echo -e "${YELLOW}🗄️  Loading database schema...${NC}"
    sudo -u postgres psql -d helios_quant -f sql/schema.sql
    echo -e "${GREEN}✅ Schema loaded${NC}"
else
    echo -e "${YELLOW}⚠️  sql/schema.sql not found. Run from project root or load schema manually.${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo ""
echo "Services Status:"
echo "---------------"
systemctl status postgresql --no-pager -l | head -3
systemctl status redis-server --no-pager -l | head -3
echo ""
echo "Next Steps:"
echo "1. cd web && npm install"
echo "2. cd go && go mod download"
echo "3. ./scripts/start-dev.sh"
echo ""
echo "Database Connection:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: helios_quant"
echo "  User: helios"
echo "  Password: helios_dev_password"
echo ""
echo "Test connection:"
echo "  psql -U helios -d helios_quant -h localhost"
