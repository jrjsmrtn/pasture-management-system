<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Four-Interface BDD Testing Tutorial

**Audience**: BDD practitioners, Python developers, QA engineers
**Prerequisites**: Basic understanding of Gherkin/BDD, Python, and API testing
**Estimated Time**: 60-90 minutes
**Technologies**: Behave (Python BDD), Playwright (Web UI), REST APIs, Email (SMTP/IMAP)

## Overview

This tutorial teaches you how to achieve comprehensive BDD test coverage by testing the same functionality across **four different interfaces**:

1. **Web UI** (Playwright browser automation)
1. **CLI** (Command-line interface)
1. **API** (REST API)
1. **Email** (Email gateway integration)

By testing across multiple interfaces, you ensure:

- **Interface parity**: All interfaces behave consistently
- **Complete coverage**: Every user journey is validated
- **Integration confidence**: Cross-interface workflows work correctly
- **Regression protection**: Changes to one interface don't break others

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Write BDD scenarios that test the same operation across 4 interfaces
1. Implement step definitions for Web UI, CLI, API, and Email
1. Use cross-interface verification to validate integration
1. Apply variable substitution for dynamic test data
1. Troubleshoot common issues in multi-interface testing

## Why Four Interfaces?

Most issue tracking systems provide multiple ways to interact with them:

- **Web UI**: Point-and-click interface for casual users
- **CLI**: Scriptable interface for automation and power users
- **API**: Programmatic interface for integrations
- **Email**: Natural communication channel for notifications and updates

**The Challenge**: Ensuring all 4 interfaces behave consistently and integrate seamlessly.

**The Solution**: Four-interface BDD testing validates that creating an issue via email produces the same result as creating it via Web UI, CLI, or API.

## Project Structure

```
pasture-management-system/
├── features/
│   ├── issue_tracking/
│   │   ├── four_interface_testing.feature  # Main tutorial feature
│   │   ├── create_issue_email.feature      # Email-specific scenarios
│   │   └── ...
│   ├── steps/
│   │   ├── web_ui_steps.py                 # Playwright step definitions
│   │   ├── cli_steps.py                    # CLI step definitions
│   │   ├── api_steps.py                    # REST API step definitions
│   │   └── email_steps.py                  # Email step definitions
│   └── environment.py                       # Test fixtures and setup
└── tests/
    └── utils/
        ├── playwright_helpers.py            # Web UI helpers
        ├── api_client.py                    # API client
        └── greenmail_client.py              # Email server client
```

## Interface 1: Web UI Testing (Playwright)

### Step Definition Example

```python
# features/steps/web_ui_steps.py

from behave import given, when, then
from playwright.sync_api import sync_playwright, expect

@given('I am logged in as "{username}" with password "{password}"')
def step_login(context, username, password):
    """Log in to the web interface using Playwright."""
    page = context.page  # Playwright page from environment.py

    page.goto("http://localhost:9080/pms/")
    page.fill('input[name="__login_name"]', username)
    page.fill('input[name="__login_password"]', password)
    page.click('button[type="submit"]')

    # Verify login succeeded
    expect(page.locator("body")).to_contain_text("Logged in")

@when("I navigate to the new issue page")
def step_navigate_new_issue(context):
    """Navigate to the new issue creation page."""
    context.page.goto("http://localhost:9080/pms/issue?@template=item")

@when("I fill in the issue form")
def step_fill_issue_form(context):
    """Fill in the issue creation form."""
    page = context.page

    for row in context.table:
        field = row['field']
        value = row['value']

        if field == 'title':
            page.fill('input[name="title"]', value)
        elif field == 'priority':
            page.select_option('select[name="priority"]', label=value)

@when("I submit the form")
def step_submit_form(context):
    """Submit the current form."""
    context.page.click('button[type="submit"]')

@then('I should see "{text}" on the page')
def step_verify_text_on_page(context, text):
    """Verify text appears on the current page."""
    expect(context.page.locator("body")).to_contain_text(text)
```

### Gherkin Scenario

```gherkin
@four-interface @web-ui @smoke
Scenario: Create issue via Web UI
  Given I am logged in as "admin" with password "admin"
  When I navigate to the new issue page
  And I fill in the issue form:
    | field    | value                     |
    | title    | Web UI Test Issue         |
    | priority | urgent                    |
  And I submit the form
  Then I should see "Web UI Test Issue" on the page
  And the issue should be created in the database
```

### Key Patterns

**Playwright Best Practices**:

- Use **locators by name attribute** for form fields: `input[name="title"]`
- Use **expect() for assertions** instead of plain assert
- **Wait for navigation** after form submissions
- **Take screenshots on failure** (configured in environment.py)
- Test at **1024x768 resolution** for consistency

## Interface 2: CLI Testing

### Step Definition Example

```python
# features/steps/cli_steps.py

import subprocess
from behave import when, then

@when("I create an issue via CLI with")
def step_create_issue_cli(context):
    """Create an issue using roundup-admin CLI."""
    tracker_dir = "tracker"

    # Extract field values from table
    title = None
    priority = None
    for row in context.table:
        if row['field'] == 'title':
            title = row['value']
        elif row['field'] == 'priority':
            priority = row['value']

    # Create message first (issues require messages)
    msg_cmd = [
        "roundup-admin", "-i", tracker_dir,
        "create", "msg",
        f"content=Issue created: {title}",
        "author=1"  # admin user
    ]
    msg_result = subprocess.run(msg_cmd, capture_output=True, text=True, timeout=30)
    assert msg_result.returncode == 0, f"Failed to create message: {msg_result.stderr}"

    message_id = msg_result.stdout.strip()

    # Look up priority ID
    priority_id = None
    if priority:
        priority_cmd = ["roundup-admin", "-i", tracker_dir, "find", "priority", f"name={priority}"]
        priority_result = subprocess.run(priority_cmd, capture_output=True, text=True, timeout=30)
        priority_id = priority_result.stdout.strip()

    # Create issue
    issue_cmd = [
        "roundup-admin", "-i", tracker_dir,
        "create", "issue",
        f"title={title}",
        f"messages={message_id}",
        "status=1"  # new
    ]
    if priority_id:
        issue_cmd.append(f"priority={priority_id}")

    issue_result = subprocess.run(issue_cmd, capture_output=True, text=True, timeout=30)
    assert issue_result.returncode == 0, f"Failed to create issue: {issue_result.stderr}"

    context.created_issue_id = issue_result.stdout.strip()

@when('I update issue "{issue_id}" status to "{status}" via CLI')
def step_update_issue_status_cli(context, issue_id, status):
    """Update issue status via CLI."""
    tracker_dir = "tracker"

    # Look up status ID
    status_cmd = ["roundup-admin", "-i", tracker_dir, "find", "status", f"name={status}"]
    status_result = subprocess.run(status_cmd, capture_output=True, text=True, timeout=30)
    status_id = status_result.stdout.strip()

    # Update issue
    update_cmd = [
        "roundup-admin", "-i", tracker_dir,
        "set", f"issue{issue_id}",
        f"status={status_id}"
    ]
    result = subprocess.run(update_cmd, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, f"Failed to update issue: {result.stderr}"
```

### Gherkin Scenario

```gherkin
@four-interface @cli @smoke
Scenario: Create issue via CLI
  When I create an issue via CLI with:
    | field    | value                |
    | title    | CLI Test Issue       |
    | priority | urgent               |
  Then the issue should be created
  And the issue title should be "CLI Test Issue"
  And the issue priority should be "urgent"
```

### Key Patterns

**CLI Testing Best Practices**:

- Use **subprocess.run()** with timeout for safety
- **Capture stderr** for error diagnostics
- **Look up IDs** (priority, status) before setting properties
- **Create message first** (Roundup requirement)
- **Store created IDs** in context for verification

## Interface 3: API Testing (REST)

### Step Definition Example

```python
# features/steps/api_steps.py

import requests
from behave import when, then

@when("I create an issue via API with")
def step_create_issue_api(context):
    """Create an issue via REST API."""
    base_url = "http://localhost:9080/pms/rest/data"

    # Extract field values
    data = {}
    for row in context.table:
        field = row['field']
        value = row['value']
        data[field] = value

    # Look up priority ID if provided
    if 'priority' in data:
        priority_name = data['priority']
        priority_response = requests.get(
            f"{base_url}/priority",
            params={"@filter": f"name={priority_name}"}
        )
        priorities = priority_response.json()['data']['collection']
        if priorities:
            data['priority'] = priorities[0]['id']

    # Set default status to "new"
    if 'status' not in data:
        status_response = requests.get(
            f"{base_url}/status",
            params={"@filter": "name=new"}
        )
        statuses = status_response.json()['data']['collection']
        if statuses:
            data['status'] = statuses[0]['id']

    # Create issue
    response = requests.post(
        f"{base_url}/issue",
        json=data,
        headers={"Content-Type": "application/json"}
    )

    context.api_response = response
    if response.status_code in (200, 201):
        context.created_issue_id = response.json()['data']['id']

@when('I update issue "{issue_id}" via API with')
def step_update_issue_api(context, issue_id):
    """Update an issue via REST API."""
    base_url = "http://localhost:9080/pms/rest/data"

    # Extract field values
    data = {}
    for row in context.table:
        field = row['field']
        value = row['value']

        # Look up IDs for linked properties
        if field in ('status', 'priority'):
            lookup_response = requests.get(
                f"{base_url}/{field}",
                params={"@filter": f"name={value}"}
            )
            items = lookup_response.json()['data']['collection']
            if items:
                data[field] = items[0]['id']
        else:
            data[field] = value

    # Update issue
    response = requests.patch(
        f"{base_url}/issue/{issue_id}",
        json=data,
        headers={"Content-Type": "application/json"}
    )

    context.api_response = response

@then("the API response should be successful")
def step_verify_api_success(context):
    """Verify API response indicates success."""
    assert context.api_response.status_code in (200, 201), (
        f"API request failed with status {context.api_response.status_code}: "
        f"{context.api_response.text}"
    )
```

### Gherkin Scenario

```gherkin
@four-interface @api @smoke
Scenario: Create issue via API
  When I create an issue via API with:
    | field    | value                |
    | title    | API Test Issue       |
    | priority | urgent               |
  Then the API response should be successful
  And the issue should be created in the database
  And the issue title should be "API Test Issue"
  And the issue priority should be "urgent"
```

### Key Patterns

**API Testing Best Practices**:

- Use **requests library** for HTTP calls
- **Look up linked property IDs** (status, priority) before POST/PATCH
- **Store response** in context for assertions
- **Check status codes** (200, 201, 204)
- **Parse JSON** responses for created IDs
- **Set Content-Type: application/json** header

## Interface 4: Email Testing

### Step Definition Example

```python
# features/steps/email_steps.py

from email.mime.text import MIMEText
import subprocess
from behave import given, when, then

@given("I compose an email with")
def step_compose_email(context):
    """Compose an email message."""
    email_data = {}
    for row in context.table:
        email_data[row['field']] = row['value']

    # Create MIME message
    msg = MIMEText(email_data.get('body', ''))
    msg['From'] = email_data['from']
    msg['To'] = email_data['to']
    msg['Subject'] = email_data['subject']

    context.email_message = msg

@when("I send the email to the mail gateway")
def step_send_email_to_gateway(context):
    """Send email to roundup-mailgw via PIPE."""
    tracker_dir = "tracker"

    # Use roundup-mailgw in PIPE mode
    cmd = ["roundup-mailgw", "-C", tracker_dir, "pipe"]

    result = subprocess.run(
        cmd,
        input=context.email_message.as_string(),
        capture_output=True,
        text=True,
        timeout=30
    )

    # Store result for verification
    context.mailgw_result = result

@then("a new issue should be created")
def step_verify_issue_created(context):
    """Verify a new issue was created."""
    tracker_dir = "tracker"

    # List all issues
    cmd = ["roundup-admin", "-i", tracker_dir, "list", "issue"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    issues = [line for line in result.stdout.strip().split('\n') if line.strip()]
    assert len(issues) > 0, "Expected at least one issue to be created"

    # Store the last created issue ID
    last_issue = issues[-1].split(':')[0].strip()
    context.created_issue_id = last_issue
```

### Gherkin Scenario

```gherkin
@four-interface @email @smoke
Scenario: Create issue via Email
  Given I compose an email with:
    | field   | value                                      |
    | from    | roundup-admin@localhost                    |
    | to      | issue_tracker@localhost                    |
    | subject | Email Test Issue [priority=urgent]        |
    | body    | This issue was created via email gateway  |
  When I send the email to the mail gateway
  Then a new issue should be created
  And the issue title should be "Email Test Issue"
  And the issue priority should be "urgent"
```

### Key Patterns

**Email Testing Best Practices**:

- Use **email.mime for message construction**
- Use **roundup-mailgw PIPE mode** for fast testing
- **Parse subject for properties**: `[priority=urgent]`, `[status=in-progress]`
- **Support GreenMail mode** for full SMTP/IMAP testing
- **Silent rejection** of unknown users (security)

## Cross-Interface Verification

The real power of four-interface testing is **cross-interface verification**: create via one interface, verify via another.

### Example: Email → Web UI

```gherkin
@four-interface @integration
Scenario: Create via Email, verify via Web UI
  Given I compose an email with:
    | field   | value                              |
    | from    | roundup-admin@localhost            |
    | to      | issue_tracker@localhost            |
    | subject | Cross-interface Test Issue         |
    | body    | Created via email, verified via UI |
  When I send the email to the mail gateway
  Then a new issue should be created
  And I am logged in as "admin" with password "admin"
  And I navigate to the issues list
  And I should see "Cross-interface Test Issue" on the page
```

**Why This Matters**: Ensures the email gateway integration writes to the same database that the Web UI reads from.

### Example: CLI → API → Web UI

```gherkin
@four-interface @integration
Scenario: Create via CLI, update via API, verify via Web UI
  When I create an issue via CLI with:
    | field | value                |
    | title | Multi-interface Test |
  Then the issue should be created
  When I update the last created issue via API with:
    | field  | value       |
    | status | in-progress |
  Then the API response should be successful
  And I am logged in as "admin" with password "admin"
  And I navigate to the last created issue
  And I should see "in-progress" on the page
```

**Why This Matters**: Validates that all three interfaces share the same backend state.

## Variable Substitution Patterns

Variable substitution allows you to reference dynamically created data in later steps.

### Pattern 1: Note and Substitute with Curly Braces

```gherkin
Scenario: Create via API, update via Email using variable
  When I create an issue via API with:
    | field | value           |
    | title | API Email Test  |
  Then the API response should be successful
  And I note the created issue ID as "api_issue"
  When I compose an email with:
    | field   | value                                |
    | from    | roundup-admin@localhost              |
    | to      | issue_tracker@localhost              |
    | subject | [{api_issue}] API Email Test         |
    | body    | Adding message via email             |
  And I send the email to the mail gateway
  Then the issue "{api_issue}" should have a new message
```

**Step Implementation**:

```python
@then('I note the created issue ID as "{variable_name}"')
def step_note_issue_id(context, variable_name):
    """Store the created issue ID for later use."""
    if not hasattr(context, 'issue_variables'):
        context.issue_variables = {}
    context.issue_variables[variable_name] = context.created_issue_id

@then('the issue "{issue_id}" should have a new message')
def step_verify_issue_message(context, issue_id):
    """Verify issue has a new message."""
    # Substitute variable if present
    variable_name = issue_id.strip("{}")
    if hasattr(context, 'issue_variables') and variable_name in context.issue_variables:
        issue_id = context.issue_variables[variable_name]

    # ... verification logic
```

### Pattern 2: Automatic Context Tracking

```python
# Store in context
context.created_issue_id = "123"
context.last_created_issue_id = "123"

# Reference in later steps
@when("I navigate to the last created issue")
def step_navigate_last_issue(context):
    issue_id = context.last_created_issue_id
    context.page.goto(f"http://localhost:9080/pms/issue{issue_id}")
```

## Database Verification (Common Step)

All four interfaces should ultimately write to the same database. A common verification step validates this:

```python
@then('the issue title should be "{expected_title}"')
def step_verify_issue_title(context, expected_title):
    """Verify issue title in database (interface-agnostic)."""
    tracker_dir = "tracker"
    issue_id = context.created_issue_id

    cmd = ["roundup-admin", "-i", tracker_dir, "get", f"issue{issue_id}", "title"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    actual_title = result.stdout.strip()
    assert actual_title == expected_title, (
        f"Expected title '{expected_title}', got '{actual_title}'"
    )
```

This step can be used after **any** interface operation to verify the result.

## Test Environment Setup

### environment.py (Behave Fixtures)

```python
# features/environment.py

from playwright.sync_api import sync_playwright
import subprocess
import time

def before_all(context):
    """Set up test environment before all scenarios."""
    # Start Playwright for Web UI tests
    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(headless=True)
    context.context_browser = context.browser.new_context(
        viewport={'width': 1024, 'height': 768}
    )

def before_scenario(context, scenario):
    """Set up before each scenario."""
    # Reset database for clean slate
    subprocess.run(["./scripts/reset-test-db.sh", "admin", "--no-server"], check=True)
    time.sleep(1)

    # Create new Playwright page for @web-ui scenarios
    if 'web-ui' in scenario.tags:
        context.page = context.context_browser.new_page()

def after_scenario(context, scenario):
    """Clean up after each scenario."""
    # Take screenshot on failure
    if scenario.status == 'failed' and hasattr(context, 'page'):
        try:
            screenshot_path = f"reports/screenshots/{scenario.name}.png"
            context.page.screenshot(path=screenshot_path)
        except Exception:
            pass

    # Close page
    if hasattr(context, 'page'):
        context.page.close()

def after_all(context):
    """Tear down test environment."""
    if hasattr(context, 'browser'):
        context.browser.close()
    if hasattr(context, 'playwright'):
        context.playwright.stop()
```

## Troubleshooting Guide

### Issue 1: Playwright Page Not Found

**Symptom**: `AttributeError: 'Context' object has no attribute 'page'`

**Cause**: Forgot to tag scenario with `@web-ui`

**Solution**: Add `@web-ui` tag to trigger Playwright page creation:

```gherkin
@four-interface @web-ui  # <- Add this tag
Scenario: Create issue via Web UI
```

### Issue 2: CLI Creates Issue But Web UI Doesn't Show It

**Symptom**: Issue visible via CLI but not in Web UI

**Cause**: Database not refreshed, or server caching

**Solution**: Restart Roundup server after database changes:

```bash
pkill -f "roundup-server" && sleep 2
roundup-server -p 9080 pms=tracker &
```

### Issue 3: Variable Substitution Not Working

**Symptom**: `{api_issue}` appears literally instead of being substituted

**Cause**: Forgot to strip curly braces in step definition

**Solution**: Strip braces before lookup:

```python
variable_name = issue_id.strip("{}")  # Remove { and }
if hasattr(context, 'issue_variables') and variable_name in context.issue_variables:
    issue_id = context.issue_variables[variable_name]
```

### Issue 4: Email Tests Slow (>5 seconds each)

**Symptom**: Email scenarios take 5+ seconds

**Cause**: Using GreenMail mode (full SMTP/IMAP)

**Solution**: Use PIPE mode for fast tests (default):

```bash
# Fast mode (default)
behave features/issue_tracking/email_security.feature

# Comprehensive mode (slower)
EMAIL_TEST_MODE=greenmail behave features/issue_tracking/email_security.feature
```

### Issue 5: API Returns 404 for Lookups

**Symptom**: `requests.get(f"{base_url}/status")` returns 404

**Cause**: Incorrect API endpoint or filter syntax

**Solution**: Check Roundup REST API documentation:

```python
# Correct filter syntax
response = requests.get(
    f"{base_url}/status",
    params={"@filter": "name=new"}  # Use @filter parameter
)
```

### Issue 6: Database Out of Sync

**Symptom**: Tests fail intermittently with "issue not found"

**Cause**: Previous test didn't clean up properly

**Solution**: Use `reset-test-db.sh` in `before_scenario`:

```python
def before_scenario(context, scenario):
    subprocess.run(["./scripts/reset-test-db.sh", "admin", "--no-server"], check=True)
    time.sleep(1)  # Give database time to reset
```

## Best Practices Summary

### 1. Test Coverage Strategy

- **Priority 1**: Test each critical operation via all 4 interfaces (create, update, list)
- **Priority 2**: Test cross-interface workflows (email→web, cli→api→web)
- **Priority 3**: Test interface-specific features (email attachments, web UI forms)

### 2. Naming Conventions

```gherkin
# Pattern: <Operation> via <Interface>
Scenario: Create issue via Web UI
Scenario: Update issue via CLI
Scenario: Set priority via API
Scenario: Add message via Email

# Pattern: Cross-interface verification
Scenario: Create via Email, verify via Web UI
Scenario: Create via CLI, update via API, verify via Web UI
```

### 3. Tag Strategy

```gherkin
@four-interface      # All scenarios in this pattern
@web-ui              # Triggers Playwright setup
@cli                 # CLI-specific tags
@api                 # API-specific tags
@email               # Email-specific tags
@smoke               # Critical path scenarios
@integration         # Cross-interface scenarios
```

### 4. Step Definition Organization

```
features/steps/
├── web_ui_steps.py       # Playwright locators, navigation
├── cli_steps.py          # subprocess.run(), roundup-admin
├── api_steps.py          # requests library, REST endpoints
├── email_steps.py        # email.mime, roundup-mailgw
└── common_steps.py       # Database verification (shared)
```

### 5. Performance Optimization

**Fast Tests** (for CI/CD):

- Use PIPE mode for email (0.17s/test)
- Headless Playwright (--headed only for debugging)
- Parallel execution: `behave -j 4`

**Comprehensive Tests** (for releases):

- GreenMail mode for email (5.2s/test, full SMTP/IMAP)
- Headed Playwright for visual debugging
- Sequential execution for stability

## Real-World Example: Complete Test Suite

Our project has **169 BDD scenarios** across 4 interfaces:

- **Web UI** (@web-ui): 76 scenarios (45%)
- **CLI** (@cli): 21 scenarios (12%)
- **API** (@api): 37 scenarios (22%)
- **Email** (@email): 12 scenarios (7%)
- **Mixed/Integration**: 23 scenarios (14%)

**Coverage Areas**:

- Issue tracking: 59 scenarios
- Change management: 69 scenarios
- CMDB: 41 scenarios

**Test Execution**:

- Fast mode: ~3 minutes (PIPE email, headless browser, parallel)
- Full mode: ~15 minutes (GreenMail, headed browser, sequential)

## Conclusion

Four-interface BDD testing ensures:

✅ **Consistent behavior** across all user interfaces
✅ **Complete coverage** of integration points
✅ **Confidence in deployments** - if tests pass, all interfaces work
✅ **Regression protection** - changes to one interface can't break others
✅ **Living documentation** - scenarios demonstrate how to use each interface

### Next Steps

1. **Read the code**: Explore `features/issue_tracking/four_interface_testing.feature`
1. **Run the tests**: `behave --tags=@four-interface`
1. **Write your own**: Pick a feature, write scenarios for all 4 interfaces
1. **Cross-verify**: Create via one interface, verify via another
1. **Share your pattern**: Adapt this to your own projects

### Further Reading

- [BDD Testing Best Practices](../reference/bdd-testing-best-practices.md) - Behave fixtures and patterns
- [Roundup Development Practices](../reference/roundup-development-practices.md) - CLI and API usage
- [GreenMail Testing Reference](../reference/greenmail-testing.md) - Email testing modes
- [Email Security Hardening](../howto/email-security-hardening.md) - Email gateway security

## Appendix: Complete Example

Here's a complete example showing all four interfaces for the same operation:

```gherkin
Feature: Four-Interface Demonstration

  @four-interface @web-ui
  Scenario: Create and update via Web UI
    Given I am logged in as "admin" with password "admin"
    When I navigate to the new issue page
    And I fill in the issue form:
      | field    | value         |
      | title    | UI Demo       |
      | priority | critical      |
    And I submit the form
    Then I should see "UI Demo" on the page
    When I update the issue status to "in-progress"
    Then the issue should have status "in-progress"

  @four-interface @cli
  Scenario: Create and update via CLI
    When I create an issue via CLI with:
      | field    | value     |
      | title    | CLI Demo  |
      | priority | critical  |
    Then the issue should be created
    When I update the last created issue status to "in-progress" via CLI
    Then the issue should have status "in-progress"

  @four-interface @api
  Scenario: Create and update via API
    When I create an issue via API with:
      | field    | value     |
      | title    | API Demo  |
      | priority | critical  |
    Then the API response should be successful
    When I update the last created issue via API with:
      | field  | value       |
      | status | in-progress |
    Then the issue should have status "in-progress"

  @four-interface @email
  Scenario: Create and update via Email
    Given I compose an email with:
      | field   | value                                |
      | from    | roundup-admin@localhost              |
      | to      | issue_tracker@localhost              |
      | subject | Email Demo [priority=critical]       |
      | body    | Created via email                    |
    When I send the email to the mail gateway
    Then a new issue should be created
    When I compose an email with:
      | field   | value                                        |
      | from    | roundup-admin@localhost                      |
      | to      | issue_tracker@localhost                      |
      | subject | [issue1] Email Demo [status=in-progress]     |
      | body    | Updated via email                            |
    And I send the email to the mail gateway
    Then the issue should have status "in-progress"
```

**Result**: Same operation tested 4 ways, ensuring complete interface parity!
