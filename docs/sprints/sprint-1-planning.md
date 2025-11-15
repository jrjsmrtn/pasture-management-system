<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Sprint 1 Plan - Pasture Management System

**Sprint Duration**: 2 weeks
**Sprint Goal**: Set up Roundup tracker with basic issue tracking and first BDD scenarios
**Target Version**: v0.2.0
**Start Date**: TBD
**End Date**: TBD

## Sprint Objective

Establish the foundational Roundup tracker instance with basic issue tracking capabilities and demonstrate BDD testing across all three interfaces (Web UI, CLI, API). This sprint creates the working foundation for all future ITIL workflows.

## User Stories

### Epic: Basic Issue Tracking

#### Story 1: Install and Configure Roundup Tracker
**As a** homelab sysadmin
**I want** a working Roundup tracker instance
**So that** I can start tracking issues in my homelab

**Acceptance Criteria**:
- Roundup tracker initializes successfully
- Web UI accessible at localhost
- Database schema initialized
- Admin user created
- Configuration stored in version control

**Story Points**: 3

---

#### Story 2: Create Issue via Web UI
**As a** homelab sysadmin
**I want** to create issues through the web interface
**So that** I can track problems in my homelab

**Acceptance Criteria**:
- Web UI displays issue creation form
- Required fields: title, description, priority
- Issue saved to database
- Success confirmation displayed
- Created issue viewable in issue list

**BDD Scenarios**: (Feature file: `features/issue_tracking/create_issue_web.feature`)
```gherkin
@story-2 @web-ui @smoke
Scenario: Create issue with required fields
  Given I am logged in to the web UI
  When I navigate to "New Issue"
  And I enter title "Database server not responding"
  And I enter description "PostgreSQL service fails to start after reboot"
  And I select priority "High"
  And I click "Submit"
  Then I should see "Issue created successfully"
  And the issue should appear in the issue list

@story-2 @web-ui @validation
Scenario: Cannot create issue without title
  Given I am logged in to the web UI
  When I navigate to "New Issue"
  And I enter description "Some description"
  And I click "Submit"
  Then I should see "Title is required"
  And the issue should not be created
```

**Story Points**: 5

---

#### Story 3: Create Issue via CLI
**As a** homelab sysadmin
**I want** to create issues from the command line
**So that** I can quickly report issues during troubleshooting

**Acceptance Criteria**:
- CLI command accepts title, description, priority
- Issue created in database
- Success message with issue ID returned
- Created issue viewable via web UI

**BDD Scenarios**: (Feature file: `features/issue_tracking/create_issue_cli.feature`)
```gherkin
@story-3 @cli @smoke
Scenario: Create issue via command line
  Given I have valid Roundup credentials
  When I run "roundup-client create issue title='Service down' description='Network service unreachable' priority=high"
  Then the command should succeed
  And I should see "Issue created: #1"
  And the issue should exist in the database

@story-3 @cli
Scenario: Create issue with minimal fields
  Given I have valid Roundup credentials
  When I run "roundup-client create issue title='Quick issue'"
  Then the command should succeed
  And the issue should have default priority "Medium"
```

**Story Points**: 3

---

#### Story 4: Create Issue via API
**As a** automation script
**I want** to create issues via REST API
**So that** I can integrate issue tracking with monitoring tools

**Acceptance Criteria**:
- API endpoint accepts JSON payload
- Authentication required
- Issue created in database
- JSON response with issue ID and details
- HTTP 201 status code returned

**BDD Scenarios**: (Feature file: `features/issue_tracking/create_issue_api.feature`)
```gherkin
@story-4 @api @smoke
Scenario: Create issue via REST API
  Given I have a valid API token
  When I POST to "/api/issues" with JSON:
    """
    {
      "title": "Backup job failed",
      "description": "Nightly backup failed with error code 5",
      "priority": "high"
    }
    """
  Then the response status should be 201
  And the response should contain "id"
  And the issue should exist in the database

@story-4 @api @security
Scenario: Cannot create issue without authentication
  Given I have no API token
  When I POST to "/api/issues" with JSON:
    """
    {
      "title": "Test issue"
    }
    """
  Then the response status should be 401
  And the response should contain "Authentication required"
```

**Story Points**: 5

---

#### Story 5: View Issue List
**As a** homelab sysadmin
**I want** to see all my issues in a list
**So that** I can track what needs attention

**Acceptance Criteria**:
- Web UI displays issue list with title, priority, status
- Issues sorted by creation date (newest first)
- Pagination for large issue lists
- Click issue to view details

**BDD Scenarios**: (Feature file: `features/issue_tracking/view_issues.feature`)
```gherkin
@story-5 @web-ui @smoke
Scenario: View list of issues
  Given the following issues exist:
    | title                  | priority | status |
    | Database server down   | High     | New    |
    | Slow network response  | Medium   | New    |
    | Update certificates    | Low      | New    |
  When I navigate to "Issues"
  Then I should see 3 issues
  And "Database server down" should appear before "Slow network response"

@story-5 @web-ui
Scenario: View issue details
  Given an issue exists with title "Test Issue"
  When I navigate to "Issues"
  And I click on "Test Issue"
  Then I should see the issue details page
  And I should see title "Test Issue"
  And I should see the description
```

**Story Points**: 3

---

## Technical Tasks

### Environment Setup
- [ ] Create Python virtual environment
- [ ] Install Roundup and dependencies
- [ ] Initialize Roundup tracker with classic template
- [ ] Configure tracker schema for basic issues
- [ ] Set up local development database

### BDD Infrastructure
- [ ] Install Behave and dependencies
- [ ] Install Playwright and browsers
- [ ] Configure Playwright for 1024x768 screenshots
- [ ] Create environment.py with setup/teardown hooks
- [ ] Create step definition base classes
- [ ] Configure JUnit XML report generation

### Customization
- [ ] Customize issue schema (priority, status fields)
- [ ] Create basic web UI templates (English only)
- [ ] Configure CLI interface
- [ ] Set up basic REST API endpoints

### Testing
- [ ] Write step definitions for web UI scenarios
- [ ] Write step definitions for CLI scenarios
- [ ] Write step definitions for API scenarios
- [ ] Configure screenshot capture on failures
- [ ] Set up test data fixtures

### Documentation
- [ ] Write "Getting Started" tutorial
- [ ] Document Roundup installation process
- [ ] Create reference docs for issue schema
- [ ] Document BDD test execution

## Definition of Done

- [ ] All user stories completed with acceptance criteria met
- [ ] All BDD scenarios implemented and passing
- [ ] Playwright screenshots at 1024x768 resolution
- [ ] JUnit XML reports generated with screenshots
- [ ] Code passes pre-commit hooks (ruff, mypy, gitleaks)
- [ ] "Getting Started" tutorial published
- [ ] Test coverage >85% for new code
- [ ] CHANGELOG.md updated for v0.2.0
- [ ] Sprint retrospective completed

## Sprint Backlog

| Task | Story Points | Status |
|------|-------------|--------|
| Story 1: Install and Configure Roundup | 3 | Not Started |
| Story 2: Create Issue via Web UI | 5 | Not Started |
| Story 3: Create Issue via CLI | 3 | Not Started |
| Story 4: Create Issue via API | 5 | Not Started |
| Story 5: View Issue List | 3 | Not Started |
| BDD Infrastructure Setup | 5 | Not Started |
| Tutorial: Getting Started | 3 | Not Started |

**Total Story Points**: 27

## Risks and Dependencies

### Risks
- **Roundup Learning Curve**: Team unfamiliar with Roundup customization
  - *Mitigation*: Allocate time for Roundup documentation review, start with classic template
- **Playwright Setup Complexity**: Browser automation can be tricky
  - *Mitigation*: Use official Playwright Python package, follow best practices

### Dependencies
- Python 3.9+ installed
- MacPorts package manager (for macOS)
- Podman available for C4 DSL validation
- Network access for package installation

## Success Metrics

- [ ] Roundup tracker accessible and functional
- [ ] Minimum 10 BDD scenarios passing across all interfaces
- [ ] All web UI screenshots captured at 1024x768
- [ ] Zero security issues from pre-commit hooks
- [ ] Tutorial enables new user to create first issue
- [ ] Sprint goal achieved: working foundation for ITIL workflows
