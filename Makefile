help:
	@echo "Locust Flow - Makefile Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install dependencies"
	@echo "  make install-dev      Install dev dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run unit tests"
	@echo "  make coverage         Run tests with coverage report"
	@echo "  make test-verbose     Run tests with verbose output"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Run all linters"
	@echo "  make format           Format code with black and isort"
	@echo "  make format-check     Check code formatting"
	@echo ""
	@echo "Security:"
	@echo "  make security         Run security scans"
	@echo "  make bandit           Run bandit security scanner"
	@echo "  make safety           Check dependencies for vulnerabilities"
	@echo ""
	@echo "Configuration:"
	@echo "  make generate-config  Generate new config file"
	@echo ""
	@echo "Validation:"
	@echo "  make validate-configs Validate YAML config files"
	@echo ""
	@echo "Running:"
	@echo "  make run              Start Locust web UI"
	@echo "  make run-headless     Run headless load test"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            Remove cache and temp files"
	@echo ""
	@echo "CI:"
	@echo "  make ci               Run all CI checks (test, lint, security)"
	@echo "  make all              Run everything (install, test, lint, security)"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

install-dev:
	@echo "Installing dev dependencies..."
	pip install -r requirements.txt
	pip install pytest pytest-cov flake8 pylint black isort bandit safety yamllint

test:
	@echo "Running unit tests..."
	python tests/run_tests.py

test-verbose:
	@echo "Running unit tests (verbose)..."
	python -m unittest discover tests -v

coverage:
	@echo "Running tests with coverage..."
	pytest tests/ --cov=framework --cov-report=html --cov-report=term
	@echo ""
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	@echo "Running linters..."
	@echo "\n=== Flake8 ==="
	flake8 framework/ tests/ --max-line-length=127 --exclude=__pycache__,.venv || true
	@echo "\n=== Pylint ==="
	pylint framework/ --max-line-length=127 --exit-zero || true

format:
	@echo "Formatting code..."
	black framework/ tests/ config_generator.py main.py
	isort framework/ tests/ config_generator.py main.py
	@echo "Code formatted successfully!"

format-check:
	@echo "Checking code formatting..."
	black --check framework/ tests/ config_generator.py main.py
	isort --check-only framework/ tests/ config_generator.py main.py

security:
	@echo "Running security scans..."
	@$(MAKE) bandit
	@$(MAKE) safety

bandit:
	@echo "\n=== Bandit Security Scan ==="
	bandit -r framework/ || true

safety:
	@echo "\n=== Safety Dependency Check ==="
	safety scan || true

generate-config:
	@echo "Generating new config file..."
	python config_generator.py

validate-configs:
	@output=$$(python validate_config.py configs/*.yaml configs/*.yml 2>&1); \
	if [ $$? -eq 0 ]; then \
		echo "Config validation passed"; \
		exit 0; \
	else \
		echo "$$output"; \
		exit 1; \
	fi

run: validate-configs
	@echo "Starting Locust web UI..."
	@echo "Open http://localhost:8089 in your browser"
	locust -f main.py

run-headless: validate-configs
	@echo "Running headless load test..."
	@echo "Users: 10, Spawn rate: 2, Duration: 60s"
	locust -f main.py --headless -u 10 -r 2 -t 60s

clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf bandit-report.json
	@echo "Cleanup complete!"

ci: test lint security validate-configs
	@echo ""
	@echo "==================================="
	@echo "All CI checks completed!"
	@echo "==================================="

all: install-dev test lint security validate-configs
	@echo ""
	@echo "==================================="
	@echo "All tasks completed successfully!"
	@echo "==================================="
