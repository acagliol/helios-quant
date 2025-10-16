#!/bin/bash

# Helios Quant Framework - Development Start Script
# Starts all services in native mode (no Docker)

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Helios Quant Framework - Starting Development Environment${NC}"
echo "================================================================"
echo ""

# Check if services are running
echo -e "${YELLOW}🔍 Checking system services...${NC}"

if ! sudo systemctl is-active --quiet postgresql; then
    echo -e "${YELLOW}  Starting PostgreSQL...${NC}"
    sudo systemctl start postgresql
fi
echo -e "${GREEN}  ✅ PostgreSQL is running${NC}"

if ! sudo systemctl is-active --quiet redis-server; then
    echo -e "${YELLOW}  Starting Redis...${NC}"
    sudo systemctl start redis-server
fi
echo -e "${GREEN}  ✅ Redis is running${NC}"

echo ""

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo -e "${GREEN}✅ Environment variables loaded from .env${NC}"
else
    echo -e "${YELLOW}⚠️  .env file not found. Using .env.example...${NC}"
    cp .env.example .env
    export $(cat .env | grep -v '^#' | xargs)
fi

echo ""

# Check if dependencies are installed
echo -e "${YELLOW}🔍 Checking dependencies...${NC}"

if [ ! -d "web/node_modules" ]; then
    echo -e "${YELLOW}  Installing frontend dependencies...${NC}"
    cd web && npm install && cd ..
fi

if [ ! -f "go/go.sum" ]; then
    echo -e "${YELLOW}  Downloading Go dependencies...${NC}"
    cd go && go mod download && cd ..
fi

echo -e "${GREEN}✅ Dependencies ready${NC}"
echo ""

# Create log directory
mkdir -p logs

echo -e "${BLUE}🚀 Starting services...${NC}"
echo ""

# Start Go API in background
echo -e "${YELLOW}  Starting Go API on port 8080...${NC}"
cd go
go run main.go > ../logs/api.log 2>&1 &
API_PID=$!
echo $API_PID > ../logs/api.pid
cd ..
echo -e "${GREEN}  ✅ API started (PID: $API_PID)${NC}"

# Wait for API to be ready
echo -e "${YELLOW}  Waiting for API to be ready...${NC}"
sleep 3

# Start Next.js frontend in background
echo -e "${YELLOW}  Starting Next.js frontend on port 3000...${NC}"
cd web
npm run dev > ../logs/web.log 2>&1 &
WEB_PID=$!
echo $WEB_PID > ../logs/web.pid
cd ..
echo -e "${GREEN}  ✅ Frontend started (PID: $WEB_PID)${NC}"

echo ""
echo -e "${GREEN}🎉 All services started successfully!${NC}"
echo ""
echo "Access your application:"
echo "  Frontend:  http://localhost:3000"
echo "  API:       http://localhost:8080"
echo "  Health:    http://localhost:8080/api/v1/health"
echo ""
echo "Logs:"
echo "  API:       tail -f logs/api.log"
echo "  Frontend:  tail -f logs/web.log"
echo ""
echo "Stop services:"
echo "  Run: ./scripts/stop-dev.sh"
echo "  Or:  kill $API_PID $WEB_PID"
echo ""
echo -e "${BLUE}Press Ctrl+C to view logs (services will keep running)${NC}"
echo ""

# Tail logs
tail -f logs/api.log logs/web.log
