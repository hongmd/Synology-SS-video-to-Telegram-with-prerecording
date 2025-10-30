#!/bin/bash

# Setup script for Synology Surveillance Station Video to Telegram
# This script helps with initial setup and configuration

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}Synology SS Video to Telegram${NC}"
echo -e "${GREEN}Setup Script${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    echo "Please install Docker from https://www.docker.com"
    exit 1
fi
echo -e "${GREEN}✓ Docker is installed${NC}"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose is installed${NC}"

echo ""
echo -e "${YELLOW}Checking project structure...${NC}"

# Check required files
required_files=(".env.example" "docker-compose.yaml" "Dockerfile" "requirements.txt")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ Found $file${NC}"
    else
        echo -e "${RED}✗ Missing $file${NC}"
        exit 1
    fi
done

echo ""
echo -e "${YELLOW}Setting up environment...${NC}"

# Create .env from .env.example if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env from template${NC}"
    echo -e "${YELLOW}Please edit .env with your configuration:${NC}"
    echo "  - TG_CHAT_ID: Your Telegram chat ID"
    echo "  - TG_TOKEN: Your Telegram bot token"
    echo "  - SYNO_IP: Your Synology NAS IP address"
    echo "  - SYNO_LOGIN: Your Synology username"
    echo "  - SYNO_PASS: Your Synology password"
else
    echo -e "${GREEN}✓ .env already exists${NC}"
fi

echo ""
echo -e "${YELLOW}Validating configuration...${NC}"

# Validate .env file
source .env

if [ -z "$TG_CHAT_ID" ]; then
    echo -e "${RED}✗ TG_CHAT_ID is not set${NC}"
    exit 1
fi
echo -e "${GREEN}✓ TG_CHAT_ID is set${NC}"

if [ -z "$TG_TOKEN" ]; then
    echo -e "${RED}✗ TG_TOKEN is not set${NC}"
    exit 1
fi
echo -e "${GREEN}✓ TG_TOKEN is set${NC}"

if [ -z "$SYNO_IP" ]; then
    echo -e "${RED}✗ SYNO_IP is not set${NC}"
    exit 1
fi
echo -e "${GREEN}✓ SYNO_IP is set to $SYNO_IP${NC}"

if [ -z "$SYNO_LOGIN" ]; then
    echo -e "${RED}✗ SYNO_LOGIN is not set${NC}"
    exit 1
fi
echo -e "${GREEN}✓ SYNO_LOGIN is set${NC}"

if [ -z "$SYNO_PASS" ]; then
    echo -e "${RED}✗ SYNO_PASS is not set${NC}"
    exit 1
fi
echo -e "${GREEN}✓ SYNO_PASS is set${NC}"

echo ""
echo -e "${YELLOW}Validating docker-compose.yaml...${NC}"
docker-compose config > /dev/null
echo -e "${GREEN}✓ docker-compose.yaml is valid${NC}"

echo ""
echo -e "${YELLOW}Building Docker image...${NC}"
docker-compose build
echo -e "${GREEN}✓ Docker image built successfully${NC}"

echo ""
echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}Setup completed!${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Review .env configuration: cat .env"
echo "  2. Start containers: docker-compose up -d"
echo "  3. Check logs: docker-compose logs -f"
echo "  4. Configure Synology webhook: http://your-docker-host:7878/webhookcam"
echo ""
echo -e "${YELLOW}For more information, see:${NC}"
echo "  - English: README.en.md"
echo "  - Russian: README.md"
echo ""
