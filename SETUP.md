# Carbon Trace Kenya - Setup Guide

Quick start guide to get the app running with the new components.

## Prerequisites

- Python 3.10+
- PostgreSQL 13+ (or Docker)
- Redis (or Docker)
- Node.js 18+ (for frontend)

## Step 1: Environment Setup

### 1.1 Create `.env` file

```bash
cp .env.example .env
```

### 1.2 Update `.env` with your values

Edit `.env` and update:

```bash
# Database
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/carbon_trace_kenya

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Secret (generate: python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET=your-generated-secret-here

# Frontend CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 1.3 Option A: Use Docker (Recommended)

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Wait for services to be ready
sleep 5

# Check if services are running
docker ps
```

### 1.3 Option B: Manual Setup

**PostgreSQL:**
```bash
# Linux/Mac
brew install postgresql
brew services start postgresql

# Windows - Download from https://www.postgresql.org/download/windows/
# Then create database:
createdb carbon_trace_kenya

# Optional: Create dedicated user
createuser -P carbon_user
# Grant permissions - run in psql:
# GRANT ALL PRIVILEGES ON DATABASE carbon_trace_kenya TO carbon_user;
```

**Redis:**
```bash
# Linux
apt-get install redis-server
redis-server

# Mac
brew install redis
redis-server

# Windows - Use Windows Subsystem for Linux (WSL) or Docker
```

## Step 2: Database Setup

### 2.1 Run Migrations

```bash
# Install alembic if not already installed
pip install alembic

# Run all migrations (creates tables)
alembic upgrade head
```

### 2.2 Seed Sample Data

```bash
python seed_db.py
```

You'll see:
```
[*] Creating database tables...
[OK] Tables created

[*] Seeding companies and users...
[OK] Created 10 companies with 30 users

[*] Seeding uploads...
[OK] Created sample uploads

[*] Seeding emissions data...
[OK] Created 360 emission records

[*] Seeding anomaly flags...
[OK] Created sample anomaly flags

TEST CREDENTIALS
Email: admin.evans.group@carbontrace.ke
Password: DemoPassword123
```

## Step 3: Install Dependencies

### Backend

```bash
# Install Python dependencies
pip install -r requirements.txt

# If using specific Python versions
python3.13 -m pip install -r requirements.txt
```

### Frontend

```bash
cd carbontrace

# Install Node dependencies
npm install

# Or with yarn
yarn install
```

## Step 4: Start Services

### Using Make (Linux/Mac)

```bash
# Start all services
make dev

# Or individually:
make api        # Start FastAPI server
make worker     # Start background worker
make frontend   # Start React dev server
```

### Manual Startup

**Terminal 1 - API Server:**
```bash
cd /path/to/Carbon-Trace-Kenya

# Windows
c:/python313/python.exe -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Linux/Mac
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Background Worker:**
```bash
cd /path/to/Carbon-Trace-Kenya

# Windows
c:/python313/python.exe worker.py

# Linux/Mac
python worker.py
```

**Terminal 3 - Frontend:**
```bash
cd /path/to/Carbon-Trace-Kenya/carbontrace

npm run dev
# Runs on http://localhost:5173
```

## Step 5: Test Authentication

### Using cURL

```bash
# Login and get token
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin.evans.group@carbontrace.ke",
    "password": "DemoPassword123"
  }'

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user_id": 1,
  "email": "admin.evans.group@carbontrace.ke"
}
```

### Using the API Docs

1. Open http://localhost:8000/docs
2. Click "Authorize" button (top right)
3. Use token from login response
4. All endpoints now authenticated!

### Validate Token

```bash
curl -X POST http://localhost:8000/api/auth/validate \
  -H "Content-Type: application/json" \
  -d '{"token": "your-jwt-token-here"}'
```

## Step 6: Verify All Components

### API Health

```bash
curl http://localhost:8000/docs
```

Should show interactive API documentation.

### Database Connection

```bash
# Check migrations
alembic current
# Should show: 0002_create_core_tables

# Check data
psql carbon_trace_kenya -c "SELECT COUNT(*) FROM companies;"
# Should show: 10
```

### Worker Status

Check terminal where worker is running - should show:
```
RQ Worker 'default' ready to process jobs
```

### Frontend

Open http://localhost:5173 in browser

## Common Issues

### "ModuleNotFoundError: No module named 'xxx'"

**Fix:** Install requirements
```bash
pip install -r requirements.txt
```

### "ConnectionRefusedError: can't connect to PostgreSQL"

**Fix:** Start PostgreSQL
```bash
# Check if running
psql -c "SELECT 1;"

# Or restart
docker-compose restart postgres
```

### "Redis connection refused"

**Fix:** Start Redis
```bash
# Check if running
redis-cli ping

# Or restart
docker-compose restart redis
```

### "JWT_SECRET not set"

**Fix:** Update .env file
```bash
JWT_SECRET=your-secure-secret-key-here
```

## API Endpoints (Summary)

### Authentication
- `POST /api/auth/token` - Login (get JWT)
- `POST /api/auth/signup` - Register new user
- `GET /api/auth/me` - Get current user
- `POST /api/auth/validate` - Check if token is valid
- `POST /api/auth/logout` - Logout

### Calculations
- `POST /api/calculate/{company_id}` - Calculate emissions
- `GET /api/calculate/results/{job_id}` - Get calculation results

### Uploads
- `POST /api/upload/{company_id}` - Upload file
- `GET /api/uploads/{company_id}` - List uploads

### Reports
- `GET /api/reports/{company_id}` - Generate report
- `GET /api/reports/{company_id}/xbrl` - Export as XBRL

### Anomalies
- `GET /api/anomalies/{company_id}` - List detected anomalies
- `POST /api/anomalies/{company_id}/{anomaly_id}/resolve` - Mark as resolved

### Jobs
- `GET /api/jobs` - List background jobs
- `GET /api/jobs/{job_id}` - Get job status

## Next Steps

1. **Customize for Production**
   - Change `JWT_SECRET` to a secure value
   - Update database credentials
   - Configure CORS for your frontend URL
   - Set up email/SMTP for notifications

2. **Deploy**
   - See `Dockerfile` and `docker-compose.yml`
   - Update environment variables for production
   - Run migrations on production database

3. **Development**
   - Check `tests/test_scope1.py` for example tests
   - Run tests: `pytest tests/`
   - Check code: `black api/` and `flake8 api/`

## Support

For issues or questions:
1. Check logs in terminal where service is running
2. Check `/api/docs` for interactive API documentation
3. Review error messages in browser console (frontend issues)
4. Check database: `psql carbon_trace_kenya -c "SELECT * FROM companies;"`
