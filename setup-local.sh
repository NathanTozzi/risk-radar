#!/bin/bash

# RiskRadar Local Development Setup
# For systems without Docker

set -e

echo "🎯 RiskRadar Local Development Setup"
echo "====================================="

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    echo "Please install Python 3.11+ from https://python.org"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    echo "Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

if ! command -v psql &> /dev/null; then
    echo "⚠️ PostgreSQL not found. You'll need to install and configure PostgreSQL"
    echo "Or update DATABASE_URL in .env to use SQLite for testing"
fi

echo "✅ Prerequisites check complete"

# Setup backend
echo ""
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Backend setup complete"

# Setup frontend  
echo ""
echo "🎨 Setting up frontend..."
cd ../frontend

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

echo "✅ Frontend setup complete"

# Create .env file
echo ""
echo "⚙️ Setting up configuration..."
cd ..

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env file from template"
    echo "⚠️ Please update DATABASE_URL in .env for your PostgreSQL setup"
fi

# Test backend imports
echo ""
echo "🧪 Testing backend setup..."
cd backend
source .venv/bin/activate

python -c "
try:
    from models import Company, CompanyType
    print('✅ Models import successfully')
    
    company = Company(name='Test', type=CompanyType.GC, normalized_name='TEST')
    print('✅ Model creation works')
    print('🎉 Backend setup verified!')
except Exception as e:
    print(f'❌ Backend test failed: {e}')
    exit(1)
"

echo ""
echo "🎉 Local development setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure your database connection in .env"
echo "2. Start the backend:"
echo "   cd backend && source .venv/bin/activate && uvicorn main:app --reload"
echo "3. In another terminal, start the frontend:"
echo "   cd frontend && npm run dev"
echo ""
echo "Access points:"
echo "- Frontend: http://localhost:3000"
echo "- API: http://localhost:8000"  
echo "- API Docs: http://localhost:8000/docs"