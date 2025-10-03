#!/bin/bash

# Financial Dashboard Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Financial Dashboard deployment...${NC}"

# Check if required environment variables are set
if [ -z "$GITHUB_REPOSITORY" ]; then
    echo -e "${RED}Error: GITHUB_REPOSITORY environment variable is not set${NC}"
    exit 1
fi

# Set environment variables
export GITHUB_REPOSITORY=${GITHUB_REPOSITORY}

# Pull latest code
echo -e "${YELLOW}Pulling latest code...${NC}"
git pull origin main

# Pull latest Docker images
echo -e "${YELLOW}Pulling latest Docker images...${NC}"
docker-compose -f docker-compose.prod.yml pull

# Stop existing containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker-compose -f docker-compose.prod.yml down

# Start new containers
echo -e "${YELLOW}Starting new containers...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
sleep 30

# Check if services are running
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo -e "${GREEN}Deployment successful! Services are running.${NC}"
else
    echo -e "${RED}Deployment failed! Services are not running properly.${NC}"
    docker-compose -f docker-compose.prod.yml logs
    exit 1
fi

# Clean up old images
echo -e "${YELLOW}Cleaning up old Docker images...${NC}"
docker image prune -f

echo -e "${GREEN}Deployment completed successfully!${NC}"