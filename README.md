# Locust Flow

**Config-driven API load testing. No Python code required.**

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

- ✅ **Zero Code** - Just YAML config files
- ✅ **Config Validation** - Catch errors before runtime
- ✅ **Multi-User** - Test with 50+ accounts, realistic load
- ✅ **Smart Data** - Random numbers, UUIDs, encryption, timestamps
- ✅ **Auth Flows** - Complex multi-step authentication
- ✅ **Conditional** - Skip steps based on conditions
- ✅ **Validation** - Status codes, response times, JSON content
- ✅ **Weights** - Control load distribution (browse > cart > checkout)

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
- ✅ Validates configs before running (prevents runtime errors)
- ✅ Consistent commands across environments
- ✅ Automatic error handling
- ✅ Built-in best practices

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

### Plugins

| Plugin | Usage |
|--------|-------|
| `random_number` | `min: 100, max: 5000` |
| `random_string` | `length: 10` |
| `uuid` | Generate unique ID |
| `timestamp` | Unix or ISO format |
| `select_from_list` | Pick from array (round_robin/random) |
| `rsa_encrypt` | Encrypt with public key |
| `sha256` | Hash data |
| `base64_encode` | Encode data |
| `store_data` | Save tokens/data |

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

### Validation

```yaml
validate:
  status_code: 200
  max_response_time: 2000
  json:
    success: true
    data.status: "completed"
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

**Conditions:** `equals`, `not_equals`, `contains`, `greater_than`, `less_than`, `is_empty`, `is_not_empty`

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

---

## Advanced

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

## Available Commands

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

## Tips

1. **Always use `make run`** - It validates configs before starting
2. Use `run_init_once: true` for faster tests
3. Add `init_list_var` to specify which variable contains accounts
4. Use `round_robin` for even distribution
5. Use `random` for realistic patterns
6. Set weights to match real behavior (0-1 range)
7. Store tokens to avoid re-authentication
8. Validate responses to catch errors early

---

## Examples

Check `/configs/` for more:
- `test.yaml` - Wave Money API
- `test-wave-pay.yaml` - 50 users example
