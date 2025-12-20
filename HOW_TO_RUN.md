# How to Run

## Quick Start

```bash
git # 1. Install dependencies
make install

# 2. Validate your config (IMPORTANT!)
make validate-configs

# 3. Start load testing
make run
```

Open `http://localhost:8089` in your browser.

**Note:** `make run` automatically validates configs before starting. If validation fails, Locust won't start.

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

### Start Web UI (Recommended)

```bash
make run
```

**What happens:**
1. ✓ Validates all configs in `configs/` folder
2. ✓ If validation passes: Shows "Config validation passed"
3. ✓ Starts Locust web UI
4. ❌ If validation fails: Shows errors and stops (Locust won't start)

Then open `http://localhost:8089`

### Headless Mode

```bash
make run-headless
# Runs: 10 users, 2/sec spawn rate, 60 seconds
# Also validates configs first
```

### Manual Commands (Not Recommended)

```bash
# ALWAYS validate first!
python validate_config.py configs/*.yaml

# Then run if validation passed
locust -f main.py

# Headless
locust -f main.py --headless -u 10 -r 2 -t 60s

# Custom port
locust -f main.py --web-port 8090
```

**Why use `make run` instead?**
- ✅ Automatic config validation before starting
- ✅ Prevents runtime errors from invalid configs
- ✅ Clean, minimal output on success
- ✅ Detailed errors on failure

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

### Config Validation

```bash
make validate-configs  # Validate all YAML configs
```

**What it validates:**
- ✅ Required fields (`service_name`, `base_url`, `steps`/`init`)
- ✅ HTTP methods (GET, POST, PUT, PATCH, DELETE, etc.)
- ✅ Weight range (0-1, accepts "0.5" or 0.5)
- ✅ Transform types and configurations
- ✅ Variable references (e.g., `select_from_list` from field)
- ✅ Validation conditions and formats
- ✅ retry_on conditions
- ✅ Top-level key typos (strict errors)
- ✅ Step/transform key typos (warnings)
- ⚠️ Template variables like `{{ weight }}` bypass validation

**Output:**
```bash
# Success (minimal)
Config validation passed

# Failure (detailed)
[INVALID] Config is invalid
[ERROR] steps[0]: 'weight' must be between 0 and 1 (inclusive), got 10
[WARNING] steps[0]: Unknown field 'metod'. Valid fields: name, method, endpoint...
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

## Recommended Workflow

### For Running Tests

```bash
# 1. Install
make install

# 2. Validate config (catches errors early!)
make validate-configs

# 3. Run
make run
# Opens http://localhost:8089
```

### For Development

```bash
# 1. Setup
make install-dev

# 2. Make changes
# ... edit code or configs ...

# 3. Validate configs (if changed)
make validate-configs

# 4. Format code
make format

# 5. Run all checks
make ci

# 6. Commit
git add .
git commit -m "Your changes"
git push
```

### Common Issues

**Config validation fails:**
```bash
# See detailed errors
make validate-configs

# Common fixes:
# - Fix typos in field names
# - Ensure weight is between 0-1
# - Check variable references exist
# - Verify transform types are valid
```

**Runtime errors:**
```bash
# Always validate first!
make validate-configs

# If validation passes but runtime fails:
# - Check template variable values
# - Verify API endpoints are correct
# - Check network connectivity
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
