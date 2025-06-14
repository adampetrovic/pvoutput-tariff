# PVOutput Tariff Uploader - Development Makefile

.PHONY: help install install-dev test test-cov lint format type-check security check clean build docker run validate

# Default target
help: ## Show this help message
	@echo "PVOutput Tariff Uploader - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make install-dev    # Setup development environment"
	@echo "  make check          # Run all quality checks"
	@echo "  make test-cov       # Run tests with coverage"
	@echo "  make docker         # Build Docker image"

# Development setup
install: ## Install production dependencies
	pip install pipenv
	pipenv install

install-dev: ## Install development dependencies
	pip install pipenv
	pipenv install --dev
	pipenv run pre-commit install

# Testing
test: ## Run tests
	pipenv run pytest test/ --tb=short

test-cov: ## Run tests with coverage report
	pipenv run pytest test/ --cov=uploader --cov-report=html --cov-report=term-missing --cov-report=xml

test-verbose: ## Run tests with verbose output
	pipenv run pytest test/ -v

test-failed: ## Run only failed tests
	pipenv run pytest test/ --lf

# Code quality
lint: ## Run linting checks
	pipenv run flake8 uploader.py test/

format: ## Format code
	pipenv run black uploader.py test/
	pipenv run isort uploader.py test/

format-check: ## Check code formatting
	pipenv run black --check uploader.py test/
	pipenv run isort --check-only uploader.py test/

type-check: ## Run type checking
	pipenv run mypy uploader.py

# Security
security: ## Run security checks
	pipenv run bandit -r uploader.py
	pipenv run safety scan

security-audit: ## Run comprehensive security audit
	pipenv run bandit -r uploader.py -f json -o bandit-report.json
	pipenv run safety scan --output json --output-file safety-report.json
	pipenv run pip-audit --format=json --output=pip-audit-report.json

# Combined checks
check: lint format-check type-check security test ## Run all quality checks

check-ci: ## Run CI-style checks (used in GitHub Actions)
	pipenv run flake8 uploader.py test/
	pipenv run black --check uploader.py test/
	pipenv run isort --check-only uploader.py test/
	pipenv run mypy uploader.py
	pipenv run pytest test/ --cov=uploader --cov-report=xml

# Configuration validation
validate: ## Validate test configurations
	@echo "Validating test configurations..."
	@pipenv run python -c "\
	from config_schema import validate_config; \
	import yaml; \
	import os; \
	configs = ['test/config.yaml', 'test/config_august.yaml']; \
	for config_file in configs: \
		if os.path.exists(config_file): \
			print(f'Validating {config_file}...'); \
			with open(config_file, 'r') as f: \
				config = yaml.safe_load(f); \
			validate_config(config); \
			print(f'✅ {config_file} is valid'); \
		else: \
			print(f'⚠️  {config_file} not found'); \
	print('All configurations validated successfully!')"

# Dependencies
deps-update: ## Update dependencies
	@if [ ! -f Pipfile ]; then echo "❌ No Pipfile found. Run 'make install' first."; exit 1; fi
	pipenv update

deps-outdated: ## Check for outdated dependencies
	@if [ ! -f Pipfile ]; then echo "❌ No Pipfile found. Run 'make install' first."; exit 1; fi
	pipenv update --outdated

deps-graph: ## Show dependency graph
	@if [ ! -f Pipfile ]; then echo "❌ No Pipfile found. Run 'make install' first."; exit 1; fi
	@echo "📊 Dependency graph:"
	pipenv graph || (echo "❌ Failed to generate dependency graph. Try running 'make install' first." && exit 1)

deps-licenses: ## Show dependency licenses
	@if [ ! -f Pipfile ]; then echo "❌ No Pipfile found. Run 'make install' first."; exit 1; fi
	pipenv run pip-licenses

# Docker
docker: ## Build Docker image
	docker build -t pvoutput-tariff:latest .

docker-multi: ## Build multi-platform Docker image
	docker buildx build --platform linux/amd64,linux/arm64 -t pvoutput-tariff:latest .

docker-test: ## Test Docker image
	docker run --rm pvoutput-tariff:latest --help

docker-run: ## Run Docker container with test config
	@echo "Running Docker container with test config..."
	@echo "Note: This will fail without valid API credentials"
	docker run --rm \
		-v $(PWD)/test/config.yaml:/config/config.yaml \
		pvoutput-tariff:latest || true

# Application
run: ## Run the application with test config
	@echo "Running application with test config..."
	@echo "Note: Set PVOUTPUT_API_KEY and PVOUTPUT_SYSTEM_ID environment variables"
	pipenv run python uploader.py --config test/config.yaml

run-help: ## Show application help
	pipenv run python uploader.py --help

# Cleanup
clean: ## Clean temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -name "*.sarif" -delete
	find . -name "*-report.json" -delete

clean-all: clean ## Clean everything including virtual environment
	pipenv --rm

# Build and packaging
build: ## Build Python package
	pipenv run python -m build

build-check: ## Check built package
	pipenv run python -m twine check dist/*

# Release helpers
tag: ## Create a new version tag (usage: make tag VERSION=v1.2.3)
	@if [ -z "$(VERSION)" ]; then echo "Usage: make tag VERSION=v1.2.3"; exit 1; fi
	git tag $(VERSION)
	git push origin $(VERSION)
	@echo "Tag $(VERSION) created and pushed. This will trigger a release."

# Development utilities
shell: ## Open pipenv shell
	pipenv shell

requirements: ## Generate requirements.txt from Pipfile
	pipenv requirements > requirements.txt

requirements-dev: ## Generate dev-requirements.txt from Pipfile
	pipenv requirements --dev > dev-requirements.txt

# GitHub Actions helpers
act-ci: ## Run GitHub Actions CI locally (requires 'act')
	act -j test

act-docker: ## Run GitHub Actions Docker workflow locally (requires 'act')
	act -j build

# Pre-commit
pre-commit: ## Run pre-commit on all files
	pipenv run pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks
	pipenv run pre-commit autoupdate

# Documentation
docs: ## Generate documentation (placeholder)
	@echo "Documentation generation not implemented yet"

# IDE setup
vscode: ## Setup VS Code settings
	mkdir -p .vscode
	@echo '{\n  "python.defaultInterpreterPath": ".venv/bin/python",\n  "python.linting.enabled": true,\n  "python.linting.flake8Enabled": true,\n  "python.formatting.provider": "black",\n  "python.sortImports.args": ["--profile", "black"]\n}' > .vscode/settings.json
	@echo "VS Code settings created in .vscode/settings.json"

# Quick development workflow
dev: install-dev validate check ## Setup development environment and run checks

quick-check: lint type-check test ## Quick checks for development

# Release preparation
prepare-release: check security-audit build ## Prepare for release (run all checks and build)

# Monitoring and profiling
profile: ## Profile the application (basic timing)
	@echo "Profiling application..."
	time pipenv run python uploader.py --config test/config.yaml || true

# Environment info
env-info: ## Show environment information
	@echo "Python version:"
	python --version
	@echo ""
	@echo "Pipenv version:"
	pipenv --version
	@echo ""
	@echo "Virtual environment location:"
	pipenv --venv 2>/dev/null || echo "No virtual environment found"
	@echo ""
	@echo "Installed packages:"
	pipenv run pip list

# Git helpers
git-clean: ## Clean git repository
	git clean -fdx

git-reset: ## Reset to clean state (WARNING: destructive)
	@echo "This will reset your repository to a clean state. Continue? [y/N]"
	@read answer && [ "$$answer" = "y" ] || exit 1
	git reset --hard HEAD
	git clean -fdx