#!/bin/bash

# Helios Quant Framework - Native Setup Script
# This script installs and configures PostgreSQL and Redis locally (no Docker)

set -e

echo "🚀 Helios Quant Framework - Native Setup"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ This script is designed for Linux. For macOS, use brew instead."
    exit 1
fi

echo -e "${YELLOW}📦 Installing PostgreSQL...${NC}"
sudo apt update
sudo apt install -y postgresql postgresql-contrib

echo -e "${GREEN}✅ PostgreSQL installed${NC}"
echo ""

echo -e "${YELLOW}📦 Installing Redis...${NC}"
sudo apt install -y redis-server

echo -e "${GREEN}✅ Redis installed${NC}"
echo ""

# Start services
echo -e "${YELLOW}🔧 Starting services...${NC}"
sudo systemctl start postgresql
sudo systemctl start redis-server

# Enable services to start on boot (optional)
echo -e "${YELLOW}🔧 Enabling services to start on boot...${NC}"
sudo systemctl enable postgresql
sudo systemctl enable redis-server

echo -e "${GREEN}✅ Services started and enabled${NC}"
echo ""

# Create PostgreSQL user and database
echo -e "${YELLOW}🗄️  Setting up PostgreSQL database...${NC}"

# Create user (if doesn't exist)
sudo -u postgres psql -tc "SELECT 1 FROM pg_user WHERE usename = 'helios'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER helios WITH PASSWORD 'helios_dev_password';"

# Create database (if doesn't exist)
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = 'helios_quant'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE helios_quant OWNER helios;"

echo -e "${GREEN}✅ Database created${NC}"
echo ""

# Run schema
if [ -f "sql/schema.sql" ]; then
    echo -e "${YELLOW}🗄️  Loading database schema...${NC}"
    sudo -u postgres psql -d helios_quant -f sql/schema.sql
    echo -e "${GREEN}✅ Schema loaded${NC}"
else
    echo -e "${YELLOW}⚠️  sql/schema.sql not found. Skipping schema setup.${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo ""
echo "Services Status:"
echo "---------------"
sudo systemctl status postgresql --no-pager -l | head -3
sudo systemctl status redis-server --no-pager -l | head -3
echo ""
echo "Next Steps:"
echo "1. Run: npm install (in web/ directory)"
echo "2. Run: go mod download (in go/ directory)"
echo "3. Run: pip install -r requirements.txt (in python/ directory)"
echo "4. Run: ./scripts/start-dev.sh to start all services"
echo ""
echo "Database Connection:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: helios_quant"
echo "  User: helios"
echo "  Password: helios_dev_password"
echo ""
echo "Redis Connection:"
echo "  Host: localhost"
echo "  Port: 6379"
echo "  Password: none"
