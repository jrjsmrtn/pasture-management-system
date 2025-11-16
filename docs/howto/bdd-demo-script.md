<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# BDD Demonstration Script

This script guides you through demonstrating the BDD testing approach used in the Pasture Management System, showcasing how Gherkin scenarios become executable tests.

## Demo Overview

**Duration**: 15-20 minutes
**Audience**: Python developers, BDD practitioners, QA engineers
**Goal**: Show how BDD enables readable, executable specifications across Web UI, CLI, and API

## Pre-Demo Checklist

### Environment Setup

```bash
# 1. Navigate to project
cd ~/Projects/pasture-management-system

# 2. Activate virtual environment
source venv/bin/activate

# 3. Ensure tracker is running
roundup-server -p 8080 tracker &
# Wait 2-3 seconds for server to start

# 4. Verify tracker is accessible
curl -s http://localhost:8080/pms/ > /dev/null && echo "✓ Tracker running"

# 5. Clean terminal
clear

# 6. Set recording mode (if using Playwright video)
export PLAYWRIGHT_VIDEO=on
export HEADLESS=false  # Show browser
export SLOW_MO=300     # Slow down for visibility
```

### iTerm2 Setup

```bash
# Increase font for visibility
# Cmd + Plus (several times) → ~18pt font

# Split panes (optional, for side-by-side)
# Cmd + D → Split vertically
# Left pane: Feature files
# Right pane: Test execution
```

### Browser Setup

- **Open Safari** to http://localhost:8080/pms/
- **Login** as admin/admin
- **Zoom** to 125% for visibility
- **Position** window (right half of screen if using OBS)

## Part 1: Introduction to BDD (2 minutes)

### Opening Statement

```
"I'm going to show you how we use Behavior-Driven Development to test
a homelab management system. What makes BDD powerful is that our tests
are written in plain English using Gherkin syntax, making them readable
by both developers and non-technical stakeholders."
```

### Show Project Structure

```bash
# Display the BDD organization
tree -L 2 features/
```

**Narration**:

```
"Our BDD tests are organized by feature area:
- issue_tracking: Issue management scenarios
- change_mgmt: ITIL change management workflows
- cmdb: Configuration Management Database tests

Each directory contains .feature files written in Gherkin,
and the steps/ directory has the Python code that makes these
scenarios executable."
```

## Part 2: Feature File Walkthrough (3 minutes)

### Show a Simple Feature

```bash
# Display Story 2 feature file
cat features/cmdb/create_ci.feature
```

**Narration**:

```
"Let's look at Story 2: Create Configuration Items.

This feature file has:
1. A clear feature description in plain English
2. Multiple scenarios covering different test cases
3. Each scenario follows the Given-When-Then structure

Notice the tags: @story-2, @cmdb, @web-ui, @smoke
These let us run specific subsets of tests."
```

### Highlight Key Scenario

```gherkin
Scenario: Create server CI
  Given I am logged in to the web UI
  When I navigate to "CMDB"
  And I click "New Configuration Item"
  And I select type "Server"
  And I enter name "db-server-01"
  ...
  Then I should see "Configuration item created successfully"
```

**Narration**:

```
"This scenario is readable by anyone - no programming knowledge needed.
It describes WHAT we're testing, not HOW to test it.
The HOW is in the step definitions we'll see next."
```

## Part 3: Step Definitions (3 minutes)

### Show Step Definition Implementation

```bash
# Show the step definition that implements "I navigate to CMDB"
grep -A 5 'def step_navigate_to_cmdb' features/steps/ci_creation_steps.py
```

**Output**:

```python
@when('I navigate to "CMDB"')
def step_navigate_to_cmdb(context):
    """Navigate to the CMDB page."""
    context.page.goto(f"{context.tracker_url}/ci")
    context.page.wait_for_load_state("networkidle")
```

**Narration**:

```
"Here's the step definition that makes 'I navigate to CMDB' executable.
It uses Playwright to:
1. Navigate to the CI page
2. Wait for the page to fully load

This same step can be reused across many scenarios.
The business logic stays in the feature file, the technical
implementation stays in the step definitions."
```

### Show Reusable Steps

```bash
# Count how many scenarios use the login step
grep -r "I am logged in" features/**/*.feature | wc -l
```

**Narration**:

```
"See how this one step definition is reused across XX scenarios?
That's the power of BDD - write once, use everywhere."
```

## Part 4: Live Test Execution - Web UI (4 minutes)

### Run a Single Scenario

```bash
# Run the smoke test scenario
behave features/cmdb/create_ci.feature:14
```

**Narration** (while test runs):

```
"Watch as Behave:
1. Reads the Gherkin scenario
2. Finds matching step definitions
3. Launches the browser with Playwright
4. Executes each step in sequence
5. Verifies the expected outcomes

Notice the browser automation - clicking buttons, filling forms,
submitting data - all driven by our readable Gherkin."
```

### Successful Output

```
Feature: Create Configuration Items

  Scenario: Create server CI
    Given I am logged in to the web UI            ... passed
    When I navigate to "CMDB"                     ... passed
    And I click "New Configuration Item"          ... passed
    And I select type "Server"                    ... passed
    And I enter name "db-server-01"               ... passed
    ...
    Then I should see "Configuration item created successfully" ... passed

1 feature passed, 0 failed, 0 skipped
1 scenario passed, 0 failed, 0 skipped
12 steps passed, 0 failed, 0 skipped, 0 undefined
```

**Narration**:

```
"All steps passed! Notice the clear, readable output.
If a step fails, Behave shows exactly which step and why.
Let me show you what happens with a failure..."
```

### Demonstrate Failure (Optional)

```bash
# Temporarily modify feature to cause failure
# Change expected text to cause assertion error
behave features/cmdb/create_ci.feature:31
```

**Narration**:

```
"Here's a validation scenario - it should fail if we try to create
a CI without a name. Watch what happens..."

[After failure]

"See how Behave shows:
1. Which step failed
2. The assertion error
3. A screenshot is captured automatically
4. The exact line in the step definition

This makes debugging incredibly fast."
```

## Part 5: Multi-Interface Testing (4 minutes)

### Show Same Feature, Three Interfaces

**Narration**:

```
"One of BDD's strengths is testing the same behavior across different
interfaces. Let me show you how we test CI creation via Web UI, CLI,
and API - all from the same feature file."
```

### Web UI Test

```bash
# Already shown above
behave --tags=@story-2 --tags=@web-ui --tags=@smoke
```

### CLI Test

```bash
# Run CLI scenario
behave features/cmdb/create_ci.feature:120
```

**Scenario**:

```gherkin
@cli
Scenario: Create network device via CLI
  When I run "roundup-admin -i tracker create ci name=core-switch-01 type=2..."
  Then the command should succeed
  And the output should contain "1"
```

**Narration**:

```
"Same feature - creating a CI - but this time via command line.
The step definition executes roundup-admin and verifies the output.
Different interface, same business requirement."
```

### API Test

```bash
# Run API scenario
behave features/cmdb/create_ci.feature:127
```

**Scenario**:

```gherkin
@api
Scenario: Create virtual machine via API
  Given I have a valid API token
  When I POST to "/api/cmdb/ci" with JSON:
    """
    {
      "name": "app-vm-01",
      "type": "6",
      ...
    }
    """
  Then the response status should be 201
```

**Narration**:

```
"And via REST API. Same CI creation logic, validated via HTTP.
This proves our system works correctly regardless of how it's accessed.
That's comprehensive testing with minimal code duplication."
```

## Part 6: Advanced Feature - Relationships (3 minutes)

### Show Complex Scenario

```bash
# Display the relationship feature
cat features/cmdb/ci_relationships.feature | head -30
```

**Highlight Scenario**:

```gherkin
Scenario: Link virtual machine to physical server
  Given a CI exists with name "db-server-01" and type "Server"
  And a CI exists with name "app-vm-01" and type "Virtual Machine"
  When I view CI "app-vm-01"
  And I click "Add Relationship"
  And I select relationship type "Runs On"
  And I select target CI "db-server-01"
  And I click "Save"
  Then "app-vm-01" should have relationship "Runs On" to "db-server-01"
  And "db-server-01" should have relationship "Hosts" to "app-vm-01"
```

**Narration**:

```
"Here's a more complex scenario testing bidirectional relationships.
When a VM 'Runs On' a server, the system automatically creates the
inverse relationship - the server 'Hosts' the VM.

Our BDD test verifies both relationships are created correctly.
This is ITIL best practice, and our Gherkin documents it clearly."
```

### Run the Scenario

```bash
behave features/cmdb/ci_relationships.feature:14
```

**Narration** (while running):

```
"Watch as Behave:
1. Creates the two CIs via CLI
2. Opens the browser
3. Navigates to the VM
4. Creates the relationship
5. Verifies BOTH CIs show the correct relationships

This tests complex business logic with simple, readable steps."
```

## Part 7: Validation Testing (2 minutes)

### Show Circular Dependency Prevention

```bash
# Show the validation scenario
sed -n '34,42p' features/cmdb/ci_relationships.feature
```

**Scenario**:

```gherkin
@validation
Scenario: Prevent circular dependency
  Given a CI "ci-a" depends on "ci-b"
  And a CI "ci-b" depends on "ci-c"
  When I view CI "ci-c"
  And I try to add dependency to "ci-a"
  Then I should see "Circular dependency detected"
  And the relationship should not be created
```

**Narration**:

```
"BDD is perfect for testing edge cases and validations.
This scenario tests that we prevent circular dependencies:
A → B → C → A (which would be invalid).

Our detector catches this and displays an error message.
The Gherkin makes the business rule crystal clear."
```

### Run the Validation

```bash
behave features/cmdb/ci_relationships.feature:36
```

## Part 8: Test Reports (2 minutes)

### Generate JUnit XML Report

```bash
# Run all CMDB tests with reports
behave features/cmdb/ \
  --junit \
  --junit-directory reports/ \
  --format json \
  --outfile reports/cmdb-results.json
```

**Narration**:

```
"Behave can generate reports in multiple formats:
- JUnit XML for CI/CD integration
- JSON for custom reporting
- HTML with plugins

Let me show you the output..."
```

### Show Test Summary

```bash
# Display the results
cat reports/TESTS-*.xml | grep -E 'testcase|failure|error' | head -20
```

**Narration**:

```
"Here's the JUnit XML that Jenkins, GitHub Actions, or any CI system
can consume. Each scenario is a test case with pass/fail status."
```

### Show Coverage Summary

```bash
# Count scenarios by tag
echo "=== Test Coverage Summary ==="
echo "Story 1 (Schema):       $(grep -c '@story-1' features/cmdb/*.feature) scenarios"
echo "Story 2 (Create):       $(grep -c '@story-2' features/cmdb/*.feature) scenarios"
echo "Story 3 (Relationships):$(grep -c '@story-3' features/cmdb/*.feature) scenarios"
echo ""
echo "Web UI tests:   $(grep -c '@web-ui' features/cmdb/*.feature) scenarios"
echo "CLI tests:      $(grep -c '@cli' features/cmdb/*.feature) scenarios"
echo "API tests:      $(grep -c '@api' features/cmdb/*.feature) scenarios"
```

**Narration**:

```
"Our BDD coverage for the CMDB feature:
- XX scenarios total
- XX for Web UI, XX for CLI, XX for API
- Every user story has executable acceptance criteria

This gives stakeholders confidence that requirements are met."
```

## Part 9: The BDD Workflow (1 minute)

### Show the Process

**Narration**:

```
"Our BDD workflow follows these steps:

1. WRITE the feature file first (Gherkin scenarios)
   - This is the specification
   - Written with product owner
   - Defines 'done'

2. RUN the scenarios (they fail - no implementation yet)
   - Behave shows 'undefined steps'
   - This is expected - we're doing TDD

3. IMPLEMENT step definitions
   - One step at a time
   - Watch tests turn green
   - Refactor as needed

4. IMPLEMENT the feature
   - In the application code
   - Tests guide development
   - Green tests mean feature is complete

5. DOCUMENTATION is automatic
   - Feature files are living documentation
   - Always up to date
   - Readable by everyone

This is BDD: Behavior-Driven Development."
```

## Part 10: Q&A Prep (2 minutes)

### Common Questions

**Q: "How long does it take to write BDD tests?"**

A: "Initially longer than unit tests, but you save time because:

- Less debugging (issues caught early)
- Better coverage (all interfaces tested)
- Living documentation (no separate docs needed)
- Fewer regressions (comprehensive test suite)"

**Q: "Can non-developers write Gherkin?"**

A: "Yes! Product owners write scenarios, developers implement steps.
Let me show you..." [Show a feature file]

**Q: "How do you handle flaky tests?"**

A: "Playwright's auto-wait eliminates most flakiness.
For edge cases, we use explicit waits and retries.
Our BDD step validation hook catches ambiguous steps before CI."

**Q: "What's the test execution time?"**

```bash
# Run all CMDB tests with timing
time behave features/cmdb/
```

A: "The full CMDB suite (XX scenarios) runs in ~XX seconds.
We run smoke tests (@smoke tag) on every commit (< 1 min),
full suite on PR, and comprehensive suite nightly."

## Closing Statement

```
"To summarize:

1. BDD makes tests READABLE - anyone can understand requirements
2. BDD makes tests MAINTAINABLE - reusable step definitions
3. BDD makes tests COMPREHENSIVE - same behavior, multiple interfaces
4. BDD makes tests VALUABLE - they're executable specifications

The Pasture Management System uses BDD to demonstrate these benefits
to the Python and QA community. Every feature has Gherkin scenarios,
every scenario has step definitions, and every test is executable.

That's how you do BDD right.

Questions?"
```

## Demo Variations

### Short Demo (5 minutes)

1. Show one feature file (2 min)
1. Run one scenario (2 min)
1. Show step definition (1 min)

### Technical Deep-Dive (30 minutes)

Add:

- Playwright architecture
- Step definition patterns
- CI/CD integration
- Custom reporters
- Performance optimization

### Executive Summary (3 minutes)

Show:

- Feature file only
- Test execution video
- Pass/fail report
- "Living documentation"

## Recording Tips

### For Playwright Video Recording

```bash
# Record everything
export PLAYWRIGHT_VIDEO=on
export HEADLESS=false
export SLOW_MO=500  # Extra slow for demo

# Run the demo script scenarios
behave features/cmdb/create_ci.feature:14
behave features/cmdb/create_ci.feature:120
behave features/cmdb/create_ci.feature:127
behave features/cmdb/ci_relationships.feature:14

# Videos saved to videos/ directory
```

### For OBS Recording

1. **Scene 1**: Feature file (full screen)
1. **Scene 2**: Terminal + Browser (split)
1. **Scene 3**: Test results (terminal full)
1. **Hotkeys**: Switch scenes smoothly
1. **Narration**: Record audio explaining each step

## Post-Demo Resources

Share with audience:

- Feature files: `features/cmdb/`
- Step definitions: `features/steps/`
- Documentation: `docs/tutorials/`, `docs/howto/`
- Video recordings: `videos/sprint4/`
- GitHub: https://github.com/jrjsmrtn/pasture-management-system

## See Also

- [Recording BDD Videos](./record-bdd-videos.md) - Playwright video setup
- [OBS Studio Setup](./record-bdd-demo.md) - Full presentation recording
- [BDD Best Practices](../explanation/bdd-best-practices.md) - Methodology
- [Behave Documentation](https://behave.readthedocs.io/) - Official docs
