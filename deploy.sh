#!/bin/bash
# Carbon Trace Kenya - Deployment Script for DigitalOcean

set -e

echo "=== Carbon Trace Kenya Deployment Script ==="

# Check if required variables are set
if [ -z "$DROPLET_IP" ]; then
    echo "Error: DROPLET_IP environment variable not set"
    echo "Export it like: export DROPLET_IP=your.droplet.ip"
    exit 1
fi

echo "Deploying to DigitalOcean Droplet: $DROPLET_IP"

# SSH into droplet and deploy
ssh root@$DROPLET_IP << 'EOF'
    echo "=== Connected to Droplet ==="
    
    # Navigate to project directory
    cd /root/carbon-trace-kenya-production
    
    # Pull latest changes
    echo "Pulling latest changes..."
    git pull origin main
    
    # Stop existing containers
    echo "Stopping existing containers..."
    docker-compose down
    
    # Build and start new containers
    echo "Building and starting containers..."
    docker-compose build
    docker-compose up -d
    
    # Wait for services to be healthy
    echo "Waiting for services to start..."
    sleep 30
    
    # Check service status
    echo "Checking service status..."
    docker-compose ps
    
    # Show logs for debugging
    echo "=== Recent logs ==="
    docker-compose logs --tail=20
    
    echo "=== Deployment Complete ==="
    echo "Backend: http://$(curl -s ifconfig.me):8000"
    echo "Frontend: http://$(curl -s ifconfig.me):5173"
    echo "API Docs: http://$(curl -s ifconfig.me):8000/docs"
EOF

echo "=== Deployment Finished ==="
