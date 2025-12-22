# Locust Flow

[![CI Pipeline](https://github.com/htunkhainglynn/locust-flow/actions/workflows/ci.yml/badge.svg)](https://github.com/htunkhainglynn/locust-flow/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**A powerful, YAML-based load testing framework built on Locust. Define complex API test scenarios with multi-user authentication, data generation, encryption, and validation - all through simple configuration files.**

## Table of Contents

- [Why We Built This](#why-we-built-this)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration Reference](#configuration-reference)
- [Plugins](#plugins)
- [Validation](#validation)
- [Advanced Usage](#advanced-usage)
- [Command Reference](#command-reference)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Why We Built This

Writing Locust tests usually means writing Python — and that's fine for one project. But once you're juggling many services, many environments, and many teams, it quickly becomes painful.

Every project ends up with:
- Slightly different Locust scripts
- Repeated boilerplate
- Copy-paste logic with tiny changes
- Yet another Python file to maintain

At some point the question becomes:

**"Why am I rewriting Python just to describe HTTP flows?"**

Locust Flow was built to fix that.

Instead of treating load tests as code, it treats them as configuration:
- API flows belong in YAML/JSON
- Logic should be reusable, not rewritten
- Adding a new service should not mean adding new Python files

The goal is simple: **define traffic once, reuse it everywhere** — without the mental overhead of maintaining Python test code across dozens of projects.

If you've ever felt annoyed writing Python just to load test another API, Locust Flow is for you.

## Example

```yaml
service_name: "E-commerce API"
base_url: "https://api.shop.com"
run_init_once: true
init_list_var: "users"

variables:
  users:
    - "user001"
    - "user002"
    - "user003"
    - "user004"
    - "user005"
  passwords:
    - "pass001"
    - "pass002"
    - "pass003"
    - "pass004"
    - "pass005"

init:
  - name: "Login"
    method: "POST"
    endpoint: "/auth/login"
    pre_transforms:
      - type: "select_from_list"
        config:
          from: "users"
          mode: "round_robin"
        output: "username"
      - type: "select_from_list"
        config:
          from: "passwords"
          mode: "round_robin"
        output: "password"
    data:
      username: "{{ username }}"
      password: "{{ password }}"
    extract:
      token: "json.access_token"
    post_transforms:
      - type: "store_data"
        config:
          key: "{{ username }}"
          values:
            - "token"

steps:
  - name: "Browse Products"
    weight: 0.5
    method: "GET"
    endpoint: "/products"
    headers:
      Authorization: "Bearer {{ token }}"
  
  - name: "Add to Cart"
    weight: 0.3
    method: "POST"
    endpoint: "/cart"
    headers:
      Authorization: "Bearer {{ token }}"
    data:
      product_id: "{{ product_id }}"
      quantity: "{{ quantity }}"
    pre_transforms:
      - type: "random_number"
        config:
          min: 1
          max: 5
        output: "quantity"
  
  - name: "Checkout"
    weight: 0.2
    method: "POST"
    endpoint: "/checkout"
    headers:
      Authorization: "Bearer {{ token }}"
    validate:
      status_code: 200
      max_response_time: 3000
```

**Run it:**
```bash
make run
```

**What happens:**
1. Validates config automatically
2. Logs in 5 users once at startup
3. 100 virtual users make requests using those 5 accounts
4. 50% browse, 30% add to cart, 20% checkout
5. Random quantities, validated responses

---

## Features

- **YAML Configuration** - Define tests without writing code
- **Multi-User Testing** - Simulate realistic load with multiple accounts
- **Data Generation** - Random numbers, UUIDs, timestamps, encryption
- **Response Validation** - Automated assertions on status, timing, and content
- **Conditional Logic** - Skip steps based on runtime conditions
- **Variable Extraction** - Chain requests by extracting and reusing data
- **Retry Handling** - Automatic retries for transient failures

---

## Quick Start

### 1. Install Dependencies
```bash
make install
```

### 2. Validate Your Config
```bash
make validate-configs
```

### 3. Run Load Test
```bash
# Web UI (recommended)
make run

# Headless mode
make run-headless
```

**Why use `make`?**

| Benefit | Description |
|---------|-------------|
| **Pre-validation** | Validates configs before running, prevents runtime errors |
| **Consistency** | Same commands work across all environments |
| **Error Handling** | Automatic error detection and reporting |
| **Best Practices** | Built-in optimizations and safety checks |

### Manual Run (Not Recommended)
```bash
# Only if you can't use make
python validate_config.py configs/*.yaml  # Validate first!
locust -f main.py
# Open http://localhost:8089
```

---

## Configuration

### Basic Structure

```yaml
service_name: "My API"
base_url: "https://api.example.com"
run_init_once: true
init_list_var: "users"

variables:
  users:
    - "user1"
    - "user2"
  api_key: "abc123"

init:
  - name: "Login"
    method: "POST"
    endpoint: "/auth/login"
    extract:
      token: "json.token"

steps:
  - name: "Get Data"
    weight: 1.0
    method: "GET"
    endpoint: "/data"
    headers:
      Authorization: "Bearer {{ token }}"
```

### Multi-User Setup

```yaml
run_init_once: true
init_list_var: "users"

variables:
  users:
    - "user001"
    - "user002"
    - "user003"
  passwords:
    - "pass001"
    - "pass002"
    - "pass003"

init:
  - name: "Login"
    pre_transforms:
      - type: "select_from_list"
        config:
          from: "users"
          mode: "round_robin"
        output: "username"
    data:
      username: "{{ username }}"
    extract:
      token: "json.token"
    post_transforms:
      - type: "store_data"
        config:
          key: "{{ username }}"
          values:
            - "token"
```

## Plugins

### Data Generators

| Plugin | Description | Configuration | Output |
|--------|-------------|---------------|--------|
| `random_number` | Generate random integer | `min`, `max` | Integer between min and max |
| `random_string` | Generate random string | `length` | Alphanumeric string |
| `random_choice` | Pick random item | `choices` (array) | One item from array |
| `uuid` | Generate UUID v4 | None | UUID string |
| `timestamp` | Current timestamp | `format` (unix/iso) | Timestamp string |
| `increment` | Auto-increment counter | `start`, `step` | Incremented number |

### List Selection

| Plugin | Description | Configuration | Output |
|--------|-------------|---------------|--------|
| `select_from_list` | Pick from variable list | `from`, `mode` (round_robin/random) | Selected item |

### Encryption & Hashing

| Plugin | Description | Configuration | Input Required |
|--------|-------------|---------------|----------------|
| `rsa_encrypt` | RSA encryption | `public_key` | Data to encrypt |
| `sha256` | SHA-256 hash | None | Data to hash |
| `hmac` | HMAC signature | `key`, `algorithm` | Data to sign |
| `base64_encode` | Base64 encoding | None | Data to encode |
| `base64_decode` | Base64 decoding | None | Data to decode |

### Data Storage

| Plugin | Description | Configuration | Purpose |
|--------|-------------|---------------|----------|
| `store_data` | Store variables by key | `key`, `values` | Multi-user token management |

**Example:**
```yaml
pre_transforms:
  - type: "random_number"
    config:
      min: 100
      max: 5000
    output: "amount"
  
  - type: "uuid"
    output: "request_id"
  
  - type: "rsa_encrypt"
    input: "{{ password }}"
    output: "encrypted_password"
```

### Variables

```yaml
variables:
  api_key: "abc123"

headers:
  Authorization: "{{ api_key }}"

extract:
  token: "json.access_token"
  user_id: "json.user.id"
  cookie: "headers.Set-Cookie"
```

## Validation

### Basic Validation

| Field | Type | Description | Example |
|-------|------|-------------|----------|
| `status_code` | Integer | Expected HTTP status | `200`, `201`, `404` |
| `max_response_time` | Integer | Max time in milliseconds | `2000`, `5000` |
| `json` | Object | JSON path assertions | `success: true` |
| `fail_on_error` | Boolean | Stop test on failure | `true`, `false` |

### Field-Based Validation

| Field | Type | Description | Example |
|-------|------|-------------|----------|
| `field` | String | JSON path to validate | `data.status`, `user.id` |
| `condition` | String | Comparison operator | `equals`, `contains`, `greater_than` |
| `expected` | Any | Expected value | `"active"`, `100`, `true` |

### Available Conditions

| Condition | Description | Example |
|-----------|-------------|----------|
| `equals` | Exact match | `field: "status", expected: "success"` |
| `not_equals` | Not equal | `field: "error", expected: null` |
| `contains` | String contains | `field: "message", expected: "approved"` |
| `not_contains` | String doesn't contain | `field: "message", expected: "error"` |
| `greater_than` | Numeric comparison | `field: "balance", expected: 0` |
| `less_than` | Numeric comparison | `field: "count", expected: 100` |
| `is_empty` | Check if empty | `field: "errors"` |
| `is_not_empty` | Check if not empty | `field: "data"` |

### Validation Examples

```yaml
# Basic validation
validate:
  status_code: 200
  max_response_time: 2000
  json:
    success: true
    data.status: "completed"

# Field-based validation
validate:
  - field: "data.balance"
    condition: "greater_than"
    expected: 0
  - field: "data.status"
    condition: "equals"
    expected: "active"
  - field: "errors"
    condition: "is_empty"
```

### Conditional Steps

```yaml
steps:
  - name: "Transfer Money"
    skip_if:
      condition: "equals"
      left: "{{ sender }}"
      right: "{{ receiver }}"
    data:
      from: "{{ sender }}"
      to: "{{ receiver }}"
```

### Skip Conditions

| Condition | Description | Use Case |
|-----------|-------------|----------|
| `equals` | Values are equal | Skip if sender equals receiver |
| `not_equals` | Values are different | Skip if status is not active |
| `contains` | String contains substring | Skip if message contains error |
| `greater_than` | Numeric comparison | Skip if balance too low |
| `less_than` | Numeric comparison | Skip if count exceeds limit |
| `is_empty` | Value is empty/null | Skip if no data available |
| `is_not_empty` | Value exists | Skip if already processed |

### Weights

```yaml
steps:
  - name: "Browse"
    weight: 0.5
  - name: "Add to Cart"
    weight: 0.3
  - name: "Checkout"
    weight: 0.2
```

## Configuration Reference

### Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `service_name` | String | Yes | Name of the service being tested |
| `base_url` | String | Yes | Base URL for all requests |
| `run_init_once` | Boolean | No | Run init steps once at startup |
| `init_list_var` | String | No | Variable containing user list |
| `variables` | Object | No | Global variables |
| `init` | Array | No | Initialization steps |
| `steps` | Array | Yes | Main test steps |

### Step Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | String | Yes | Step name for logging |
| `method` | String | Yes | HTTP method (GET, POST, PUT, DELETE, PATCH) |
| `endpoint` | String | Yes | API endpoint path |
| `weight` | Float | No | Execution probability (0.0-1.0, default: 1.0) |
| `headers` | Object | No | HTTP headers |
| `data` | Object | No | Request body (form data) |
| `json` | Object | No | JSON request body |
| `params` | Object | No | URL query parameters |
| `timeout` | Integer | No | Request timeout in seconds |
| `pre_request` | Array | No | Steps to run before this step |
| `pre_transforms` | Array | No | Data transformations before request |
| `post_transforms` | Array | No | Data transformations after request |
| `extract` | Object | No | Extract variables from response |
| `validate` | Object/Array | No | Response validation rules |
| `retry_on` | Object | No | Retry configuration |
| `skip_if` | Object | No | Conditional step execution |

### Transform Structure

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | String | Yes | Plugin name |
| `input` | String | No | Input variable (template) |
| `output` | String | Yes | Output variable name |
| `config` | Object | No | Plugin-specific configuration |

### Retry Configuration

| Field | Type | Description |
|-------|------|-------------|
| `max_attempts` | Integer | Maximum retry attempts (default: 3) |
| `status_codes` | Array | HTTP status codes to retry on |
| `exceptions` | Array | Exception types to retry on |

---

## Advanced Usage

### Pre-Request Steps

```yaml
steps:
  - name: "Payment"
    pre_request:
      - "Get Fresh Token"
    method: "POST"
    endpoint: "/payments"
```

### Chained Transforms

```yaml
pre_transforms:
  - type: "random_string"
    config:
      length: 8
    output: "password"
  
  - type: "sha256"
    input: "{{ password }}"
    output: "hashed"
  
  - type: "base64_encode"
    input: "{{ hashed }}"
    output: "final"
```

---

## Command Reference

```bash
# Setup
make install          # Install dependencies
make install-dev      # Install dev dependencies

# Validation
make validate-configs # Validate all YAML configs

# Testing
make test             # Run unit tests
make coverage         # Run tests with coverage report

# Running
make run              # Start Locust web UI (validates first)
make run-headless     # Run headless load test (validates first)

# Code Quality
make lint             # Run linters
make format           # Format code

# CI/CD
make ci               # Run all CI checks
make all              # Run everything
```

---

## Best Practices

| Practice | Recommendation | Reason |
|----------|----------------|--------|
| **Config Validation** | Always use `make run` | Catches errors before runtime |
| **Initialization** | Use `run_init_once: true` | Faster tests, less load on auth |
| **User Management** | Set `init_list_var` | Proper multi-user setup |
| **Load Distribution** | Use `round_robin` for users | Even distribution across accounts |
| **User Behavior** | Use `random` for actions | Realistic traffic patterns |
| **Step Weights** | Match real user behavior | Accurate load simulation |
| **Token Storage** | Use `store_data` plugin | Avoid re-authentication |
| **Response Validation** | Validate critical responses | Early error detection |
| **Timeouts** | Set appropriate timeouts | Prevent hanging requests |
| **Retry Logic** | Configure retries for transient errors | Handle network issues |

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Config validation fails | YAML syntax error | Check indentation, quotes, and structure |
| "Plugin not found" | Typo in plugin name | Check plugin name spelling |
| "Variable not found" | Missing variable | Ensure variable is defined or extracted |
| Authentication fails | Wrong credentials | Verify credentials in variables section |
| Timeout errors | Slow API or low timeout | Increase timeout value |
| Rate limiting | Too many requests | Reduce users or add delays |
| Token expired | Long test duration | Implement token refresh in pre_request |

### Debug Mode

```bash
# Run with verbose logging
LOG_LEVEL=DEBUG make run

# Validate specific config
python validate_config.py configs/your-config.yaml

# Run tests to verify setup
make test
```

### Performance Tips

| Tip | Description | Impact |
|-----|-------------|--------|
| Use `run_init_once` | Initialize once, not per user | 10-100x faster startup |
| Optimize weights | Focus on critical paths | Better resource usage |
| Set realistic timeouts | Avoid hanging requests | Cleaner test results |
| Validate selectively | Only validate critical responses | Reduced overhead |
| Use connection pooling | Enabled by default | Better performance |

---

## Examples

Check `/configs/` directory for complete examples:

| File | Description | Features Demonstrated |
|------|-------------|----------------------|
| `test.yaml` | Wave Money API | Multi-step auth, encryption, validation |
| `test-wave-pay.yaml` | 50 users example | Multi-user setup, token storage, weights |

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Run tests: `make test`
4. Run linters: `make lint`
5. Format code: `make format`
6. Submit a pull request

### Development Setup

```bash
# Install development dependencies
make install-dev

# Install pre-commit hooks
make install-hooks

# Run all checks
make ci
```

### Running Tests

```bash
# Run unit tests
make test

# Run with coverage
make coverage

# Run specific test file
pytest tests/test_config_validator.py -v
```
