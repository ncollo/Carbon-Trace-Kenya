# CarbonTrace Frontend

Modern React frontend for CarbonTrace - an AI-powered transport emission disclosure platform for Kenyan institutions.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **shadcn/ui** - UI components
- **React Router** - Navigation
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **Lucide React** - Icons

## Prerequisites

- Node.js 18+ 
- npm or yarn
- FastAPI backend running on port 8000

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd CarbonTrace-Frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and set your API base URL:
```
VITE_API_BASE_URL=http://localhost:8000
```

## Development

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Build

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

## Features

- **Dashboard** - Overview of carbon emission statistics
- **Vehicles** - Manage fleet vehicles
- **Reports** - Generate and download NSE-compliant carbon reports
- **Authentication** - Secure login system
- **Responsive Design** - Works on desktop and mobile

## Backend Integration

This frontend is designed to work with a FastAPI backend. Ensure your backend provides the following API endpoints:

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/me` - Get current user
- `POST /auth/logout` - User logout

### Vehicles
- `GET /vehicles` - List all vehicles
- `POST /vehicles` - Create vehicle
- `PUT /vehicles/{id}` - Update vehicle
- `DELETE /vehicles/{id}` - Delete vehicle

### Fuel Records
- `GET /fuel-records` - List fuel records
- `POST /fuel-records` - Create fuel record

### Travel Receipts
- `GET /travel-receipts` - List travel receipts
- `POST /travel-receipts` - Create travel receipt

### Reports
- `GET /reports` - List emission reports
- `POST /reports/generate` - Generate new report
- `GET /reports/{id}/download` - Download report PDF

### Dashboard
- `GET /dashboard/stats` - Get dashboard statistics

## PostgreSQL Migration Guide for Backend

The backend currently uses SQLite. Here's how to migrate to PostgreSQL:

### 1. Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Windows
# Download from https://www.postgresql.org/download/windows/
```

### 2. Create Database
```bash
sudo -u postgres psql
CREATE DATABASE carbontrace;
CREATE USER carbontrace_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE carbontrace TO carbontrace_user;
\q
```

### 3. Update Backend Dependencies
Add to your `requirements.txt`:
```
psycopg2-binary==2.9.9
asyncpg==0.29.0
```

### 4. Update Database Configuration
In your FastAPI backend, update the database URL:

```python
# SQLite (current)
DATABASE_URL = "sqlite:///./carbontrace.db"

# PostgreSQL (new)
DATABASE_URL = "postgresql://carbontrace_user:your_password@localhost/carbontrace"
```

### 5. Update SQLAlchemy Models
If using SQLAlchemy, update the engine:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite
# engine = create_engine("sqlite:///./carbontrace.db")

# PostgreSQL
engine = create_engine("postgresql://carbontrace_user:your_password@localhost/carbontrace")
```

### 6. Run Migrations
If using Alembic:
```bash
alembic upgrade head
```

Or create tables directly:
```python
Base.metadata.create_all(bind=engine)
```

### 7. Update Environment Variables
Create `.env` file for backend:
```
DATABASE_URL=postgresql://carbontrace_user:your_password@localhost/carbontrace
```

### 8. Test Connection
```python
import asyncpg

async def test_connection():
    conn = await asyncpg.connect("postgresql://carbontrace_user:your_password@localhost/carbontrace")
    version = await conn.fetchval('SELECT version()')
    print(version)
    await conn.close()
```

## Team

- **Team:** EmitIQ
- **Project:** CarbonTrace

## License

MIT
