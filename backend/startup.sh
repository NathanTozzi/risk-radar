#!/bin/bash

# Backend startup script for Render deployment
set -e

PORT=${PORT:-8000}

echo "🚀 Starting RiskRadar backend..."
echo "📊 Setting up database..."

# Create tables
python -c "from database import create_db_and_tables; create_db_and_tables()"

# Seed database if empty
python -c "
from database import get_session
from models import Company
from sqlmodel import select
import asyncio
from seed_data import seed_database

try:
    session = next(get_session())
    companies = session.exec(select(Company)).all()
    count = len(companies)
    if count == 0:
        print('🌱 Seeding database with sample data...')
        asyncio.run(seed_database())
        print('✅ Database seeded successfully!')
    else:
        print(f'📊 Database already contains {count} companies')
    session.close()
except Exception as e:
    print(f'⚠️  Database seeding failed: {e}')
    print('Continuing without sample data...')
"

echo "🌐 Starting API server on port ${PORT}..."
exec uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1