# Carbon Trace Kenya - Production Deployment Setup

## Quick Start for Hackathon Demo

### 1. Create Production Repo
```bash
# On GitHub, create new repo: carbon-trace-kenya-production
# Then clone and copy production files
git clone git@github.com:YOUR_USERNAME/carbon-trace-kenya-production.git
cd carbon-trace-kenya-production
```

### 2. Generate SSH Keys
```bash
# Generate deployment key
ssh-keygen -t ed25519 -C "carbon-trace-deploy-key" -f ~/.ssh/carbon_trace_deploy_key

# Add public key to DigitalOcean during droplet creation
cat ~/.ssh/carbon_trace_deploy_key.pub
```

### 3. DigitalOcean Droplet Setup
- **Size**: 2GB RAM, 1 CPU (minimum for Docker)
- **OS**: Ubuntu 24.04
- **Add SSH key**: Paste the public key from above
- **Enable IPv6**: Yes
- **Enable Monitoring**: Yes

### 4. Server First-Time Setup
```bash
# SSH into droplet
ssh root@YOUR_DROPLET_IP

# Update and install dependencies
apt update && apt upgrade -y
apt install -y git docker.io docker-compose nodejs npm python3 python3-pip

# Clone production repo
git clone git@github.com:YOUR_USERNAME/carbon-trace-kenya-production.git
cd carbon-trace-kenya-production

# Setup environment
cp .env.example .env
# Edit .env with your values
```

### 5. Deploy with Docker
```bash
docker-compose build
docker-compose up -d
```

### 6. Access Your App
- **Backend**: http://YOUR_DROPLET_IP:8000
- **Frontend**: http://YOUR_DROPLET_IP:5173
- **API Docs**: http://YOUR_DROPLET_IP:8000/docs

## Files to Copy to Production Repo
- docker-compose.yml
- Dockerfile  
- carbontrace-backend/
- carbontrace/
- .env.example
- requirements.txt
- .github/workflows/deploy.yml (CI/CD)

## Environment Variables Needed
```bash
DATABASE_URL=postgresql://user:pass@postgres:5432/carbon
REDIS_URL=redis://redis:6379/0
JWT_SECRET=your-secure-secret-key
JWT_ALGORITHM=HS256
USE_S3=false  # Set to true if using S3
```

## CI/CD Setup
Add deploy key to GitHub repo settings:
- Go to Settings > Secrets and variables > Actions
- Add `DEPLOY_SSH_KEY` (private key content)
- Add `DROPLET_IP` (your droplet IP)
