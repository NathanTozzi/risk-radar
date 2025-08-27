# RiskRadar Development Guide

## Prerequisites

### Option 1: Docker (Recommended)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) - for Mac/Windows
- Docker Compose (included with Docker Desktop)

### Option 2: Local Development
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+ (optional, for background tasks)

## Quick Start Options

### 🐳 Docker Development (Recommended)

```bash
# Install Docker Desktop first, then:
make demo
```

This will:
- Build all containers
- Start database and services
- Seed with sample data  
- Launch frontend at http://localhost:3000
- API at http://localhost:8000

### 🔧 Local Development (Without Docker)

If Docker isn't available, you can run locally:

#### 1. Setup Backend
```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup local PostgreSQL database
# Update DATABASE_URL in .env to point to your local PostgreSQL

# Run migrations and seed data
python seed_data.py

# Start API server
uvicorn main:app --reload --port 8000
```

#### 2. Setup Frontend
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### 3. Access Application
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Development Workflow

### With Docker
```bash
# Start all services
make dev

# View logs
make logs

# Access database
make db

# Run tests
make test

# Clean up
make clean
```

### Local Development
```bash
# Backend (Terminal 1)
cd backend
source .venv/bin/activate
uvicorn main:app --reload

# Frontend (Terminal 2)
cd frontend  
npm run dev

# Tests (Terminal 3)
cd backend
python -m pytest
```

## Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Database (adjust for your setup)
DATABASE_URL=postgresql://user:password@localhost:5432/riskradar

# Optional: Redis for background tasks
REDIS_URL=redis://localhost:6379/0

# Data source settings
OSHA_SCRAPE_THROTTLE_MS=2000
NEWS_RSS_FEEDS=https://feeds.construction.com/news/rss
```

## Troubleshooting

### Docker Issues
- **Port conflicts**: Change ports in `docker-compose.yml`
- **Permission issues**: Run `docker-compose down` and restart Docker Desktop
- **Build errors**: Run `make clean && make build`

### Local Development Issues
- **Database connection**: Ensure PostgreSQL is running and credentials are correct
- **Python dependencies**: Make sure you're in the virtual environment
- **Node modules**: Delete `node_modules` and run `npm install`

### Database Setup (Local)
```sql
-- Create database and user in PostgreSQL
CREATE DATABASE riskradar;
CREATE USER riskradar WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE riskradar TO riskradar;
```

## Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## API Documentation

Once running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Key Endpoints

- `GET /companies` - List all companies
- `GET /events` - List safety incidents  
- `GET /opportunities` - List target opportunities
- `POST /opportunities/rebuild` - Regenerate scores
- `POST /outreach/generate` - Create outreach kit
- `POST /ingest/run` - Run data ingestion

## Sample Data

The application includes comprehensive sample data:
- 8 subcontractors with safety records
- 6 general contractors 
- 4 property owners
- 30+ safety incidents and violations
- 10+ target opportunities with outreach kits

## Next Steps

1. **Develop**: Add features, modify scoring, enhance UI
2. **Demo**: Show the application to stakeholders  
3. **Deploy**: Move to production environment

For deployment options, see `DEPLOYMENT.md`.