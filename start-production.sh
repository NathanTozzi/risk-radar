#!/bin/bash

# Production startup script for Render
set -e

# Set default port if not provided
PORT=${PORT:-10000}

echo "🚀 Starting RiskRadar production server..."

# Change to backend directory
cd backend

# Run database migrations
echo "📊 Setting up database..."
python -c "from database import create_db_and_tables; create_db_and_tables()"

# Seed database if it's empty
echo "🌱 Checking for existing data..."
python -c "
from database import get_session
from models import Company
from sqlmodel import select
try:
    session = next(get_session())
    companies = session.exec(select(Company)).all()
    count = len(companies)
    if count == 0:
        print('Seeding database with initial data...')
        import asyncio
        from seed_data import seed_database
        asyncio.run(seed_database())
    else:
        print(f'Database already contains {count} companies')
    session.close()
except Exception as e:
    print(f'Database check failed: {e}')
"

# Start FastAPI server with static file serving
echo "🌐 Starting API server on port ${PORT}..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1