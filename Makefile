# Agentic Integration Platform Makefile
.PHONY: help install dev test lint format type-check security clean build run docker-build docker-run deploy

# Default target
help: ## Show this help message
	@echo "Agentic Integration Platform - Development Commands"
	@echo "=================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development Setup
install: ## Install dependencies using custom script
	chmod +x install.sh
	./install.sh

install-poetry: ## Install dependencies using Poetry directly
	poetry install --no-cache
	poetry run pre-commit install

install-no-root: ## Install dependencies without installing the current project
	poetry install --no-cache --no-root

install-ml: ## Install with ML dependencies (PyTorch, etc.)
	poetry install --extras ml --no-cache

dev: ## Start development environment with sample data
	@echo "🚀 Starting development environment..."
	docker-compose up -d postgres redis neo4j qdrant
	@echo "⏳ Waiting for databases to be ready..."
	sleep 10
	@echo "📊 Initializing realistic sample data..."
	poetry run python scripts/init_dev_data.py
	@echo "🌟 Starting API server..."
	DEBUG=true poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-clean: ## Start development environment without sample data
	@echo "🚀 Starting clean development environment..."
	docker-compose up -d postgres redis neo4j qdrant
	@echo "⏳ Waiting for databases to be ready..."
	sleep 5
	@echo "🌟 Starting API server..."
	DEBUG=true poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-data: ## Initialize development sample data only
	@echo "📊 Initializing realistic sample data..."
	poetry run python scripts/init_dev_data.py

dev-down: ## Stop development environment
	@echo "🛑 Stopping development environment..."
	docker-compose down

# Code Quality
lint: ## Run linting with Ruff
	poetry run ruff check app/ tests/

format: ## Format code with Black and Ruff
	poetry run black app/ tests/
	poetry run ruff check --fix app/ tests/

type-check: ## Run type checking with MyPy
	poetry run mypy app/

security: ## Run security scan with Bandit
	poetry run bandit -r app/

# Testing
test: ## Run all tests
	poetry run pytest --disable-warnings

test-fast: ## Run tests with timeout and fail fast
	poetry run pytest -x --timeout=30 --tb=short --disable-warnings

test-unit: ## Run unit tests only
	poetry run pytest tests/unit/ --timeout=20

test-integration: ## Run integration tests only
	poetry run pytest tests/integration/ --timeout=30

test-coverage: ## Run tests with coverage report
	poetry run pytest --cov=app --cov-report=html --cov-report=term

# Database
db-upgrade: ## Run database migrations
	poetry run alembic upgrade head

db-downgrade: ## Rollback last migration
	poetry run alembic downgrade -1

db-revision: ## Create new migration
	poetry run alembic revision --autogenerate -m "$(MESSAGE)"

db-reset: ## Reset database (WARNING: destroys all data)
	docker-compose down -v
	docker-compose up -d postgres
	sleep 5
	poetry run alembic upgrade head

# Docker
docker-build: ## Build Docker image
	docker build -t agentic-integration-platform:latest .

docker-run: ## Run application in Docker
	docker run -p 8000:8000 --env-file .env agentic-integration-platform:latest

docker-compose-up: ## Start all services with Docker Compose
	docker-compose up -d

docker-compose-down: ## Stop all services
	docker-compose down

docker-compose-logs: ## View logs from all services
	docker-compose logs -f

# Production
build: ## Build production-ready application
	poetry build

deploy-staging: ## Deploy to staging environment
	@echo "Deploying to staging..."
	# Add staging deployment commands here

deploy-production: ## Deploy to production environment
	@echo "Deploying to production..."
	# Add production deployment commands here

# Monitoring
logs: ## View application logs
	docker-compose logs -f app

metrics: ## Open Prometheus metrics
	open http://localhost:9090

grafana: ## Open Grafana dashboards
	open http://localhost:3000

jaeger: ## Open Jaeger tracing UI
	open http://localhost:16686

# Utilities
clean: ## Clean up temporary files and caches
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".mypy_cache" -delete
	find . -type d -name ".ruff_cache" -delete
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/

shell: ## Start interactive Python shell with app context
	poetry run python -c "from app.main import app; import IPython; IPython.embed()"

docs: ## Generate API documentation
	poetry run python -c "from app.main import app; import json; print(json.dumps(app.openapi(), indent=2))" > openapi.json

check: lint type-check security test ## Run all quality checks

ci: install check ## Run CI pipeline locally

# Environment
env-copy: ## Copy environment template
	cp .env.example .env
	@echo "Environment file created. Please update .env with your configuration."

env-check: ## Check environment configuration
	poetry run python -c "from app.core.config import settings; print('Configuration loaded successfully')"

# Knowledge Graph
kg-init: ## Initialize knowledge graph schema
	@echo "Initializing knowledge graph..."
	# Add Neo4j schema initialization commands

kg-backup: ## Backup knowledge graph data
	@echo "Backing up knowledge graph..."
	# Add Neo4j backup commands

kg-restore: ## Restore knowledge graph data
	@echo "Restoring knowledge graph..."
	# Add Neo4j restore commands

# AI Services
ai-test: ## Test AI service connections
	poetry run python -c "from app.services.ai import test_connections; test_connections()"

# Vector Database
vector-init: ## Initialize vector database collections
	@echo "Initializing vector database..."
	# Add Qdrant collection initialization

vector-backup: ## Backup vector database
	@echo "Backing up vector database..."
	# Add Qdrant backup commands
