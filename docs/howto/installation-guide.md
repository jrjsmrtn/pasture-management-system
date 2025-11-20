<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Installation Guide

**Audience**: Homelab sysadmins and developers installing PMS for the first time

**Purpose**: Step-by-step instructions to install and configure the Pasture Management System

**Estimated Time**: 20-30 minutes

## System Requirements

### Hardware Requirements

**Minimum**:

- CPU: 1 core
- RAM: 512 MB
- Disk: 500 MB free space

**Recommended** (for optimal performance):

- CPU: 2+ cores
- RAM: 1 GB
- Disk: 2 GB free space (includes room for database growth)

### Software Requirements

**Operating System**:

- Linux (Ubuntu 20.04+, Debian 11+, RHEL 8+, or similar)
- macOS 11+ (Big Sur or later)
- Windows 10+ with WSL2 (recommended) or native Python

**Python**:

- Python 3.9 or later
- `pip` package manager
- `venv` module (usually included with Python)

**Optional but Recommended**:

- `uv` - Fast Python package manager (10-100x faster than pip)
- Git - For version control and updates

**Browser** (for web UI):

- Chromium/Chrome (for Playwright testing)
- Firefox, Safari, or Edge (for general use)

## Installation Methods

Choose one of the following installation methods based on your preference.

### Method 1: Installation with uv (Recommended)

`uv` is a fast Python package manager that provides better performance and dependency resolution.

#### Step 1: Install uv

**macOS/Linux**:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows** (PowerShell):

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify installation:

```bash
uv --version
```

#### Step 2: Clone the Repository

```bash
git clone https://github.com/yourusername/pasture-management-system.git
cd pasture-management-system
```

#### Step 3: Create Virtual Environment and Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies with uv
uv pip install -r requirements.txt

# Install development dependencies (optional, for contributors)
uv pip install -e ".[dev]"
```

#### Step 4: Install Playwright Browsers

```bash
playwright install chromium
```

**Verification**:

```bash
python3 -c "import roundup; print(f'Roundup version: {roundup.__version__}')"
python3 -c "import behave; print('Behave installed successfully')"
python3 -c "import playwright; print('Playwright installed successfully')"
```

### Method 2: Installation with pip

Standard Python package manager installation.

#### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/pasture-management-system.git
cd pasture-management-system
```

#### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt

# Install development dependencies (optional, for contributors)
pip install -e ".[dev]"
```

#### Step 4: Install Playwright Browsers

```bash
playwright install chromium
```

**Verification**:

```bash
python3 -c "import roundup; print(f'Roundup version: {roundup.__version__}')"
```

### Method 3: From Source (Advanced)

For contributors or those who want to modify the source code.

```bash
# Clone repository
git clone https://github.com/yourusername/pasture-management-system.git
cd pasture-management-system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in editable mode with all development dependencies
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium

# Install pre-commit hooks (for contributors)
pre-commit install
pre-commit install --hook-type pre-push
```

## Roundup Tracker Initialization

After installing dependencies, initialize the Roundup tracker database.

### Quick Initialization (Recommended)

Use the provided reset script for one-command setup:

```bash
./scripts/reset-test-db.sh admin
```

This script will:

1. Stop any running Roundup servers
1. Remove existing database
1. Initialize fresh database with admin password "admin"
1. Start Roundup server on port 9080

**Custom admin password**:

```bash
./scripts/reset-test-db.sh your_secure_password
```

**Initialize without starting server**:

```bash
./scripts/reset-test-db.sh admin --no-server
```

### Manual Initialization (Alternative)

If you prefer manual control or the script doesn't work:

#### Step 1: Initialize Database

```bash
cd tracker
rm -rf db/*  # Clear existing database if any
uv run roundup-admin -i . initialise
cd ..
```

You will be prompted for:

- Admin username (default: `admin`)
- Admin password (choose a secure password)
- Admin email (optional)

#### Step 2: Verify Database

```bash
ls -la tracker/db/
```

You should see database files including `user.db`, `issue.db`, etc.

## Database Setup

PMS uses SQLite as the default database backend (configured in Roundup).

### Default Configuration

The default database configuration is:

- **Backend**: SQLite (via Roundup's `anydbm` backend)
- **Location**: `tracker/db/`
- **Files**: Multiple `.db` files for different object types

### Configuration File

The main configuration is in `tracker/config.ini`:

```ini
[main]
database = db
template_engine = zopetal
templates = html
```

**Important**: Do not modify `config.ini` unless you understand Roundup configuration.

### Database Permissions

Ensure the database directory is writable:

```bash
chmod 755 tracker/db
```

## First-Run Configuration

### Step 1: Start the Roundup Server

```bash
uv run roundup-server -p 9080 pms=tracker
```

**Parameters**:

- `-p 9080`: Port number (change if 9080 is in use)
- `pms=tracker`: Tracker name and directory (`pms` is the URL path, `tracker` is the directory)

**Running in background**:

```bash
uv run roundup-server -p 9080 pms=tracker > /dev/null 2>&1 &
```

### Step 2: Access the Web Interface

Open your browser and navigate to:

```
http://localhost:9080/pms/
```

You should see the PMS login page.

### Step 3: Log In

Use the admin credentials you created during initialization:

- **Username**: `admin`
- **Password**: (the password you set, default: `admin`)

### Step 4: Verify Installation

After logging in:

1. Check the home page displays correctly
1. Navigate to "Issues" - should show empty issue list
1. Navigate to "CIs" - should show empty CI list
1. Navigate to "Changes" - should show empty change list
1. Check the CMDB Dashboard - should display with 0 items

## Verification Steps

### Verify Server is Running

```bash
curl -s http://localhost:9080/pms/ | grep -q "Roundup" && echo "Server is running" || echo "Server is not running"
```

### Verify Dependencies

```bash
# Check Python version
python3 --version  # Should be 3.9+

# Check Roundup
uv run roundup-admin -h | head -1

# Check Behave (for BDD testing)
behave --version

# Check Playwright (for web UI testing)
playwright --version
```

### Run Smoke Tests

```bash
# Run BDD smoke tests
behave --tags=@smoke

# Run unit tests (if available)
pytest tests/
```

### Check Server Logs

If running in foreground, logs appear in the terminal.

If running in background:

```bash
# Check if server process is running
ps aux | grep roundup-server

# Stop server
pkill -f "roundup-server"
```

## Common Installation Issues

### Issue 1: Python Version Too Old

**Symptom**:

```
ERROR: This package requires Python 3.9 or later
```

**Solution**:

Install Python 3.9 or later:

```bash
# macOS with Homebrew
brew install python@3.9

# Ubuntu/Debian
sudo apt-get install python3.9

# Check version
python3 --version
```

### Issue 2: Port 9080 Already in Use

**Symptom**:

```
error: [Errno 48] Address already in use
```

**Solution**:

Either stop the existing service or use a different port:

```bash
# Find process using port 9080
lsof -i :9080

# Kill existing Roundup server
pkill -f "roundup-server"

# Or use a different port
uv run roundup-server -p 9081 pms=tracker
```

### Issue 3: Database Permission Denied

**Symptom**:

```
PermissionError: [Errno 13] Permission denied: 'tracker/db/user.db'
```

**Solution**:

Fix database directory permissions:

```bash
chmod -R 755 tracker/db
```

### Issue 4: Playwright Browser Installation Failed

**Symptom**:

```
Error: Browser was not installed
```

**Solution**:

Install Playwright browsers manually:

```bash
# Install Chromium only (faster)
playwright install chromium

# Or install all browsers
playwright install
```

### Issue 5: Module Not Found

**Symptom**:

```
ModuleNotFoundError: No module named 'roundup'
```

**Solution**:

Ensure virtual environment is activated and dependencies are installed:

```bash
source venv/bin/activate
uv pip install -r requirements.txt
```

### Issue 6: Database Already Initialized Error

**Symptom**:

```
Database already initialized
```

**Solution**:

Remove existing database and reinitialize:

```bash
./scripts/reset-test-db.sh admin
```

Or manually:

```bash
cd tracker
rm -rf db/*
uv run roundup-admin -i . initialise
cd ..
```

### Issue 7: uv Command Not Found

**Symptom**:

```
bash: uv: command not found
```

**Solution**:

Either install `uv` or use `pip` instead:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or replace 'uv run' with direct Python execution
python3 -m roundup.admin -i tracker initialise
python3 -m roundup.server -p 9080 pms=tracker
```

### Issue 8: Pre-commit Hooks Failing

**Symptom** (for contributors):

```
pre-commit hook failed
```

**Solution**:

Install and update pre-commit hooks:

```bash
pre-commit install
pre-commit autoupdate
pre-commit run --all-files
```

## Next Steps

After successful installation:

1. **[Deployment Guide](deployment-guide.md)**: Configure PMS for production use
1. **[Administration Guide](administration-guide.md)**: Learn how to administer PMS
1. **[Managing Issue Lifecycle](managing-issue-lifecycle.md)**: Create and manage issues
1. **[Submit Change Request](submit-change-request.md)**: Create change requests
1. **[Documenting Infrastructure Dependencies](documenting-infrastructure-dependencies.md)**: Manage CIs in the CMDB

## Getting Help

### Documentation

- [How-to Guides](../howto/): Task-specific guides
- [Reference Documentation](../reference/): Technical reference
- [Tutorials](../tutorials/): Learning-oriented guides

### Troubleshooting

- [Debugging BDD Scenarios](debugging-bdd-scenarios.md): For BDD test issues
- [Roundup Development Practices](../reference/roundup-development-practices.md): For Roundup-specific issues

### Community Support

- **GitHub Issues**: [https://github.com/yourusername/pasture-management-system/issues](https://github.com/yourusername/pasture-management-system/issues)
- **GitHub Discussions**: [https://github.com/yourusername/pasture-management-system/discussions](https://github.com/yourusername/pasture-management-system/discussions)

## Related Documentation

- [Deployment Guide](deployment-guide.md) - Production deployment patterns
- [Administration Guide](administration-guide.md) - System administration procedures
- [Roundup Development Practices](../reference/roundup-development-practices.md) - Roundup-specific guidance
- [Architecture Overview](../explanation/architecture-overview.md) - System architecture

______________________________________________________________________

**Document Version**: 1.0.0
**Last Updated**: 2025-11-20
**Maintained By**: PMS Team
