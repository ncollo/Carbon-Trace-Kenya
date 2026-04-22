# Carbon Trace Kenya - Complete Troubleshooting Guide

## Common Errors and Solutions

### 1. **Backend Connection Errors**

#### Error: `Connection refused` or `ERR_CONNECTION_REFUSED`
**Causes:**
- Backend not running on expected port
- Wrong port configuration
- Firewall blocking ports

**Solutions:**
```bash
# Check if backend is running
netstat -ano | findstr :8000
netstat -ano | findstr :8002

# Restart backend on correct port
python complete_test_server.py

# Check firewall (Windows)
netsh advfirewall firewall add rule name="AllowBackend" dir=in action=allow protocol=TCP localport=8002

# Check firewall (Linux)
ufw allow 8002
```

#### Error: `404 Not Found` for API endpoints
**Causes:**
- Using original backend (missing endpoints)
- Wrong endpoint paths
- Test server not started

**Solutions:**
```bash
# Use complete test server
python complete_test_server.py

# Verify endpoints exist
curl http://localhost:8002/api/health
curl http://localhost:8002/api/overview/kpis
```

### 2. **Frontend Connection Issues**

#### Error: `CORS policy` errors
**Causes:**
- Frontend and backend on different ports
- CORS not configured properly

**Solutions:**
```python
# Ensure CORS middleware is configured
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Error: `Network Error` in browser console
**Causes:**
- Backend URL mismatch in frontend config
- Backend not responding

**Solutions:**
```javascript
// Check carbontrace/src/api/client.js
const BASE = "http://localhost:8002/api";  // Must match backend port
```

### 3. **Database Connection Errors**

#### Error: `OperationalError: could not connect to server`
**Causes:**
- PostgreSQL not running
- Wrong database credentials
- Database not created

**Solutions:**
```bash
# For production deployment (DigitalOcean)
# Use docker-compose with PostgreSQL service
docker-compose up -d postgres

# Check database logs
docker-compose logs postgres

# Create database if needed
docker-compose exec postgres createdb -U postgres carbon
```

#### Error: `psycopg2.OperationalError` during local development
**Causes:**
- PostgreSQL not installed locally
- Missing pg_config

**Solutions:**
```bash
# Use mock data approach (recommended for demo)
python complete_test_server.py

# Or install PostgreSQL
sudo apt-get install postgresql postgresql-contrib
# Windows: Use Docker or WSL
```

### 4. **Docker Deployment Errors**

#### Error: `docker: command not found`
**Causes:**
- Docker not installed on server

**Solutions:**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Then restart server or logout/login
```

#### Error: `port already allocated`
**Causes:**
- Port conflicts with existing services

**Solutions:**
```bash
# Find what's using the port
netstat -tulpn | grep :8000
lsof -i :8000

# Kill conflicting processes
sudo kill -9 <PID>

# Or use different ports in docker-compose.yml
ports:
  - "8001:8000"  # Map container port 8000 to host port 8001
```

#### Error: `docker-compose build fails`
**Causes:**
- Missing dependencies
- Syntax errors in Dockerfile

**Solutions:**
```bash
# Clean build cache
docker system prune -f
docker-compose build --no-cache

# Check Dockerfile syntax
docker build -t test .
```

### 5. **SSH and Deployment Errors**

#### Error: `Permission denied (publickey)`
**Causes:**
- SSH key not added to server
- Wrong SSH key path

**Solutions:**
```bash
# Generate new SSH key
ssh-keygen -t ed25519 -C "deployment-key"

# Copy public key to server
ssh-copy-id root@YOUR_DROPLET_IP

# Or manually add to ~/.ssh/authorized_keys on server
```

#### Error: `Host key verification failed`
**Causes:**
- Server SSH key changed
- First-time connection

**Solutions:**
```bash
# Remove old host key
ssh-keygen -R YOUR_DROPLET_IP

# Or skip verification (for testing)
ssh -o StrictHostKeyChecking=no root@YOUR_DROPLET_IP
```

### 6. **AI Model Errors**

#### Error: `422 Unprocessable Entity` for fleet optimization
**Causes:**
- Wrong JSON request format
- Missing required fields

**Solutions:**
```bash
# Correct format
curl -X POST http://localhost:8002/api/optimize/fleet \
  -H "Content-Type: application/json" \
  -d '{
    "fleet_data": [
      {"id": "truck1", "efficiency": 0.8, "emission_factor": 2.64, "distance": 100},
      {"id": "ev1", "efficiency": 0.95, "emission_factor": 0.0, "distance": 80}
    ]
  }'
```

#### Error: `ModuleNotFoundError: No module named 'ml_models_new'`
**Causes:**
- Python path issues
- Missing ML model files

**Solutions:**
```bash
# Ensure you're in correct directory
cd /path/to/CARBON TRACE

# Add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or use absolute imports in code
```

### 7. **Environment Variable Errors**

#### Error: `GEMINI_API_KEY not configured`
**Causes:**
- Missing environment variables
- .env file not loaded

**Solutions:**
```bash
# Create .env file from template
cp .env.example .env

# Edit with your values
nano .env

# For production, set in docker-compose.yml
environment:
  - GEMINI_API_KEY=your-key-here
```

### 8. **Frontend Build Errors**

#### Error: `npm ERR! code ENOENT`
**Causes:**
- Node.js not installed
- Missing package.json

**Solutions:**
```bash
# Install Node.js (Ubuntu)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install dependencies
cd carbontrace
npm install
```

#### Error: `Vite dev server won't start`
**Causes:**
- Port conflicts
- Missing dependencies

**Solutions:**
```bash
# Kill existing processes
lsof -ti:5173 | xargs kill -9

# Clear cache
rm -rf node_modules package-lock.json
npm install

# Start with different port
npm run dev -- --port 5174
```

### 9. **GitHub Actions CI/CD Errors**

#### Error: `SSH connection timed out`
**Causes:**
- Droplet not accessible from GitHub
- SSH key issues

**Solutions:**
```yaml
# In .github/workflows/deploy.yml
- name: Deploy to DigitalOcean
  uses: appleboy/ssh-action@v0.1.5
  with:
    host: ${{ secrets.DROPLET_IP }}
    username: root
    key: ${{ secrets.DEPLOY_SSH_KEY }}
    timeout: 300s  # Increase timeout
    command_timeout: 60s
```

#### Error: `docker-compose command not found`
**Causes:**
- Docker Compose not installed on server

**Solutions:**
```bash
# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 10. **Performance Issues**

#### Error: `504 Gateway Timeout`
**Causes:**
- Slow API responses
- Server overload

**Solutions:**
```bash
# Check server resources
free -h
df -h
top

# Restart services
docker-compose restart

# Scale up if needed (DigitalOcean)
# Upgrade to larger droplet
```

## Quick Diagnostic Commands

### Backend Health Check
```bash
# Test basic connectivity
curl -f http://localhost:8002/api/health || echo "Backend down"

# Check all endpoints
python system_test.py
```

### Frontend Health Check
```bash
# Check if frontend is running
curl -f http://localhost:5173 || echo "Frontend down"

# Check browser console for errors
# Open Developer Tools (F12) in browser
```

### System Resources
```bash
# CPU and Memory
top
htop

# Disk space
df -h

# Network connectivity
ping google.com
```

### Docker Status
```bash
# Check running containers
docker ps

# Check container logs
docker-compose logs web
docker-compose logs postgres

# Restart all services
docker-compose down && docker-compose up -d
```

## Emergency Recovery

### If Everything Fails
```bash
# 1. Stop all services
docker-compose down
pkill -f python
pkill -f node

# 2. Clean up
docker system prune -f
docker volume prune -f

# 3. Restart with minimal setup
python complete_test_server.py  # Backend only
cd carbontrace && npm run dev    # Frontend only

# 4. Test basic functionality
curl http://localhost:8002/api/health
```

### Database Recovery
```bash
# Backup current data
docker-compose exec postgres pg_dump -U postgres carbon > backup.sql

# Restore from backup
docker-compose exec -T postgres psql -U postgres carbon < backup.sql

# Reset database (last resort)
docker-compose down -v
docker-compose up -d postgres
```

## Prevention Tips

1. **Always test locally before deploying**
2. **Use version control for all changes**
3. **Monitor server resources regularly**
4. **Set up automated backups**
5. **Use environment-specific configurations**
6. **Test SSH keys before deployment**
7. **Monitor logs for early error detection**

## Support Checklist

Before asking for help, verify:
- [ ] Backend responds to `/api/health`
- [ ] Frontend loads without console errors
- [ ] All required files are present
- [ ] Environment variables are set
- [ ] Docker services are running
- [ ] SSH keys work correctly
- [ ] Ports are accessible
- [ ] System has sufficient resources

Run the deployment checklist:
```bash
python deployment_checklist.py
```

This will identify most common issues before they become problems.
