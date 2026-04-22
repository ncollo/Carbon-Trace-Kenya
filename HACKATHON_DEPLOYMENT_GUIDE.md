# Carbon Trace Kenya - Hackathon Deployment Guide

## Quick Setup for Live Demo (30 minutes)

### Step 1: Create Production Repository
1. Go to GitHub and create new repo: `carbon-trace-kenya-production`
2. Make it **Private** for security during hackathon
3. Clone locally and copy these files:
   ```bash
   git clone git@github.com:YOUR_USERNAME/carbon-trace-kenya-production.git
   cd carbon-trace-kenya-production
   
   # Copy essential files from your dev repo
   cp -r ../CARBON\ TRACE/carbontrace-backend .
   cp -r ../CARBON\ TRACE/carbontrace .
   cp ../CARBON\ TRACE/docker-compose.prod.yml docker-compose.yml
   cp ../CARBON\ TRACE/Dockerfile .
   cp ../CARBON\ TRACE/requirements.txt .
   cp ../CARBON\ TRACE/.env.example .
   cp -r ../CARBON\ TRACE/.github .
   ```

### Step 2: Generate SSH Key
```bash
# Generate deployment key
ssh-keygen -t ed25519 -C "hackathon-deploy-key" -f ~/.ssh/hackathon_deploy

# Copy public key (this will be shown in terminal)
cat ~/.ssh/hackathon_deploy.pub
```

### Step 3: Create DigitalOcean Droplet
1. **Droplet Specs** (minimum for demo):
   - $6/month plan (1GB RAM, 1 CPU, 25GB SSD)
   - Ubuntu 24.04 LTS
   - Region: Choose closest to your hackathon location
   - **Add SSH Key**: Paste the public key from Step 2

2. **After creation**, note the Droplet IP address

### Step 4: First-Time Server Setup
```bash
# SSH into your new droplet
ssh root@YOUR_DROPLET_IP

# Run setup commands
apt update && apt upgrade -y
apt install -y git docker.io docker-compose

# Clone your production repo
git clone git@github.com:YOUR_USERNAME/carbon-trace-kenya-production.git
cd carbon-trace-kenya-production

# Setup environment
cp .env.example .env
nano .env  # Edit with your settings
```

### Step 5: Configure GitHub Secrets
In your production repo on GitHub:
1. Go to Settings > Secrets and variables > Actions
2. Add these secrets:
   - `DEPLOY_SSH_KEY`: Copy content of `~/.ssh/hackathon_deploy` (private key)
   - `DROPLET_IP`: Your droplet IP address

### Step 6: Deploy!
```bash
# From your local machine
export DROPLET_IP=YOUR_DROPLET_IP
chmod +x deploy.sh
./deploy.sh
```

Or push to GitHub and let Actions deploy automatically.

## Access Your Live Demo
- **Backend API**: http://YOUR_DROPLET_IP:8000
- **Frontend**: http://YOUR_DROPLET_IP:5173  
- **API Documentation**: http://YOUR_DROPLET_IP:8000/docs
- **New ML Features**: http://YOUR_DROPLET_IP:8000/api/models/new-features

## New ML Model Features for Demo

### 1. Real-time Carbon Prediction
```bash
curl -X POST http://YOUR_DROPLET_IP:8000/api/predict/carbon-emissions \
  -H "Content-Type: application/json" \
  -d '{
    "distance_km": 25.5,
    "vehicle_type": "diesel_truck",
    "road_type": "urban",
    "traffic_density": "high"
  }'
```

### 2. Fleet Optimization
```bash
curl -X POST http://YOUR_DROPLET_IP:8000/api/optimize/fleet \
  -H "Content-Type: application/json" \
  -d '{
    "fleet_data": [
      {"id": "truck1", "efficiency": 0.8, "emission_factor": 2.64},
      {"id": "ev1", "efficiency": 0.95, "emission_factor": 0.0}
    ]
  }'
```

## Troubleshooting Quick Fixes

### If Docker fails to start:
```bash
ssh root@YOUR_DROPLET_IP
systemctl restart docker
docker system prune -f
```

### If ports are blocked:
```bash
ssh root@YOUR_DROPLET_IP
ufw allow 8000
ufw allow 5173
ufw allow 22
```

### Check service status:
```bash
ssh root@YOUR_DROPLET_IP
cd carbon-trace-kenya-production
docker-compose ps
docker-compose logs web
```

## Demo Script for Hackathon

1. **Show Overview**: http://YOUR_DROPLET_IP:5173
2. **API Features**: http://YOUR_DROPLET_IP:8000/docs
3. **New ML Models**: Show carbon prediction endpoint
4. **Live Data**: Upload a fuel card image to show OCR
5. **Real-time Updates**: Push a change to trigger CI/CD

## Environment Variables (.env)
```bash
DATABASE_URL=postgresql://user:pass@postgres:5432/carbon
REDIS_URL=redis://redis:6379/0
JWT_SECRET=hackathon-demo-secret-key
JWT_ALGORITHM=HS256
USE_S3=false
GEMINI_API_KEY=your-gemini-key  # For OCR features
```

## Success Metrics
- [ ] Backend responds at /api/health
- [ ] Frontend loads at port 5173
- [ ] New ML endpoints return predictions
- [ ] Image OCR works with fuel receipts
- [ ] CI/CD deploys on git push

Good luck with your hackathon demo!
