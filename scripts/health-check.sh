#!/bin/bash

# Health check script for Synology Surveillance Station Video to Telegram
# This script checks if the container is running and responsive

CONTAINER_NAME="VideoSsToTg"
PORT=7878
MAX_RETRIES=5
RETRY_COUNT=0

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Checking container health...${NC}"

# Check if container exists and is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${RED}✗ Container $CONTAINER_NAME is not running${NC}"
    docker ps -a --filter "name=$CONTAINER_NAME"
    exit 1
fi
echo -e "${GREEN}✓ Container $CONTAINER_NAME is running${NC}"

# Check if port is listening
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if nc -z localhost $PORT 2>/dev/null; then
        echo -e "${GREEN}✓ Port $PORT is listening${NC}"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
        echo -e "${YELLOW}Waiting for port $PORT... (Attempt $RETRY_COUNT/$MAX_RETRIES)${NC}"
        sleep 2
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}✗ Port $PORT is not responding after $MAX_RETRIES attempts${NC}"
    echo -e "${YELLOW}Container logs:${NC}"
    docker logs --tail=20 $CONTAINER_NAME
    exit 1
fi

# Check container logs for errors
echo -e "${YELLOW}Checking logs for errors...${NC}"
if docker logs $CONTAINER_NAME 2>&1 | grep -i "error" > /dev/null; then
    echo -e "${YELLOW}⚠ Found errors in container logs${NC}"
    docker logs --tail=10 $CONTAINER_NAME | grep -i error || true
else
    echo -e "${GREEN}✓ No errors found in logs${NC}"
fi

echo ""
echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}Health check passed!${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""
echo -e "${YELLOW}Container status:${NC}"
docker ps --filter "name=$CONTAINER_NAME"
echo ""
echo -e "${YELLOW}Webhook URL:${NC}"
echo "http://your-synology-ip:$PORT/webhookcam"
echo ""
