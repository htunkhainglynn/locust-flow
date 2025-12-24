help:
	@echo "Locust Flow - Makefile Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make venv             Create virtual environment"
	@echo "  make install          Install dependencies"
	@echo "  make install-dev      Install dev dependencies"
	@echo "  make install-hooks    Install git pre-commit hooks"
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

venv:
	@echo "Creating virtual environment..."
	python3 -m venv .venv
	@echo ""
	@echo "Virtual environment created!"
	@echo "Activate it with:"
	@echo "  source .venv/bin/activate    (Linux/Mac)"
	@echo "  .venv\\Scripts\\activate      (Windows)"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

install-dev:
	@echo "Installing dev dependencies..."
	pip install -r requirements.txt
	pip install pytest pytest-cov flake8 pylint black isort bandit safety yamllint

install-hooks:
	@echo "Installing git pre-commit hooks..."
	@if [ ! -d .git ]; then \
		echo "Error: Not a git repository. Run 'git init' first."; \
		exit 1; \
	fi
	@echo '#!/bin/bash' > .git/hooks/pre-commit
	@echo '' >> .git/hooks/pre-commit
	@echo 'echo "Running pre-commit checks..."' >> .git/hooks/pre-commit
	@echo '' >> .git/hooks/pre-commit
	@echo '# Format code' >> .git/hooks/pre-commit
	@echo 'echo "1/3 Formatting code..."' >> .git/hooks/pre-commit
	@echo 'make format > /dev/null 2>&1' >> .git/hooks/pre-commit
	@echo '' >> .git/hooks/pre-commit
	@echo '# Run tests' >> .git/hooks/pre-commit
	@echo 'echo "2/3 Running tests..."' >> .git/hooks/pre-commit
	@echo 'test_output=$$(make test 2>&1)' >> .git/hooks/pre-commit
	@echo 'if [ $$? -ne 0 ]; then' >> .git/hooks/pre-commit
	@echo '    echo "$$test_output" | grep -v "ERROR:root:" | grep -v "WARNING:root:" | grep -E "(FAILED|Traceback|File.*line|AssertionError)" | tail -10' >> .git/hooks/pre-commit
	@echo '    echo ""' >> .git/hooks/pre-commit
	@echo '    echo "Tests failed! Run '\''make test'\'' for full output."' >> .git/hooks/pre-commit
	@echo '    exit 1' >> .git/hooks/pre-commit
	@echo 'fi' >> .git/hooks/pre-commit
	@echo '' >> .git/hooks/pre-commit
	@echo '# Lint code' >> .git/hooks/pre-commit
	@echo 'echo "3/3 Linting code..."' >> .git/hooks/pre-commit
	@echo 'flake8 framework/ tests/ --max-line-length=127 --exclude=__pycache__,.venv --select=E9,F63,F7,F82' >> .git/hooks/pre-commit
	@echo 'if [ $$? -ne 0 ]; then' >> .git/hooks/pre-commit
	@echo '    echo "Linting failed! Commit aborted."' >> .git/hooks/pre-commit
	@echo '    exit 1' >> .git/hooks/pre-commit
	@echo 'fi' >> .git/hooks/pre-commit
	@echo '' >> .git/hooks/pre-commit
	@echo 'echo "All checks passed!"' >> .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "Pre-commit hooks installed successfully!"
	@echo ""
	@echo "The hook will run before each commit:"
	@echo "  1. Format code (black, isort)"
	@echo "  2. Run unit tests (shows output on failure)"
	@echo "  3. Lint code (flake8)"
	@echo ""
	@echo "To skip the hook, use: git commit --no-verify"

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
	echo "$$output"; \
	if echo "$$output" | grep -q "\[ERROR\]"; then \
		echo "Config validation failed due to errors"; \
		exit 1; \
	elif echo "$$output" | grep -q "\[WARNING\]"; then \
		echo "Config validation passed with warnings"; \
		exit 0; \
	else \
		exit 0; \
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

clean-venv:
	@echo "Removing virtual environment..."
	rm -rf .venv
	@echo "Virtual environment removed!"

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
