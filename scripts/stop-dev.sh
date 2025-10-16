#!/bin/bash

# Helios Quant Framework - Stop Development Services

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🛑 Stopping Helios Quant Framework services...${NC}"
echo ""

# Stop API
if [ -f "logs/api.pid" ]; then
    API_PID=$(cat logs/api.pid)
    if kill -0 $API_PID 2>/dev/null; then
        kill $API_PID
        echo -e "${GREEN}✅ API stopped (PID: $API_PID)${NC}"
    else
        echo -e "${YELLOW}⚠️  API process not running${NC}"
    fi
    rm logs/api.pid
else
    echo -e "${YELLOW}⚠️  API PID file not found${NC}"
fi

# Stop Frontend
if [ -f "logs/web.pid" ]; then
    WEB_PID=$(cat logs/web.pid)
    if kill -0 $WEB_PID 2>/dev/null; then
        kill $WEB_PID
        echo -e "${GREEN}✅ Frontend stopped (PID: $WEB_PID)${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend process not running${NC}"
    fi
    rm logs/web.pid
else
    echo -e "${YELLOW}⚠️  Frontend PID file not found${NC}"
fi

# Also kill any remaining node/go processes on our ports (cleanup)
echo ""
echo -e "${YELLOW}🧹 Cleaning up any remaining processes...${NC}"

# Kill processes on port 8080 (API)
PID_8080=$(lsof -ti:8080 2>/dev/null)
if [ ! -z "$PID_8080" ]; then
    kill $PID_8080 2>/dev/null
    echo -e "${GREEN}✅ Cleaned up port 8080${NC}"
fi

# Kill processes on port 3000 (Frontend)
PID_3000=$(lsof -ti:3000 2>/dev/null)
if [ ! -z "$PID_3000" ]; then
    kill $PID_3000 2>/dev/null
    echo -e "${GREEN}✅ Cleaned up port 3000${NC}"
fi

echo ""
echo -e "${GREEN}🎉 All services stopped${NC}"
echo ""
echo "System services (PostgreSQL, Redis) are still running."
echo "To stop them:"
echo "  sudo systemctl stop postgresql"
echo "  sudo systemctl stop redis-server"
