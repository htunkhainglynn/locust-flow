# How to Run Locust Flow

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

### 1. Create a Virtual Environment (Recommended)

**Important:** The virtual environment (`.venv/` or `venv/`) is not included in the repository. You must create it on your machine.

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

**Note:** If you prefer using `venv` instead of `.venv`, that works too:
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** The requirements.txt uses flexible version ranges for compatibility across different systems and Python versions. If you encounter any issues, try upgrading pip first:

```bash
pip install --upgrade pip
```

## Running Load Tests

### Option 1: Generate a Config First (Recommended for New Users)

```bash
# Generate a minimal config template
python config_generator.py

# Follow the prompts to create your config file
# Files are saved to configs/ directory
```

### Option 2: Run with Existing Configs

```bash
# Run with web UI (interactive mode)
locust -f main.py

# Then open http://localhost:8089 in your browser
```

### Option 3: Run Headless (No Web UI)

```bash
# Run with 10 users, spawn rate of 2 users/sec, for 60 seconds
locust -f main.py --headless -u 10 -r 2 -t 60s
```

## Web UI Usage

1. Open http://localhost:8089 in your browser
2. Select the user class (corresponds to your config file)
3. Set number of users and spawn rate
4. Click "Start swarming"
5. Monitor real-time statistics and graphs

## Troubleshooting

### Import Errors
If you get import errors, ensure all dependencies are installed:
```bash
pip install -r requirements.txt --upgrade
```

### Port Already in Use
If port 8089 is already in use, specify a different port:
```bash
locust -f main.py --web-port 8090
```

### Config Not Found
Ensure your config files are in the `configs/` directory with `.yaml` extension.
