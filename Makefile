.PHONY: help dev build seed demo clean test lint

# Default target
help:
	@echo "RiskRadar Development Commands"
	@echo ""
	@echo "make dev       - Start development environment"
	@echo "make build     - Build all containers"
	@echo "make seed      - Seed database with sample data"
	@echo "make demo      - Run full demo (build + seed + dev)"
	@echo "make test      - Run test suite"
	@echo "make lint      - Run code linting"
	@echo "make clean     - Clean up containers and volumes"
	@echo ""

# Start development environment
dev:
	@echo "🚀 Starting RiskRadar development environment..."
	docker-compose up --build

# Build containers
build:
	@echo "🔨 Building containers..."
	docker-compose build

# Seed database with sample data
seed:
	@echo "🌱 Seeding database with sample data..."
	docker-compose exec api python seed_data.py

# Run full demo
demo: build
	@echo "🎬 Running full RiskRadar demo..."
	docker-compose up -d postgres redis
	@echo "Waiting for database to be ready..."
	@sleep 10
	docker-compose up -d api
	@echo "Waiting for API to be ready..."
	@sleep 5
	@echo "Seeding database..."
	docker-compose exec api python seed_data.py
	@echo "Starting frontend..."
	docker-compose up -d web
	@echo ""
	@echo "🎉 RiskRadar is ready!"
	@echo "Frontend: http://localhost:3000"
	@echo "API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

# Run tests
test:
	@echo "🧪 Running test suite..."
	docker-compose exec api python -m pytest tests/ -v

# Run linting
lint:
	@echo "🔍 Running code linting..."
	docker-compose exec api python -m black . --check
	docker-compose exec api python -m isort . --check-only
	cd frontend && npm run lint

# Clean up
clean:
	@echo "🧹 Cleaning up containers and volumes..."
	docker-compose down -v
	docker system prune -f

# Stop services
stop:
	@echo "⏹️ Stopping all services..."
	docker-compose down

# Show logs
logs:
	docker-compose logs -f

# Database shell
db:
	docker-compose exec postgres psql -U riskradar -d riskradar

# API shell
shell:
	docker-compose exec api python

# Frontend shell  
frontend-shell:
	docker-compose exec web sh