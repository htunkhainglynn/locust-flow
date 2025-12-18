# Locust Flow

A powerful, config-driven load testing framework that eliminates Python boilerplate for API load testing. Built on top of Locust, it allows you to define complete test flows using simple YAML or JSON configuration files.

## Why Locust Flow?

- **Zero Boilerplate**: Add new services with just a YAML config file - no Python code required
- **Template Engine**: Dynamic data with `{{ variable }}` syntax for flexible test scenarios
- **Plugin System**: Built-in RSA encryption, HMAC, SHA256, Base64, and data generators
- **Flow-Based Testing**: Define multi-step API flows with dependencies and pre-requests
- **Variable Extraction**: Seamlessly pass data between test steps using JSONPath
- **Response Validation**: Built-in validation for status codes, response times, and JSON content
- **Weight-Based Distribution**: Control load distribution across different endpoints
- **Multi-User Support**: Distribute different credentials across virtual users with round-robin or random selection
- **Shared Token Storage**: Store and reuse authentication tokens across virtual users
- **Extensible Architecture**: Easy to add custom plugins and transformations

## Perfect For

- API load testing without requiring Python knowledge
- Teams that want config-driven, maintainable test suites
- Microservices with complex authentication flows
- Multi-step API scenarios (login → transaction → confirmation)
- Rapid prototyping and iteration of load tests
- Sharing test configurations across teams

## Quick Example

```yaml
service_name: "My API"
base_url: "https://api.example.com"

init:
  - name: "Login"
    method: "POST"
    endpoint: "/auth/login"
    data:
      username: "{{ username }}"
      password: "{{ password }}"
    extract:
      auth_token: "json.token"

steps:
  - name: "Create Order"
    weight: 0.7
    method: "POST"
    endpoint: "/orders"
    headers:
      Authorization: "Bearer {{ auth_token }}"
    data:
      amount: "{{ random_amount }}"
    pre_transforms:
      - type: "random_number"
        config:
          min: 100
          max: 1000
        output: "random_amount"
    validate:
      status_code: 201
      max_response_time: 2000
```

That's it! Run with: `locust -f main.py`

---

## 🚀 Quick Start

### Option 1: Use the Config Generator (Recommended)

Generate a config template instantly with default values:

```bash
python config_generator.py
```

This creates `configs/my_api_service.yaml` with:
- Example login/authentication (init section)
- Example GET and POST requests
- Default headers and variables
- Response validation

Then edit the generated YAML file to customize for your API.

### Option 2: Manual Configuration

Create a YAML file in `/configs/` directory:

```yaml
service_name: "My New Service"
base_url: "https://api.mynewservice.com"

steps:
  - name: "Health Check"
    method: "GET"
    endpoint: "/health"
    validate:
      status_code: 200
```

### Running Load Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run with web UI
locust -f main.py

# Run headless
locust -f main.py --headless -u 10 -r 2 -t 60s
```

---

## Configuration Format

### Basic Structure

```yaml
service_name: "My API Service"
description: "Load test configuration"
base_url: "https://api.example.com"
run_init_once: true  # Run init steps only once across all users

# Global variables available to all steps
variables:
  api_key: "your-api-key"
  app_version: "1.0.0"
  user_id: "test_user"
  secret_key: "your-secret"

# Default headers for all requests
headers:
  Content-Type: "application/json"
  Accept: "application/json"
  User-Agent: "LoadTest/{{ app_version }}"

# Initialization steps (run once per user or once globally)
init:
  - name: "Get Auth Token"
    method: "POST"
    endpoint: "/auth/login"
    data:
      username: "{{ user_id }}"
      password: "{{ secret_key }}"
    extract:
      auth_token: "json.token"
      user_id: "json.user.id"

# Test steps with weights and advanced features
steps:
  - name: "Get User Profile"
    weight: 0.3  # 30% of requests
    method: "GET"
    endpoint: "/users/{{ user_id }}"
    headers:
      Authorization: "Bearer {{ auth_token }}"
    validate:
      status_code: 200

  - name: "Create Transaction"
    weight: 0.7  # 70% of requests (main load)
    pre_request:
      - "Get Fresh Token"  # Execute before this step
    method: "POST"
    endpoint: "/transactions"
    headers:
      Authorization: "Bearer {{ auth_token }}"
    data:
      amount: "{{ random_amount }}"
      type: "{{ transaction_type }}"
      description: "Load test transaction"
    pre_transforms:
      - type: "random_number"
        config:
          min: 100
          max: 1000
        output: "random_amount"
      - type: "random_choice"
        config:
          choices: ["TRANSFER", "PAYMENT", "TOPUP"]
        output: "transaction_type"
    validate:
      status_code: 201
      max_response_time: 3000
    extract:
      transaction_id: "json.id"
```

### Step Configuration Options

Each step supports comprehensive configuration:

#### **Basic Request Properties**
- **`method`**: HTTP method (GET, POST, PUT, DELETE, etc.)
- **`endpoint`**: API endpoint path (supports template variables)
- **`headers`**: Custom headers (merged with global headers)
- **`data`**: Request body for POST/PUT (JSON or form data)
- **`params`**: Query parameters for GET requests

#### **Advanced Features**
- **`weight`**: Execution probability (0.0-1.0) for load distribution
- **`pre_request`**: Execute other steps before this one
- **`depends_on`**: Step dependency (deprecated, use pre_request)
- **`use_curl`**: Force use of curl executor for case-sensitive headers
- **`fail_fast`**: Stop execution on failure

#### **Data Transformation**
- **`pre_transforms`**: Transform data before request
- **`post_transforms`**: Transform data after response

#### **Response Handling**
- **`validate`**: Response validation rules
- **`extract`**: Extract variables from response

### Complete Step Example

```yaml
steps:
  - name: "Create Order"
    weight: 0.8                    # 80% of requests
    method: "POST"
    endpoint: "/api/orders"
    
    # Execute fresh token before this step
    pre_request:
      - "Get Fresh Token"
    
    # Custom headers
    headers:
      Authorization: "Bearer {{ auth_token }}"
      Content-Type: "application/json"
      X-Request-ID: "{{ request_id }}"
    
    # JSON request body with template variables
    data:
      customer_id: "{{ customer_id }}"
      amount: "{{ order_amount }}"
      currency: "{{ currency }}"
      items:
        - product_id: "{{ product_id }}"
          quantity: "{{ quantity }}"
    
    # Transform data before request
    pre_transforms:
      - type: "uuid"
        output: "request_id"
      - type: "random_number"
        config:
          min: 100
          max: 5000
        output: "order_amount"
      - type: "random_choice"
        config:
          choices: ["USD", "EUR", "GBP"]
        output: "currency"
    
    # Validate response
    validate:
      status_code: 201
      max_response_time: 3000
      json:
        success: true
        data.status: "created"
    
    # Extract data for next steps
    extract:
      order_id: "json.data.order_id"
      total_amount: "json.data.total"
```

### Weight-Based Load Distribution

Control request distribution using weights:

```yaml
steps:
  - name: "Browse Products"
    weight: 0.5    # 50% of requests
    method: "GET"
    endpoint: "/products"
    
  - name: "View Product Details"
    weight: 0.3    # 30% of requests
    method: "GET"
    endpoint: "/products/{{ product_id }}"
    
  - name: "Purchase Product"
    weight: 0.2    # 20% of requests
    method: "POST"
    endpoint: "/purchase"
```

**Note**: Weights don't need to sum to 1.0. The framework normalizes them automatically.

## 🔄 Init Steps & Pre-Request Features

### Init Steps Configuration

Init steps run once per user (or once globally) to set up authentication and shared data:

```yaml
# Global setting - run init once for all users (shared context)
run_init_once: true

init:
  - name: "Get Session Token"
    method: "POST"
    endpoint: "/auth/session"
    data:
      client_id: "{{ client_id }}"
      client_secret: "{{ client_secret }}"
    extract:
      session_token: "json.access_token"
      expires_in: "json.expires_in"

  - name: "User Login"
    method: "POST"
    endpoint: "/auth/login"
    headers:
      Authorization: "Bearer {{ session_token }}"
    data:
      username: "{{ username }}"
      password: "{{ hashed_password }}"
    pre_transforms:
      - type: "sha256"
        input: "{{ password }}"
        output: "hashed_password"
    extract:
      user_token: "json.user_token"
      user_id: "json.user.id"
```

### Pre-Request Feature

Execute steps before main requests for fresh data:

#### **Method 1: Reference Existing Steps**
```yaml
steps:
  - name: "Process Payment"
    pre_request:
      - "Get Fresh Token"  # References step by name
    method: "POST"
    endpoint: "/payments"
    data:
      token: "{{ fresh_token }}"  # Uses fresh token
```

#### **Method 2: Inline Step Definition**
```yaml
steps:
  - name: "Process Payment"
    pre_request:
      - method: "GET"
        endpoint: "/auth/refresh"
        headers:
          Authorization: "Bearer {{ auth_token }}"
        extract:
          fresh_token: "json.access_token"
    method: "POST"
    endpoint: "/payments"
    data:
      token: "{{ fresh_token }}"  # Uses inline extracted token
```

### Init vs Pre-Request Comparison

| Feature | Init Steps | Pre-Request |
|---------|------------|-------------|
| **When** | Once per user/globally | Before each main request |
| **Purpose** | Authentication, setup | Fresh data, tokens |
| **Scope** | Shared across all steps | Specific to one step |
| **Performance** | High (runs once) | Lower (runs repeatedly) |
| **Use Case** | Login, device registration | Security tokens, fresh data |

### Best Practices

#### **Use Init Steps For:**
- User authentication (login)
- Device registration
- One-time setup data
- Shared configuration

#### **Use Pre-Request For:**
- Security tokens that expire
- Fresh timestamps
- Dynamic data per request
- Rate-limited endpoints

```yaml
# GOOD: Login once in init
init:
  - name: "Login"
    method: "POST"
    endpoint: "/auth/login"
    extract:
      session_token: "json.token"

# GOOD: Fresh token per transaction
steps:
  - name: "Create Transaction"
    pre_request:
      - "Get Fresh Token"
    method: "POST"
    endpoint: "/transactions"
```

## 👥 Multi-User Load Testing

### Complete Multi-User Authentication Example

Test with multiple user accounts distributed across virtual users:

```yaml
service_name: "Multi-User API"
base_url: "https://api.example.com"
run_init_once: true  # Login happens once per virtual user

variables:
  # Multiple user accounts for load testing
  msisdns: ["9776864450", "9777012251", "9778123456"]
  passwords: ["pass1", "pass2", "pass3"]
  
  # Shared configuration
  app_id: "com.example.app"
  app_version: "1.0"

init:
  # Step 1: Select credentials for this virtual user
  - name: "Get Device ID"
    method: "GET"
    endpoint: "/device/{{ msisdn }}"
    pre_transforms:
      # Round-robin ensures even distribution of users
      - type: "select_from_list"
        config:
          from: "msisdns"
          mode: "round_robin"
        output: "msisdn"
      - type: "select_from_list"
        config:
          from: "passwords"
          mode: "round_robin"
        output: "password"
    extract:
      device_id: "json.deviceId"

  # Step 2: Get security token
  - name: "Get Security Token"
    method: "GET"
    endpoint: "/auth/token"
    headers:
      deviceid: "{{ device_id }}"
    extract:
      security_counter: "json.securityCounter"

  # Step 3: Login and store credentials
  - name: "Login"
    method: "POST"
    endpoint: "/auth/login"
    headers:
      deviceid: "{{ device_id }}"
    data:
      msisdn: "{{ msisdn }}"
      password: "{{ encrypted_password }}"
    pre_transforms:
      - type: "rsa_encrypt"
        input: "{{ password }}:{{ security_counter }}"
        output: "encrypted_password"
    extract:
      auth_token: "headers.Authorization"
    post_transforms:
      # Store auth data for reuse across requests
      - type: "store_data"
        config:
          key: "{{ msisdn }}"
          values:
            - "auth_token"
            - "device_id"
            - "security_counter"

steps:
  - name: "Create Transaction"
    method: "POST"
    endpoint: "/transactions"
    headers:
      Authorization: "{{ auth_token }}"
      deviceid: "{{ device_id }}"
    data:
      amount: "{{ amount }}"
    pre_transforms:
      - type: "random_number"
        config:
          min: 100
          max: 5000
        output: "amount"
    validate:
      status_code: 200
```

### How Multi-User Distribution Works

**With 10 Virtual Users and 3 Accounts:**

| Virtual User | Account Selected | Mode |
|--------------|------------------|------|
| User 1 | msisdns[0] | Round-robin |
| User 2 | msisdns[1] | Round-robin |
| User 3 | msisdns[2] | Round-robin |
| User 4 | msisdns[0] | Round-robin (cycles back) |
| User 5 | msisdns[1] | Round-robin |
| ... | ... | ... |

**Benefits:**
- **Even Distribution**: Round-robin ensures balanced load across accounts
- **Realistic Testing**: Simulates multiple real users
- **Token Reuse**: Stored tokens avoid repeated authentication
- **Scalable**: Add more accounts by extending the lists

### Token Manager Features

The `TokenManager` automatically:
- **Thread-safe storage** of authentication data per user
- **Shared across virtual users** for the same account
- **Persistent during test run** (no re-authentication needed)
- **Automatic cleanup** when test ends

**Stored Data Structure:**
```python
{
  "9776864450": {
    "auth_token": "eyJhbGc...",
    "device_id": "ABC123",
    "security_counter": "12345"
  },
  "9777012251": {
    "auth_token": "eyJhbGc...",
    "device_id": "DEF456",
    "security_counter": "67890"
  }
}
```

## 🔌 Plugin System

### Complete Plugin Reference

**Available Plugins:**
- **Encryption**: RSA, HMAC, SHA256, Base64
- **Generators**: UUID, Timestamp, Random Number/String, Increment
- **Selection**: Select From List, Random Choice
- **Storage**: Store Data (Token Manager)

#### 🔐 Encryption Plugins

##### **RSA Encryption**
```yaml
pre_transforms:
  - type: "rsa_encrypt"
    input: "{{ sensitive_data }}"
    output: "encrypted_data"
    # Uses rsa_public_key from variables section
```

##### **HMAC Signature**
```yaml
pre_transforms:
  - type: "hmac"
    input: "{{ payload_data }}"
    config:
      secret_key: "your-secret-key"
      algorithm: "sha256"  # sha1, sha256, sha512
    output: "signature"
```

##### **SHA256 Hashing**
```yaml
pre_transforms:
  - type: "sha256"
    input: "{{ data_to_hash }}"
    output: "hashed_value"
```

##### **Base64 Encoding/Decoding**
```yaml
pre_transforms:
  - type: "base64_encode"
    input: "{{ raw_data }}"
    output: "encoded_data"
  
  - type: "base64_decode"
    input: "{{ encoded_data }}"
    output: "decoded_data"
```

#### 🎲 Generator Plugins

##### **UUID Generation**
```yaml
pre_transforms:
  - type: "uuid"
    output: "request_id"
    # Generates: "550e8400-e29b-41d4-a716-446655440000"
```

##### **Timestamp Generation**
```yaml
pre_transforms:
  - type: "timestamp"
    config:
      format: "unix"        # unix, iso, custom
      custom_format: "%Y-%m-%d %H:%M:%S"
    output: "current_time"
```

##### **Random Numbers**
```yaml
pre_transforms:
  - type: "random_number"
    config:
      min: 1000
      max: 50000
      type: "int"          # int or float
    output: "random_amount"
```

##### **Random Strings**
```yaml
pre_transforms:
  - type: "random_string"
    config:
      length: 10
      charset: "alphanumeric"  # alphanumeric, alpha, numeric, custom
      custom_chars: "ABCDEF123456"
    output: "random_code"
```

##### **Random Choice**
```yaml
pre_transforms:
  - type: "random_choice"
    config:
      choices: ["VISA", "MASTERCARD", "AMEX"]
    output: "card_type"
  
  # Weighted choices
  - type: "random_choice"
    config:
      choices: 
        - value: "USD"
          weight: 0.7
        - value: "EUR"
          weight: 0.2
        - value: "GBP"
          weight: 0.1
    output: "currency"
```

##### **Incremental Values**
```yaml
pre_transforms:
  - type: "increment"
    config:
      start: 1000
      step: 1
      prefix: "TXN"
      suffix: ""
    output: "transaction_id"
    # Generates: TXN1000, TXN1001, TXN1002, ...
```

##### **Select From List**
```yaml
variables:
  msisdns: ["9776864450", "9777012251", "9778123456"]
  passwords: ["2580", "1133", "4567"]

pre_transforms:
  # Random selection
  - type: "select_from_list"
    config:
      from: "msisdns"  # Variable name containing the list
      mode: "random"   # random or round_robin
    output: "selected_msisdn"
  
  # Round-robin selection (distributes evenly across virtual users)
  - type: "select_from_list"
    config:
      from: "passwords"
      mode: "round_robin"
    output: "selected_password"
  
  # Direct list in config
  - type: "select_from_list"
    config:
      items: ["USD", "EUR", "GBP"]
      mode: "random"
    output: "currency"
```

**Use Cases:**
- Distribute multiple user accounts across virtual users
- Round-robin selection ensures even distribution
- Random selection for realistic load patterns

##### **Store Data (Token Manager)**
```yaml
post_transforms:
  # Store authentication data for reuse across virtual users
  - type: "store_data"
    config:
      key: "{{ msisdn }}"  # Unique identifier (e.g., user ID, phone number)
      values:
        - "wmt_mfs_token"      # Variable names to store
        - "device_id"
        - "security_counter"
```

**Use Cases:**
- Store authentication tokens per user
- Share login data across virtual users
- Reuse credentials without re-authenticating
- Multi-user load testing with persistent sessions

### Advanced Plugin Usage

#### **Chained Transformations**
```yaml
pre_transforms:
  # Step 1: Generate random data
  - type: "random_string"
    config:
      length: 8
    output: "raw_password"
  
  # Step 2: Hash the password
  - type: "sha256"
    input: "{{ raw_password }}"
    output: "hashed_password"
  
  # Step 3: Encode for transmission
  - type: "base64_encode"
    input: "{{ hashed_password }}"
    output: "encoded_password"
```

#### **Conditional Plugin Usage**
```yaml
pre_transforms:
  # Generate different data based on environment
  - type: "random_choice"
    config:
      choices: ["test_user_1", "test_user_2", "test_user_3"]
    output: "test_username"
    
  # Use production-like data for staging
  - type: "uuid"
    output: "session_id"
```

#### **Complex Data Generation**
```yaml
pre_transforms:
  # Generate realistic transaction data
  - type: "random_choice"
    config:
      choices: ["TRANSFER", "PAYMENT", "TOPUP", "WITHDRAWAL"]
    output: "transaction_type"
    
  - type: "random_number"
    config:
      min: 100
      max: 10000
    output: "amount"
    
  - type: "timestamp"
    config:
      format: "iso"
    output: "transaction_time"
    
  - type: "uuid"
    output: "correlation_id"
```

## 🔄 Variable System

Use `{{ variable_name }}` to reference variables:

```yaml
data:
  user_id: "{{ user_id }}"
  amount: "{{ transaction_amount }}"

extract:
  user_id: "json.data.user.id"  # Extract from JSON response
  token: "headers.Authorization"  # Extract from headers
```

## ✅ Response Validation

```yaml
validate:
  status_code: 200          # Exact match
  status_code: [200, 201]   # Multiple acceptable codes
  max_response_time: 2000   # Max 2 seconds
  json:
    success: true           # Validate JSON content
    data.count: 10
```

## 🔀 Conditional Step Execution

Skip steps based on runtime conditions using `skip_if`:

### Available Conditions

| Condition | Description | Example |
|-----------|-------------|---------|
| `equals` | Skip if values are equal | Skip if sender == receiver |
| `not_equals` | Skip if values are different | Skip if status != "active" |
| `contains` | Skip if left contains right | Skip if email contains "@test.com" |
| `not_contains` | Skip if left doesn't contain right | Skip if response not contains "error" |
| `greater_than` | Skip if left > right | Skip if amount > 10000 |
| `less_than` | Skip if left < right | Skip if balance < 100 |
| `is_empty` | Skip if value is empty/null | Skip if optional_field is empty |
| `is_not_empty` | Skip if value exists | Skip if error_message is not empty |

### Example: Skip Self-Transfer

```yaml
variables:
  msisdns: ["9776864450", "9777012251", "9778123456"]

init:
  - name: "Login"
    method: "POST"
    endpoint: "/auth/login"
    pre_transforms:
      # Select user credentials for this virtual user
      - type: "select_from_list"
        config:
          from: "msisdns"
          mode: "round_robin"
        output: "msisdn"
    data:
      username: "{{ msisdn }}"
      password: "{{ password }}"
    extract:
      auth_token: "json.token"

steps:
  - name: "Transfer Money"
    method: "POST"
    endpoint: "/transfer"
    headers:
      Authorization: "{{ auth_token }}"
    pre_transforms:
      # Randomly select a receiver (could be same as sender)
      - type: "select_from_list"
        config:
          from: "msisdns"
          mode: "random"  # Random selection for receiver
        output: "receiver_msisdn"
      
      # Generate random amount
      - type: "random_number"
        config:
          min: 1000
          max: 50000
        output: "amount"
    
    skip_if:
      condition: "equals"
      left: "{{ msisdn }}"        # Sender (from init)
      right: "{{ receiver_msisdn }}"  # Receiver (randomly selected)
    
    data:
      from: "{{ msisdn }}"           # Sender
      to: "{{ receiver_msisdn }}"    # Receiver
      amount: "{{ amount }}"
    
    validate:
      status_code: 200
```

**Result:** Transfer step is automatically skipped when sender and receiver are the same user.

### More Examples

**Skip if amount too large:**
```yaml
- name: "Process Large Transaction"
  method: "POST"
  endpoint: "/transactions/large"
  skip_if:
    condition: "less_than"
    left: "{{ amount }}"
    right: "10000"
  data:
    amount: "{{ amount }}"
```

**Skip if user is inactive:**
```yaml
- name: "Send Notification"
  method: "POST"
  endpoint: "/notifications"
  skip_if:
    condition: "not_equals"
    left: "{{ user_status }}"
    right: "active"
  data:
    user_id: "{{ user_id }}"
```

**Skip if test user:**
```yaml
- name: "Charge Payment"
  method: "POST"
  endpoint: "/payments"
  skip_if:
    condition: "contains"
    left: "{{ email }}"
    right: "@test.com"
  data:
    email: "{{ email }}"
    amount: "{{ amount }}"
```

### Benefits

- **Realistic Testing**: Avoid invalid scenarios (self-transfers, etc.)
- **Smart Load Distribution**: Skip unnecessary requests
- **Conditional Flows**: Different paths based on data
- **Error Prevention**: Skip steps that would fail due to business logic

## 🔍 Enhanced Error Logging

The framework provides detailed error logging for init steps to help debug authentication issues:

**When init steps fail (status code >= 400), the logs include:**
- Request URL
- Request Headers
- Request Body (first 500 chars)
- Response Body (first 500 chars)

**Example error log:**
```
[ERROR] Init step 'Login' failed!
[ERROR] Request URL: https://api.example.com/auth/login
[ERROR] Request Headers: {'Content-Type': 'application/json', 'deviceid': 'ABC123'}
[ERROR] Request Body: {"msisdn":"9776864450","password":"encrypted_value"}
[ERROR] Response Body: {"error":"Invalid credentials","code":401}
```

**Benefits:**
- Quick debugging of authentication failures
- Visibility into request/response data
- Helps identify configuration issues
- Reduces troubleshooting time

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run with web UI
locust -f main.py

# Run headless
locust -f main.py MyServiceUser --headless -u 10 -r 2 -t 60s
```

## 🎯 Adding New Services

Create a YAML config file in `/configs/` directory:

```yaml
service_name: "My New Service"
base_url: "https://api.mynewservice.com"

steps:
  - name: "Health Check"
    method: "GET"
    endpoint: "/health"
    validate:
      status_code: 200
```

That's it! **No Python code needed.**
