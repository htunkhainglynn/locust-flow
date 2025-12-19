# How to Run

## Quick Start

```bash
# 1. Install dependencies
make install-dev

# 2. Run tests
make test

# 3. Start load testing
make run
```

Open `http://localhost:8089` in your browser.

---

## Prerequisites

- Python 3.8+
- pip
- make (optional)

---

## Installation

### Using Makefile (Recommended)

```bash
# Production dependencies only
make install

# With dev tools (testing, linting, security)
make install-dev
```

### Manual Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Running Load Tests

### Start Web UI

```bash
make run
```

Then open `http://localhost:8089`

### Headless Mode

```bash
make run-headless
# Runs: 10 users, 2/sec spawn rate, 60 seconds
```

### Manual Commands

```bash
# Web UI
locust -f main.py

# Headless
locust -f main.py --headless -u 10 -r 2 -t 60s

# Custom port
locust -f main.py --web-port 8090
```

---

## Development

### Testing

```bash
make test           # Run unit tests
make test-verbose   # Verbose output
make coverage       # Coverage report (htmlcov/index.html)
```

### Code Quality

```bash
make lint           # Run linters
make format         # Auto-format code
make format-check   # Check formatting
```

### Security

```bash
make security       # All security scans
make bandit         # Bandit scanner
make safety         # Dependency check
```

### Validation

```bash
make validate-configs  # Validate YAML configs
```

### CI Checks

```bash
make ci    # Run all checks (test, lint, security, validate)
make all   # Install + all checks
```

### Cleanup

```bash
make clean  # Remove cache, logs, coverage files
```

---

## Configuration

### Create New Config

```bash
python config_generator.py
```

Follow prompts to generate `configs/your_service.yaml`

### Config Location

Place YAML configs in `configs/` directory:
- `configs/test.yaml`
- `configs/test-wave-pay.yaml`
- `configs/your_service.yaml`

---

## Troubleshooting

### Import Errors

```bash
pip install -r requirements.txt --upgrade
```

### Port Already in Use

```bash
locust -f main.py --web-port 8090
```

### Config Not Found

Ensure config files are in `configs/` with `.yaml` extension.

### Dev Tools Not Found

```bash
make install-dev
```

---

## Workflow

```bash
# 1. Setup
make install-dev

# 2. Make changes
# ... edit code ...

# 3. Format
make format

# 4. Check
make ci

# 5. Commit
git add .
git commit -m "Your changes"
git push
```

---

## Help

```bash
make help  # Show all commands
```

For more details, see:
- `README.md` - Project overview
- `tests/README.md` - Testing guide
- `.github/workflows/README.md` - CI/CD docs
