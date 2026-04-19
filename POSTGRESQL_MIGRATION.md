# PostgreSQL Migration Guide for CarbonTrace Backend

This guide provides step-by-step instructions for migrating the CarbonTrace backend from SQLite to PostgreSQL.

## Why PostgreSQL?

PostgreSQL offers several advantages over SQLite for production:
- Better concurrency support
- Advanced features (JSONB, full-text search, etc.)
- Better performance for large datasets
- More robust security features
- Better suited for multi-user environments

## Migration Steps

### 1. Install PostgreSQL

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### macOS
```bash
brew install postgresql
brew services start postgresql
```

#### Windows
Download and install from: https://www.postgresql.org/download/windows/

### 2. Create Database and User

```bash
# Access PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE carbontrace;

# Create user with password
CREATE USER carbontrace_user WITH PASSWORD 'your_secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE carbontrace TO carbontrace_user;

# Exit
\q
```

### 3. Update Python Dependencies

Add to your `requirements.txt`:
```txt
psycopg2-binary==2.9.9
asyncpg==0.29.0
```

Install the new dependencies:
```bash
pip install -r requirements.txt
```

### 4. Update Backend Configuration

#### Option A: Using SQLAlchemy (Sync)

```python
# In your database configuration file
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Old (SQLite)
# DATABASE_URL = "sqlite:///./carbontrace.db"
# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# New (PostgreSQL)
DATABASE_URL = "postgresql://carbontrace_user:your_secure_password@localhost/carbontrace"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
```

#### Option B: Using SQLAlchemy (Async)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import declarative_base

# Old (SQLite)
# DATABASE_URL = "sqlite+aiosqlite:///./carbontrace.db"

# New (PostgreSQL)
DATABASE_URL = "postgresql+asyncpg://carbontrace_user:your_secure_password@localhost/carbontrace"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()
```

### 5. Update Environment Variables

Create or update `.env` file:
```env
DATABASE_URL=postgresql://carbontrace_user:your_secure_password@localhost/carbontrace
```

### 6. Migrate Data

#### Option A: Using Alembic (Recommended)

If you're using Alembic for migrations:

```bash
# Generate migration script
alembic revision --autogenerate -m "Migrate to PostgreSQL"

# Apply migration
alembic upgrade head
```

#### Option B: Manual Data Migration

Create a migration script:

```python
import sqlite3
import asyncpg
import asyncio

async def migrate_data():
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('carbontrace.db')
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    pg_conn = await asyncpg.connect(
        "postgresql://carbontrace_user:your_secure_password@localhost/carbontrace"
    )
    
    # Migrate vehicles
    sqlite_cursor.execute("SELECT * FROM vehicles")
    vehicles = sqlite_cursor.fetchall()
    
    for vehicle in vehicles:
        await pg_conn.execute(
            """
            INSERT INTO vehicles (id, registration_number, vehicle_type, fuel_type, year, mileage)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            vehicle['id'],
            vehicle['registration_number'],
            vehicle['vehicle_type'],
            vehicle['fuel_type'],
            vehicle['year'],
            vehicle['mileage']
        )
    
    # Repeat for other tables...
    
    await pg_conn.close()
    sqlite_conn.close()

asyncio.run(migrate_data())
```

### 7. Update FastAPI Dependencies

If using FastAPI with SQLAlchemy:

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 8. Test the Migration

```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Test connection
python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('postgresql://carbontrace_user:your_secure_password@localhost/carbontrace'))"

# Run your FastAPI app
uvicorn main:app --reload
```

### 9. Verify Data

Connect to PostgreSQL and verify:
```bash
sudo -u postgres psql -d carbontrace

# Check tables
\dt

# Check data
SELECT * FROM vehicles;
SELECT * FROM fuel_records;
```

## Additional PostgreSQL Configuration

### Enable Extensions (Optional)

```sql
-- Connect to database
\c carbontrace

-- Enable useful extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
```

### Performance Tuning

Edit `postgresql.conf`:
```ini
# Memory settings
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB

# Connection settings
max_connections = 100

# WAL settings
wal_buffers = 16MB
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## Backup Strategy

### Automated Backups

Create a backup script:

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/carbontrace"
mkdir -p $BACKUP_DIR

pg_dump -U carbontrace_user carbontrace > $BACKUP_DIR/carbontrace_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "carbontrace_*.sql" -mtime +7 -delete
```

Add to crontab:
```bash
crontab -e
# Daily backup at 2 AM
0 2 * * * /path/to/backup.sh
```

## Troubleshooting

### Connection Issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check logs
sudo tail -f /var/log/postgresql/postgresql-*.log

# Test connection
psql -U carbontrace_user -d carbontrace -h localhost
```

### Permission Issues

```sql
-- Grant permissions again
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO carbontrace_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO carbontrace_user;
```

## Rollback Plan

If you need to rollback to SQLite:

1. Stop using PostgreSQL
2. Restore SQLite database from backup
3. Update `.env` to use SQLite URL
4. Update database configuration in code
5. Restart application

## Production Considerations

For production deployment:

1. Use a managed PostgreSQL service (AWS RDS, Google Cloud SQL, etc.)
2. Enable SSL connections
3. Use connection pooling (PgBouncer)
4. Set up read replicas for scaling
5. Implement proper monitoring and alerting
6. Regular backup strategy
7. Use environment-specific configurations

## Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [FastAPI Database Tutorial](https://fastapi.tiangolo.com/tutorial/sql-databases/)
