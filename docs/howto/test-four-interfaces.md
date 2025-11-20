<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# How to Test Across Four Interfaces

## Overview

This guide shows you how to write and run BDD tests that verify consistent behavior across all four Pasture Management System interfaces: Web UI, CLI, API, and Email.

**Target audience**: Developers and QA engineers writing integration tests

**Prerequisites**:

- Basic BDD/Gherkin knowledge
- Familiarity with Behave framework
- Understanding of the PMS interfaces

## Quick Start

### Run Four-Interface Tests

```bash
# Run all four-interface scenarios
behave features/issue_tracking/four_interface_testing.feature

# Run specific interface tests
behave --tags=@web-ui
behave --tags=@cli
behave --tags=@api
behave --tags=@email

# Run smoke tests (one scenario per interface)
behave --tags=@smoke

# Run integration scenarios (cross-interface workflows)
behave --tags=@integration
```

### Test Results

Current test coverage:

- **15/15 scenarios passing (100%)**
- All 4 interfaces validated
- 0 error scenarios

## Writing Four-Interface Tests

### 1. Test Issue Creation Across All Interfaces

Create a scenario that tests the same operation via each interface:

```gherkin
# Web UI
@four-interface @web-ui @smoke
Scenario: Create issue via Web UI
  Given I am logged in as "admin" with password "admin"
  When I navigate to the new issue page
  And I fill in the issue form:
    | field    | value             |
    | title    | Web UI Test Issue |
    | priority | urgent            |
  And I submit the form
  Then I should see "Web UI Test Issue" on the page
  And the issue should be created in the database

# CLI
@four-interface @cli @smoke
Scenario: Create issue via CLI
  When I create an issue via CLI with:
    | field    | value          |
    | title    | CLI Test Issue |
    | priority | urgent         |
  Then the issue should be created
  And the issue title should be "CLI Test Issue"
  And the issue priority should be "urgent"

# API
@four-interface @api @smoke
Scenario: Create issue via API
  When I create an issue via API with:
    | field    | value          |
    | title    | API Test Issue |
    | priority | urgent         |
  Then the API response should be successful
  And the issue should be created in the database
  And the issue title should be "API Test Issue"

# Email
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
```

### 2. Test Cross-Interface Workflows

Verify that operations across different interfaces work together:

```gherkin
@four-interface @integration
Scenario: Create via CLI, update via API, verify via Web UI
  # Create issue using CLI
  When I create an issue via CLI with:
    | field | value                |
    | title | Multi-interface Test |
  Then the issue should be created

  # Update via API
  When I update the last created issue via API with:
    | field  | value       |
    | status | in-progress |
  Then the API response should be successful

  # Verify via Web UI
  And I am logged in as "admin" with password "admin"
  And I navigate to the last created issue
  And I should see "in-progress" on the page
```

### 3. Use Variable Substitution for Dynamic IDs

Store and reuse issue IDs across steps:

```gherkin
@four-interface @integration
Scenario: Create via API, add message via Email, verify via CLI
  # Create issue via API
  When I create an issue via API with:
    | field | value          |
    | title | API Email Test |
  Then the API response should be successful
  And I note the created issue ID as "api_issue"

  # Add message via Email (using {api_issue} variable)
  When I compose an email with:
    | field   | value                              |
    | from    | roundup-admin@localhost            |
    | to      | issue_tracker@localhost            |
    | subject | [{api_issue}] API Email Test       |
    | body    | Adding message via email           |
  And I send the email to the mail gateway

  # Verify via CLI (using {api_issue} variable)
  Then the issue "{api_issue}" should have a new message
  And I verify via CLI that issue "{api_issue}" has the message
```

## Available Step Definitions

### Web UI Steps

```gherkin
Given I am logged in as "{username}" with password "{password}"
When I navigate to the new issue page
When I fill in the issue form:
  | field    | value      |
  | title    | Issue Name |
  | priority | urgent     |
When I submit the form
When I navigate to issue "{issue_id}"
When I update the issue status to "{status}"
When I select priority "{priority}"
Then I should see "{text}" on the page
```

### CLI Steps

```gherkin
When I create an issue via CLI with:
  | field    | value      |
  | title    | Issue Name |
  | priority | urgent     |
When I update issue "{issue_id}" status to "{status}" via CLI
When I set issue "{issue_id}" priority to "{priority}" via CLI
Then the issue should be created
Then the issue title should be "{expected_title}"
Then the issue priority should be "{expected_priority}"
```

### API Steps

```gherkin
When I create an issue via API with:
  | field    | value      |
  | title    | Issue Name |
  | priority | urgent     |
When I update issue "{issue_id}" via API with:
  | field  | value       |
  | status | in-progress |
Then the API response should be successful
Then the issue should be created in the database
```

### Email Steps

```gherkin
Given I compose an email with:
  | field   | value                       |
  | from    | user@localhost              |
  | to      | issue_tracker@localhost     |
  | subject | Issue Subject [priority=X]  |
  | body    | Issue description           |
When I send the email to the mail gateway
Then a new issue should be created
```

### Cross-Interface Steps

```gherkin
When I note the created issue ID as "{variable_name}"
When I navigate to the last created issue
Then the issue "{issue_id}" should have a new message
Then I verify via CLI that issue "{issue_id}" has the message
```

## Common Patterns

### Pattern 1: Consistent Field Validation

Test that the same fields work identically across all interfaces:

```gherkin
# Verify priority setting works the same way
@four-interface
Scenario Outline: Set priority via <interface>
  Given an issue exists with id "1" and title "Priority Test"
  When I set priority "critical" via <interface>
  Then the issue "1" priority should be "critical"

  Examples:
    | interface |
    | Web UI    |
    | CLI       |
    | API       |
    | Email     |
```

### Pattern 2: Error Handling Consistency

Verify errors are handled consistently:

```gherkin
Scenario: Invalid priority rejected across interfaces
  # Test that invalid priority "super-duper-urgent" fails
  # in the same way for all interfaces
```

### Pattern 3: Cross-Interface Data Flow

Test complete workflows:

```gherkin
Scenario: Issue lifecycle across interfaces
  # Create via Email
  # Assign via Web UI
  # Update status via CLI
  # Add comments via API
  # Verify final state via all interfaces
```

## Troubleshooting

### Server Not Running

If tests fail with "Connection refused":

```bash
# The test step "Given the Roundup tracker is running" automatically
# starts the server, but you can verify manually:
curl http://localhost:9080/pms/
```

### Variable Substitution Not Working

Ensure curly braces are used correctly:

```gherkin
# Correct:
And I note the created issue ID as "my_issue"
Then the issue "{my_issue}" should have status "closed"

# Incorrect (no braces):
Then the issue "my_issue" should have status "closed"
```

### Priority/Status Validation Failures

Issues must have a priority set. Test fixtures automatically set default priority:

```python
# Fixtures create issues with priority=3 (urgent) by default
# This prevents "Required issue property priority not supplied" errors
```

### API PATCH Operations Failing

The API requires If-Match headers:

```python
# Step definitions automatically:
# 1. GET the issue to retrieve ETag
# 2. Include ETag in If-Match header for PATCH
# This is handled automatically by the test framework
```

## Best Practices

### 1. Use Appropriate Tags

```gherkin
@four-interface  # All four-interface tests
@web-ui          # Web UI specific
@cli             # CLI specific
@api             # API specific
@email           # Email specific
@smoke           # Critical smoke tests
@integration     # Cross-interface workflows
```

### 2. Keep Scenarios Focused

Each scenario should test one specific behavior:

```gherkin
# Good: Focused on one operation
Scenario: Create issue via CLI
  When I create an issue via CLI with...
  Then the issue should be created

# Avoid: Testing multiple unrelated operations
Scenario: Create, update, delete via CLI
  When I create an issue via CLI...
  And I update the issue...
  And I delete the issue...
```

### 3. Use Background for Common Setup

```gherkin
Feature: Four-Interface BDD Testing
  Background:
    Given the Roundup tracker is running
    And the admin user exists with email "roundup-admin@localhost"

  Scenario: Create issue via Web UI
    # Background runs automatically before this
```

### 4. Verify Across Interfaces

When testing one interface, verify results via another:

```gherkin
Scenario: Email creates issue visible in Web UI
  Given I compose an email with...
  When I send the email to the mail gateway
  Then a new issue should be created
  # Cross-interface verification:
  And I am logged in as "admin" with password "admin"
  And I navigate to the issues list
  And I should see "Email Issue" on the page
```

## Test Architecture

### Server Management

- Tests use `clean_database` fixture for isolation
- Each scenario gets a fresh database
- Server starts on-demand when needed
- Proper cleanup between scenarios

### Browser Context

- Web UI scenarios use Playwright
- Browser context created on-demand
- Cross-interface scenarios can dynamically add browser
- Screenshots captured on failures

### Test Isolation

- Each scenario is independent
- Database reset between scenarios
- No shared state except via explicit variables
- Server restart ensures clean state

## Performance

### Parallel Execution

```bash
# Run scenarios in parallel (faster)
behave --processes 4 features/issue_tracking/four_interface_testing.feature
```

### Smoke Test Efficiency

Run only critical paths for quick validation:

```bash
# 4 scenarios, ~15 seconds
behave --tags=@smoke features/issue_tracking/four_interface_testing.feature
```

## Related Documentation

- [BDD Testing Best Practices](../reference/bdd-testing-best-practices.md)
- [Email Gateway How-To](use-email-gateway.md)
- [Roundup Development Practices](../reference/roundup-development-practices.md)
- [Four-Interface Testing Feature](../../features/issue_tracking/four_interface_testing.feature)

## Summary

Four-interface testing ensures consistent behavior across all system interfaces:

✅ **15/15 scenarios passing (100%)**
✅ **All interfaces validated**: Web UI, CLI, API, Email
✅ **Cross-interface workflows** tested
✅ **Variable substitution** for dynamic data
✅ **Automatic server management**
✅ **Complete test isolation**

This testing architecture provides confidence that users will experience consistent behavior regardless of which interface they choose.
