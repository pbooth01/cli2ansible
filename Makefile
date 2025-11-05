.PHONY: help install dev-install test lint type-check format clean docker-up docker-down docker-logs migrate lock

help:
	@echo "Available commands:"
	@echo "  install       - Install production dependencies"
	@echo "  dev-install   - Install development dependencies"
	@echo "  test          - Run tests with coverage"
	@echo "  lint          - Run linting checks"
	@echo "  type-check    - Run MyPy type checking"
	@echo "  format        - Format code with ruff and black"
	@echo "  clean         - Remove build artifacts and cache"
	@echo "  docker-up     - Start Docker services"
	@echo "  docker-down   - Stop Docker services"
	@echo "  docker-logs   - Show Docker logs"
	@echo "  migrate       - Run database migrations"
	@echo "  lock          - Update poetry.lock file"

install:
	poetry install --only main

dev-install:
	poetry install
	poetry run pre-commit install

lock:
	poetry lock

test:
	poetry run pytest --cov=src --cov-report=html --cov-report=term

lint:
	poetry run ruff check .

type-check:
	poetry run mypy src

format:
	poetry run ruff check --fix .
	poetry run black .

clean:
	rm -rf build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov
	rm -rf .venv

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f app

migrate:
	poetry run alembic upgrade head
