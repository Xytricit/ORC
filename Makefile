# Makefile for ORC project
# Quick reference for common development tasks

.PHONY: help install install-dev install-all test test-cov lint format clean build publish docker run-web run-cli docs pre-commit setup

help:
	@echo "ORC Development Commands:"
	@echo "========================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install         Install core dependencies"
	@echo "  make install-dev     Install development dependencies"
	@echo "  make install-all     Install all dependencies (core + web + dev)"
	@echo "  make setup           Complete development setup (install + pre-commit)"
	@echo ""
	@echo "Testing:"
	@echo "  make test            Run tests"
	@echo "  make test-cov        Run tests with coverage report"
	@echo "  make test-fast       Run tests in parallel"
	@echo "  make tox             Run tests across Python versions"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint            Run linters (flake8, black --check, isort --check)"
	@echo "  make format          Auto-format code (black, isort)"
	@echo "  make type            Run type checker (mypy)"
	@echo "  make security        Run security checks (bandit)"
	@echo "  make pre-commit      Run all pre-commit hooks"
	@echo ""
	@echo "Building & Publishing:"
	@echo "  make clean           Remove build artifacts"
	@echo "  make build           Build distribution packages"
	@echo "  make publish         Publish to PyPI (requires credentials)"
	@echo "  make publish-test    Publish to TestPyPI"
	@echo ""
	@echo "Running:"
	@echo "  make run-web         Start web dashboard"
	@echo "  make run-cli         Start CLI in interactive mode"
	@echo "  make docker          Build Docker image"
	@echo "  make docker-run      Run Docker container"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs            Build documentation"
	@echo "  make docs-serve      Build and serve documentation"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean-pyc       Remove Python cache files"
	@echo "  make clean-test      Remove test artifacts"
	@echo "  make clean-build     Remove build artifacts"

# Installation
install:
	pip install -e .

install-dev:
	pip install -r requirements.txt -r requirements-dev.txt -r requirements-web.txt

install-all:
	pip install -e ".[all,dev]"

setup: install-dev
	pre-commit install
	@echo "✅ Development environment ready!"

# Testing
test:
	pytest orc/tests/ -v

test-cov:
	pytest orc/tests/ -v --cov=orc --cov-report=html --cov-report=term-missing
	@echo "📊 Coverage report: htmlcov/index.html"

test-fast:
	pytest orc/tests/ -v -n auto

test-watch:
	pytest-watch orc/tests/ -v

tox:
	tox

# Code Quality
lint:
	@echo "Running flake8..."
	flake8 orc --count --statistics
	@echo "Checking code formatting..."
	black --check orc
	@echo "Checking import sorting..."
	isort --check-only orc
	@echo "✅ All linting checks passed!"

format:
	@echo "Formatting code with black..."
	black orc
	@echo "Sorting imports with isort..."
	isort orc
	@echo "✅ Code formatted!"

type:
	mypy orc --ignore-missing-imports

security:
	bandit -r orc -ll

pre-commit:
	pre-commit run --all-files

# Building
clean: clean-pyc clean-test clean-build

clean-pyc:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*.pyd' -delete

clean-test:
	rm -rf .pytest_cache
	rm -rf .tox
	rm -rf htmlcov
	rm -f .coverage
	rm -f coverage.xml

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf orc.egg-info

build: clean
	python -m build

build-wheel:
	python setup.py bdist_wheel

build-sdist:
	python setup.py sdist

# Publishing
publish: build
	twine upload dist/*

publish-test: build
	twine upload --repository testpypi dist/*

check-dist:
	twine check dist/*

# Running
run-web:
	python -m orc.web.app

run-cli:
	orc chat

run-serve:
	orc serve

# Docker
docker:
	docker build -t orc:latest -f orc/Dockerfile .

docker-run:
	docker run -it --rm -p 5000:5000 orc:latest

docker-test:
	docker run --rm orc:latest orc --help

# Documentation
docs:
	@echo "Building documentation..."
	sphinx-build -b html docs docs/_build/html
	@echo "📚 Documentation: docs/_build/html/index.html"

docs-serve: docs
	python -m http.server -d docs/_build/html 8000

# Database
db-init:
	python -c "from orc.web.database import init_db; init_db()"

db-migrate:
	python orc/scripts/migrate.py

# Development helpers
shell:
	ipython

watch-tests:
	pytest-watch orc/tests/

check: lint test
	@echo "✅ All checks passed!"

ci: lint test-cov security
	@echo "✅ CI checks complete!"

# Version bumping (requires bump2version)
bump-patch:
	bump2version patch

bump-minor:
	bump2version minor

bump-major:
	bump2version major
