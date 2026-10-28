#!/usr/bin/env bash
# ==============================================================================
# CodeWithAnil Backend Health & Resource Monitor for Oracle Cloud ARM64
# ==============================================================================

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}==================================================================${NC}"
echo -e "${BLUE}           CodeWithAnil Production Service Status Monitor         ${NC}"
echo -e "${BLUE}==================================================================${NC}"

# 1. System Services Status
check_service() {
    local srv=$1
    if systemctl is-active --quiet "$srv"; then
        echo -e "[ ${GREEN}OK${NC} ] Service '$srv' is running."
    else
        echo -e "[ ${RED}FAIL${NC} ] Service '$srv' is STOPPED!"
    fi
}

check_service "codewithanil"
check_service "nginx"
check_service "postgresql"

echo ""

# 2. FastAPI API Health Probe
echo -e "${YELLOW}Probing internal API health endpoint (http://127.0.0.1:8000/api/health)...${NC}"
HTTP_STATUS=$(curl -s -o /tmp/cwa_health.json -w "%{http_code}" http://127.0.0.1:8000/api/health || true)

if [ "$HTTP_STATUS" -eq 200 ]; then
    echo -e "[ ${GREEN}OK${NC} ] FastAPI returned HTTP 200."
    cat /tmp/cwa_health.json
    echo ""
else
    echo -e "[ ${RED}FAIL${NC} ] Health probe returned HTTP code $HTTP_STATUS!"
fi

echo ""

# 3. Memory & CPU Utilization
echo -e "${YELLOW}Memory & CPU Consumption (FastAPI / Uvicorn):${NC}"
ps -u ubuntu -o pid,ppid,%cpu,%mem,rss,cmd | grep -E "uvicorn|python" | grep -v grep || true

echo ""
echo -e "${YELLOW}System Memory Overview:${NC}"
free -h

echo ""
echo -e "${YELLOW}Disk Storage Overview:${NC}"
df -h /

echo -e "${BLUE}==================================================================${NC}"
