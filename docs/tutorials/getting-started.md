<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Getting Started with Pasture Management System

Welcome to the Pasture Management System (PMS)! This tutorial will guide you through installing, configuring, and using PMS to track issues in your homelab.

## What is PMS?

The Pasture Management System is a lightweight issue tracking system built on Roundup, designed specifically for homelab administrators who need to track problems, maintenance tasks, and improvements across their infrastructure.

## Prerequisites

Before you begin, ensure you have:

- Python 3.9 or later
- macOS, Linux, or Windows with WSL
- Basic command-line knowledge
- 50 MB of free disk space

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/jrjsmrtn/pasture-management-system.git
cd pasture-management-system
```

### Step 2: Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Playwright Browsers

```bash
playwright install chromium
```

## Initial Setup

### Initialize the Roundup Tracker

```bash
roundup-admin install -t classic tracker
```

When prompted, configure:

- **Tracker home**: `tracker` (default)
- **Template**: `classic` (default)

### Initialize the Database

```bash
roundup-admin -i tracker initialise
```

When prompted, set:

- **Admin username**: `admin` (or your preferred username)
- **Admin password**: Choose a secure password

### Start the Tracker

```bash
roundup-server -p 8080 pms=tracker
```

The tracker is now running at: http://localhost:8080/pms/

## Creating Your First Issue

### Via Web UI

1. Open your browser and navigate to http://localhost:8080/pms/
1. Log in with your admin credentials
1. Click on "New Issue" or navigate to http://localhost:8080/pms/issue?@template=item
1. Fill in the issue details:
   - **Title**: "Test Issue - Server backup failed"
   - **Priority**: Select "urgent" from the dropdown
1. Click "Submit new entry"
1. You'll see a success message with the issue ID

### Via Command Line

```bash
roundup-admin -i tracker create issue title="Database slow query" priority=2
```

This will return the new issue ID, for example: `1`

### Via REST API

```bash
curl -X POST http://localhost:8080/pms/rest/data/issue \
  -u admin:admin \
  -H "Content-Type: application/json" \
  -H "X-Requested-With: XMLHttpRequest" \
  -H "Origin: http://localhost:8080" \
  -H "Referer: http://localhost:8080/pms/" \
  -d '{
    "title": "Network connectivity intermittent",
    "priority": "2"
  }'
```

## Viewing Issues

### List All Issues

Navigate to http://localhost:8080/pms/issue to see all issues in a table format.

### View Issue Details

Click on any issue title to see full details including:

- Title
- Status
- Priority
- Creation date
- Messages and attachments

## Understanding Priorities

PMS uses the following priority levels:

| Priority | ID  | Use Case                                               |
| -------- | --- | ------------------------------------------------------ |
| Critical | 1   | System down, data loss, security breach                |
| Urgent   | 2   | Major functionality broken, immediate attention needed |
| Bug      | 3   | Non-critical bugs, workaround available                |
| Feature  | 4   | New feature requests                                   |
| Wish     | 5   | Nice-to-have improvements                              |

## Running Tests

PMS includes comprehensive BDD tests covering all functionality:

```bash
behave features/issue_tracking/
```

This runs:

- Web UI tests (Playwright)
- CLI tests (roundup-admin)
- REST API tests (requests library)

## Development Workflow

### Running the Tracker

For development, start the tracker in the foreground:

```bash
roundup-server -p 8080 pms=tracker
```

Press `Ctrl+C` to stop.

### Running Specific Tests

```bash
# Web UI tests only
behave features/issue_tracking/create_issue_web.feature

# CLI tests only
behave features/issue_tracking/create_issue_cli.feature

# API tests only
behave features/issue_tracking/create_issue_api.feature

# View tests only
behave features/issue_tracking/view_issues.feature

# Smoke tests only
behave features/issue_tracking/ --tags=@smoke
```

### Viewing Test Screenshots

Test screenshots are saved to `screenshots/` on failure. Open them to debug UI issues.

## Troubleshooting

### Tracker Won't Start

**Problem**: `Address already in use` error

**Solution**: Another process is using port 8080. Either:

- Stop the other process
- Use a different port: `roundup-server -p 8081 pms=tracker`

### Login Fails

**Problem**: "Invalid username or password"

**Solution**: Reset admin password:

```bash
roundup-admin -i tracker set user1 password=newpassword
```

### Tests Fail with Timeout

**Problem**: Playwright times out waiting for elements

**Solution**:

1. Ensure the tracker is running: `roundup-server -p 8080 pms=tracker`
1. Check the tracker is accessible: `curl http://localhost:8080/pms/`
1. Increase timeout in `features/environment.py` if needed

### REST API Returns 400

**Problem**: "Required Header Missing"

**Solution**: Ensure you include all required headers:

- `X-Requested-With: XMLHttpRequest`
- `Origin: http://localhost:8080`
- `Referer: http://localhost:8080/pms/`

## Next Steps

Now that you have PMS running, you can:

1. **Customize the tracker**: Edit `tracker/schema.py` to add custom fields
1. **Configure email**: Set up email notifications in `tracker/config.ini`
1. **Add users**: Create additional users with `roundup-admin`
1. **Integrate with monitoring**: Use the REST API to create issues from monitoring tools
1. **Deploy to production**: Set up a reverse proxy and systemd service

## Getting Help

- **Documentation**: See `docs/` directory for detailed guides
- **Issues**: Report bugs at https://github.com/jrjsmrtn/pasture-management-system/issues
- **BDD Examples**: Check `features/` for usage examples

## License

Pasture Management System is licensed under the MIT License. See LICENSE for details.
