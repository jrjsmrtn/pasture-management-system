______________________________________________________________________

## marp: true theme: default paginate: true header: 'BDD Testing in Practice' footer: 'Pasture Management System | 2025'

<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# BDD Testing in Practice

**Behavior-Driven Development with Gherkin, Behave, and Playwright**

A demonstration from the Pasture Management System project

______________________________________________________________________

## What is BDD?

**Behavior-Driven Development** (BDD) is a software development approach that:

- 📝 Describes expected behavior in natural language
- 🤝 Bridges communication between technical and non-technical stakeholders
- ✅ Creates executable specifications that serve as tests
- 📚 Generates living documentation from test scenarios

**Key Insight**: Tests are specifications, specifications are tests

______________________________________________________________________

## The BDD Stack in PMS

```
┌─────────────────────────────────────┐
│  Gherkin Feature Files              │  ← Scenarios in natural language
│  (Given/When/Then)                  │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│  Behave (Python)                    │  ← BDD test framework
│  - Parses Gherkin                   │
│  - Executes step definitions        │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│  Step Definitions (Python)          │  ← Implementation layer
│  - Web UI: Playwright               │
│  - CLI: subprocess                  │
│  - API: requests/httpx              │
└─────────────────────────────────────┘
```

______________________________________________________________________

## Why BDD for PMS?

**Dual Objectives**:

1. **Functional Tool**: ITIL-inspired issue/change/CMDB management system
1. **BDD Demonstration**: Show Python developers the value of BDD testing

**Perfect Match**:

- Complex workflows (issue tracking, change management)
- Multiple interfaces (Web UI, CLI, API)
- Real-world business logic
- Need for comprehensive documentation

______________________________________________________________________

## Gherkin: The Language of BDD

**Gherkin** is a domain-specific language for describing software behavior:

```gherkin
Feature: Change Approval Workflow
  As a homelab sysadmin
  I want changes to go through approval stages
  So that I can prevent unauthorized or risky changes

  @story-1 @web-ui @smoke
  Scenario: Approve change request
    Given a change exists with status "Planning"
    When I view the change details
    And I click "Start Assessment"
    Then the change status should be "Assessment"
    When I add assessment notes "Risk: Low, Impact: Minimal"
    And I click "Approve"
    Then the change status should be "Approved"
    And I should see "Change approved successfully"
```

______________________________________________________________________

## Gherkin Syntax Breakdown

```gherkin
Feature: [Feature name]
  [Feature description and user story]

  @tag1 @tag2
  Scenario: [Scenario name]
    Given [precondition/context]
    When [action/event]
    Then [expected outcome]
    And [additional step]
    But [contrasting step]
```

**Benefits**:

- ✅ Readable by non-technical stakeholders
- ✅ Structured and unambiguous
- ✅ Executable as tests
- ✅ Serves as documentation

______________________________________________________________________

## Step Definitions: The Implementation

Gherkin steps map to Python functions:

```python
@given('a change exists with status "{status}"')
def step_change_exists_with_status(context, status):
    """Create a change with the specified status."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")

    # Create change via Roundup CLI
    cmd = [
        "roundup-admin", "-i", tracker_dir, "create", "change",
        "title=Test Change",
        "description=Test Description",
        f"status={status}"
    ]

    result = subprocess.run(cmd, capture_output=True,
                          text=True, timeout=10, check=True)

    # Store change ID for later steps
    context.created_change_id = result.stdout.strip()
```

______________________________________________________________________

## Three Interfaces, One Specification

BDD scenarios test **all three interfaces** from **one specification**:

```gherkin
@story-4 @web-ui
Scenario: Schedule approved change via Web UI
  Given a change exists with title "Database upgrade" and status "approved"
  When I view the change details
  And I fill in scheduling information:
    | Field          | Value      |
    | Scheduled Date | 2025-12-01 |
    | Start Time     | 02:00      |
  And I click "Submit"
  Then the change should have scheduled times

@story-4 @cli
Scenario: Schedule change via CLI
  Given a change exists with ID "1" and status "approved"
  When I run "roundup-admin set change1 scheduled_start='2025-12-01.02:00:00'"
  Then the command should succeed

@story-4 @api
Scenario: Schedule change via API
  Given a change exists with ID "1" and status "approved"
  When I PATCH "/api/changes/1/schedule" with JSON:
    """
    {"scheduled_start": "2025-12-01T02:00:00Z"}
    """
  Then the response status should be 200
```

______________________________________________________________________

## Web UI Testing with Playwright

**Playwright** provides browser automation for Web UI scenarios:

```python
@when("I view the change details")
def step_view_change_details(context):
    """Navigate to change details page."""
    change_id = context.created_change_id
    url = f"http://localhost:8080/pms/change{change_id}"
    context.page.goto(url)
    context.page.wait_for_load_state("networkidle")

@when('I fill in scheduling information:')
def step_fill_in_scheduling(context):
    """Fill in scheduling fields from a table."""
    for row in context.table:
        field = row["Field"]
        value = row["Value"]

        if field == "Scheduled Date":
            context.page.fill('input[name="scheduled_date"]', value)
        elif field == "Start Time":
            context.page.fill('input[name="start_time"]', value)
```

______________________________________________________________________

## Playwright Features in PMS

**Capabilities**:

- 🌐 Multi-browser support (Chromium, Firefox, WebKit)
- 📸 Automatic screenshots on failure
- ⏱️ Smart waiting for elements
- 🔍 Powerful selectors (CSS, text, accessibility)

**Configuration**:

```python
# environment.py
def before_all(context):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    context.page = browser.new_page(viewport={"width": 1024, "height": 768})

def after_scenario(context, scenario):
    if scenario.status == "failed":
        screenshot_path = f"screenshots/{scenario.name}.png"
        context.page.screenshot(path=screenshot_path)
```

______________________________________________________________________

## CLI Testing with subprocess

**CLI scenarios** execute commands and verify output:

```python
@when('I run "{command}"')
def step_run_cli_command(context, command):
    """Execute a CLI command."""
    # Parse command string into list
    cmd_parts = shlex.split(command)

    # Execute via subprocess
    result = subprocess.run(
        cmd_parts,
        capture_output=True,
        text=True,
        timeout=30
    )

    # Store for verification
    context.cli_result = result
    context.cli_output = result.stdout
    context.cli_error = result.stderr

@then("the command should succeed")
def step_command_should_succeed(context):
    """Verify command succeeded."""
    assert context.cli_result.returncode == 0, \
        f"Command failed: {context.cli_error}"
```

______________________________________________________________________

## API Testing with httpx

**API scenarios** test REST endpoints:

```python
@when('I PATCH "{endpoint}" with JSON:')
def step_patch_with_json(context, endpoint):
    """Send PATCH request with JSON body."""
    import httpx
    from requests.auth import HTTPBasicAuth

    base_url = "http://localhost:8080/pms"
    url = f"{base_url}{endpoint}"

    # Parse JSON from multiline text
    json_data = json.loads(context.text)

    # Send authenticated request
    response = httpx.patch(
        url,
        json=json_data,
        auth=HTTPBasicAuth("admin", "admin")
    )

    context.api_response = response

@then("the response status should be {status_code:d}")
def step_verify_response_status(context, status_code):
    """Verify HTTP response status code."""
    actual = context.api_response.status_code
    assert actual == status_code, \
        f"Expected {status_code}, got {actual}"
```

______________________________________________________________________

## Scenario Tags and Organization

**Tags** organize and filter scenarios:

```gherkin
@story-1 @web-ui @smoke
Scenario: Approve change request via Web UI
  # Critical path, run on every commit

@story-1 @cli @regression
Scenario: Approve change via CLI
  # Full regression suite, run before release

@story-1 @api @integration
Scenario: Approve change via API
  # Integration tests, run in CI/CD
```

**Execution**:

```bash
behave --tags=@smoke              # Smoke tests only
behave --tags=@web-ui             # All Web UI tests
behave --tags="@story-1 and @cli" # Story 1 CLI tests
behave --tags="not @slow"         # Exclude slow tests
```

______________________________________________________________________

## Real-World Example: Change Risk Assessment

**Feature File** (`features/change_mgmt/change_risk.feature`):

```gherkin
@story-3 @web-ui @smoke
Scenario: Add risk assessment to change
  Given a change exists with title "Upgrade PostgreSQL" and status "planning"
  When I view the change details
  And I fill in the risk assessment:
    | Field  | Value                                                |
    | Impact | Service downtime 1-2 hours during upgrade            |
    | Risk   | Database migration may fail on large datasets        |
  And I click "Submit"
  Then the change should have risk assessment saved
  And I should see the impact "Service downtime 1-2 hours during upgrade"
  And I should see the risk "Database migration may fail on large datasets"
```

______________________________________________________________________

## Step Definitions: Risk Assessment

```python
@when("I fill in the risk assessment:")
def step_fill_in_risk_assessment(context):
    """Fill in risk assessment fields from a table."""
    for row in context.table:
        field = row["Field"]
        value = row["Value"]

        if field == "Impact":
            context.page.fill('textarea[name="impact"]', value)
            context.impact_text = value
        elif field == "Risk":
            context.page.fill('textarea[name="risk"]', value)
            context.risk_text = value

@then("the change should have risk assessment saved")
def step_verify_risk_assessment_saved(context):
    """Verify risk assessment was persisted."""
    tracker_dir = getattr(context, "tracker_dir", "tracker")
    change_id = context.created_change_id

    # Verify via CLI
    cmd = ["roundup-admin", "-i", tracker_dir, "get",
           f"change{change_id}", "impact", "risk"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    output = result.stdout
    assert "Service downtime" in output, "Impact not saved"
    assert "Database migration" in output, "Risk not saved"
```

______________________________________________________________________

## Table-Driven Scenarios

**Data tables** make scenarios concise and reusable:

```gherkin
Scenario Outline: Schedule changes for different maintenance windows
  Given a change exists with title "<change_title>" and status "approved"
  When I schedule the change for "<start_time>" to "<end_time>"
  Then the change should be scheduled for "<start_time>" to "<end_time>"

  Examples:
    | change_title      | start_time        | end_time          |
    | Database upgrade  | 2025-12-01 02:00  | 2025-12-01 04:00  |
    | Firewall update   | 2025-12-08 03:00  | 2025-12-08 03:30  |
    | Server migration  | 2025-12-15 01:00  | 2025-12-15 06:00  |
```

**Result**: One scenario specification generates **three test executions**

______________________________________________________________________

## Background: Shared Context

**Background** runs before every scenario in a feature:

```gherkin
Feature: Change Implementation Tracking

  Background:
    Given the Pasture Management System is running
    And I am logged in as an administrator
    And the following changes exist:
      | title             | status      | scheduled_start    |
      | Database upgrade  | scheduled   | 2025-12-01 02:00   |
      | Network update    | implementing| 2025-11-20 03:00   |

  Scenario: Begin implementation
    When I view change "Database upgrade" details
    And I click "Start Implementation"
    Then the change status should be "implementing"

  Scenario: Complete implementation
    When I view change "Network update" details
    And I click "Mark Complete"
    Then the change status should be "completed"
```

______________________________________________________________________

## Handling Ambiguous Steps

**Problem**: Multiple step definitions match same pattern

```python
# change_workflow_steps.py
@when('I click "{button_text}"')
def step_click_button(context, button_text):
    context.page.click(f'button:has-text("{button_text}")')

# change_risk_steps.py
@when('I click "{button_text}"')  # DUPLICATE!
def step_click_button_risk(context, button_text):
    context.page.click(f'button:has-text("{button_text}")')
```

**Error**:

```
behave.step_registry.AmbiguousStep: @when('I click "Submit"') has already been defined
```

______________________________________________________________________

## Solution: Centralize Common Steps

**Best Practice**: Keep generic steps in shared modules

```python
# features/steps/common_steps.py
@when('I click "{button_text}"')
def step_click_button(context, button_text):
    """Click a button by text (supports multiple selectors)."""
    try:
        context.page.click(f'button:has-text("{button_text}")')
    except:
        context.page.click(f'input[type="submit"][value="{button_text}"]')

# features/steps/change_risk_steps.py
# Note: Step definition for 'I click "{text}"' is in common_steps.py
# to avoid duplication and support multiple selector types
```

**Validation**: Add pre-push hook

```bash
behave --dry-run 2>&1 | grep -q "AmbiguousStep" && exit 1
```

______________________________________________________________________

## Test Reports and CI/CD

**Generate JUnit XML** for CI integration:

```bash
behave --junit --junit-directory reports/
```

**Result**:

```xml
<testsuites>
  <testsuite name="change_mgmt.change_workflow" tests="5" failures="0">
    <testcase classname="change_workflow"
              name="Approve change request" time="2.34">
    </testcase>
    <testcase classname="change_workflow"
              name="Reject change with reason" time="1.89">
    </testcase>
  </testsuite>
</testsuites>
```

**CI Integration**: GitHub Actions, GitLab CI, Jenkins all support JUnit XML

______________________________________________________________________

## Pre-commit Hooks for BDD

**Catch issues before pushing**:

```yaml
# .pre-commit-config.yaml
- id: behave-tests
  name: BDD step definition validation
  entry: bash -c 'output=$(uv run behave features/ --dry-run --no-capture 2>&1);
                  echo "$output";
                  if echo "$output" | grep -q "AmbiguousStep"; then
                    exit 1;
                  fi'
  language: system
  pass_filenames: false
  stages: [pre-push]
```

**Benefits**:

- ✅ Catches ambiguous steps before CI
- ✅ Allows undefined steps (for incremental development)
- ✅ Fast feedback loop

______________________________________________________________________

## BDD as Living Documentation

**Scenarios ARE the documentation**:

```gherkin
Feature: Change Approval Workflow

  As a homelab sysadmin
  I want changes to go through approval stages
  So that I can prevent unauthorized or risky changes

  Scenario: Standard approval path
    Given a change exists in "Planning" status
    When I start assessment
    And I document risk and impact
    And I approve the change
    Then the change moves to "Approved" status
    And approval is recorded in history
```

**Generated from this**:

- ✅ Automated tests
- ✅ User documentation
- ✅ API examples
- ✅ Workflow diagrams

______________________________________________________________________

## Documentation Generation

**From BDD features to tutorials**:

```
features/change_mgmt/
├── change_workflow.feature      → Tutorial: Change Approval Process
├── change_risk.feature          → How-to: Assess Change Risk
├── change_scheduling.feature    → How-to: Schedule Changes
└── change_implementation.feature → How-to: Track Implementation
```

**Process**:

1. Write BDD scenarios for user story
1. Implement step definitions
1. Extract scenarios into tutorial
1. Add explanatory text
1. Publish as Diátaxis documentation

**Result**: Documentation that's **guaranteed to work** because it's tested

______________________________________________________________________

## Sprint 3 BDD Metrics

**Stories Implemented with BDD**:

- Story 1: Change Approval Workflow (8 points) - 11 scenarios
- Story 2: Link Changes to Issues (5 points) - 8 scenarios
- Story 3: Change Risk Assessment (5 points) - 9 scenarios
- Story 4: Change Scheduling (5 points) - 10 scenarios
- Story 5: Change Implementation Tracking (5 points) - 14 scenarios

**Total**: 52 BDD scenarios covering 28 story points

**Coverage**: Web UI (22), CLI (15), API (15)

**Lines of Code**: ~1,500 lines of step definitions

______________________________________________________________________

## Benefits Realized

**For Developers**:

- ✅ Clear specifications before coding
- ✅ Executable acceptance criteria
- ✅ Regression safety net
- ✅ Interface consistency verification

**For Stakeholders**:

- ✅ Readable test reports
- ✅ Living documentation
- ✅ Confidence in quality

**For Project**:

- ✅ 52 automated scenarios
- ✅ 3 interfaces tested from one spec
- ✅ Documentation guaranteed to work
- ✅ Comprehensive regression suite

______________________________________________________________________

## Common Pitfalls and Solutions

**Pitfall 1: Too technical Gherkin**

```gherkin
❌ When I POST /api/change with JSON payload {"status": "2"}
✅ When I start assessment for the change
```

**Pitfall 2: Duplicate step definitions**

```python
# Use pre-push hook to catch
behave --dry-run | grep "AmbiguousStep"
```

**Pitfall 3: Brittle selectors**

```python
❌ context.page.click("#submit_btn_id_12345")
✅ context.page.click('button:has-text("Submit")')
```

**Pitfall 4: Insufficient wait conditions**

```python
❌ context.page.click("button")
✅ context.page.click("button")
   context.page.wait_for_load_state("networkidle")
```

______________________________________________________________________

## Best Practices from PMS

**1. Tag Everything**

- `@story-N` - Link to user story
- `@web-ui`, `@cli`, `@api` - Interface type
- `@smoke`, `@regression` - Test suite
- `@wip` - Work in progress

**2. Use Scenario Outlines for Data Variation**

- Test multiple data combinations
- Avoid scenario duplication

**3. Keep Steps Generic and Reusable**

- Common steps in shared modules
- Specific steps in feature-related files

**4. Document Step Purpose**

- Docstrings explain what step does
- Comments explain why (if non-obvious)

______________________________________________________________________

## Best Practices (continued)

**5. Store Context Carefully**

```python
# ✅ Good: Store for later use
context.created_change_id = result.stdout.strip()

# ❌ Bad: Rely on global state
GLOBAL_CHANGE_ID = result.stdout.strip()
```

**6. Clean Up Resources**

```python
def after_scenario(context, scenario):
    """Clean up test data after each scenario."""
    if hasattr(context, "created_change_id"):
        cmd = ["roundup-admin", "-i", tracker_dir,
               "retire", f"change{context.created_change_id}"]
        subprocess.run(cmd, capture_output=True)
```

**7. Meaningful Assertions**

```python
❌ assert result == True
✅ assert result == True, f"Expected change status 'approved', got '{actual_status}'"
```

______________________________________________________________________

## Integration with Development Workflow

```
┌─────────────────────────────────────────────────┐
│  Sprint Planning                                │
│  - Define user stories                          │
│  - Write acceptance criteria                    │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  Write BDD Scenarios (Gherkin)                  │
│  - Translate acceptance criteria to scenarios   │
│  - Tag and organize features                    │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  Implement Step Definitions                     │
│  - Initially: raise NotImplementedError         │
│  - Run behave → All scenarios fail              │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  TDD Implementation                             │
│  - Write unit tests (pytest)                    │
│  - Implement features                           │
│  - Implement step definitions                   │
│  - Run behave → Scenarios pass                  │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│  Generate Documentation                         │
│  - Extract scenarios into tutorials             │
│  - Add explanatory text                         │
│  - Publish as Diátaxis docs                     │
└─────────────────────────────────────────────────┘
```

______________________________________________________________________

## Lessons Learned

**What Worked Well**:

- ✅ BDD scenarios caught interface inconsistencies early
- ✅ Documentation generated from tests stays accurate
- ✅ Non-technical stakeholders can read scenarios
- ✅ Regression suite built naturally during development

**What Was Challenging**:

- ⚠️ Initial learning curve for Gherkin best practices
- ⚠️ Managing step definition organization across features
- ⚠️ Balancing specificity vs. reusability in steps

**What We'd Do Differently**:

- 📝 Establish step organization guidelines earlier
- 📝 Set up ambiguous step detection from day one
- 📝 Create step definition templates for common patterns

______________________________________________________________________

## Tools and Technologies

**Core BDD Stack**:

- **Behave** - Python BDD framework (Gherkin parser)
- **Gherkin** - Structured natural language for scenarios

**Testing Interfaces**:

- **Playwright** - Web UI automation and testing
- **subprocess** - CLI command execution and validation
- **httpx/requests** - HTTP API testing

**Quality Tools**:

- **ruff** - Python linting and formatting
- **mypy** - Type checking
- **pre-commit** - Git hooks for validation

**Documentation**:

- **Diátaxis** - Documentation framework
- **Marpit** - Markdown presentations

______________________________________________________________________

## Resources for Learning BDD

**Official Documentation**:

- Behave: https://behave.readthedocs.io/
- Playwright: https://playwright.dev/python/
- Gherkin Reference: https://cucumber.io/docs/gherkin/

**Books**:

- "The Cucumber Book" - Matt Wynne, Aslak Hellesøy
- "BDD in Action" - John Ferguson Smart
- "Specification by Example" - Gojko Adzic

**Community**:

- r/BehaviorDrivenDev
- Behave GitHub Discussions
- Playwright Discord

______________________________________________________________________

## PMS Project Resources

**Repository**: https://github.com/jrjsmrtn/pasture-management-system

**Documentation**:

- `/docs/tutorials/` - Learning-oriented guides
- `/docs/howto/` - Task-oriented solutions
- `/docs/reference/` - Technical specifications
- `/docs/explanation/` - Conceptual understanding

**BDD Features**:

- `/features/change_mgmt/` - Change management scenarios
- `/features/issue_tracking/` - Issue tracking scenarios
- `/features/steps/` - Step definitions

**Try it yourself**: Clone the repo and run `behave --tags=@smoke`

______________________________________________________________________

## Key Takeaways

**1. BDD bridges the gap** between business requirements and technical implementation

**2. Gherkin scenarios serve as**:

- Executable specifications
- Automated tests
- Living documentation

**3. Test all interfaces** (Web UI, CLI, API) from one specification

**4. Organization matters**: Tag scenarios, centralize common steps, detect ambiguities early

**5. BDD complements TDD**: Scenarios define "what", unit tests verify "how"

**6. Documentation from tests** stays accurate because it's executable

______________________________________________________________________

## Conclusion

**BDD in PMS demonstrates**:

- ✅ Real-world application of BDD principles
- ✅ Multi-interface testing from single specs
- ✅ Living documentation generation
- ✅ Professional software practices for homelabs

**Start small**:

1. Pick one feature
1. Write 3-5 scenarios in Gherkin
1. Implement step definitions
1. Run `behave`
1. Generate documentation

**The investment pays off**:

- Fewer bugs
- Better documentation
- Clearer requirements
- Confidence in changes

______________________________________________________________________

## Thank You!

**Questions?**

**Pasture Management System**

- Repository: https://github.com/jrjsmrtn/pasture-management-system
- Documentation: `/docs/`
- BDD Features: `/features/`

**Contact**:

- Email: jrjsmrtn@gmail.com
- GitHub: @jrjsmrtn

**Try BDD yourself**: Start with one feature, write scenarios, implement steps, run tests!

______________________________________________________________________

## Bonus: Live Demo Structure

**Demo 1: Write a Simple Scenario** (5 min)

```gherkin
Feature: Simple Demo
  Scenario: Create an issue
    Given I am logged in as "admin"
    When I create an issue with title "Test Issue"
    Then I should see the issue in the issue list
```

**Demo 2: Implement Step Definitions** (10 min)

- Show Web UI step with Playwright
- Show CLI step with subprocess
- Run `behave` and watch it pass

**Demo 3: Generate Documentation** (5 min)

- Extract scenario into how-to guide
- Show it matches actual behavior

**Total**: 20 minutes + Q&A

______________________________________________________________________

## Appendix: Complete Example

See the full change approval workflow implementation:

- **Feature**: `features/change_mgmt/change_workflow.feature`
- **Steps**: `features/steps/change_workflow_steps.py`
- **Tutorial**: `docs/tutorials/managing-changes-homelab.md`

**From scenario to documentation in 3 steps**:

1. Write Gherkin scenario
1. Implement step definitions
1. Extract into tutorial with explanations

**Result**: Documentation that's guaranteed to work!
