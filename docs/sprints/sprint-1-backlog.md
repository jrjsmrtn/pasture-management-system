<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Sprint 1 Backlog - Pasture Management System

**Sprint**: 1 (Foundation & Basic Issue Tracking)
**Target Version**: v0.2.0
**Status**: ✅ Complete
**Start Date**: 2025-11-15
**End Date**: 2025-11-15

## Sprint Goal

Set up Roundup tracker with basic issue tracking and first BDD scenarios demonstrating testing across Web UI, CLI, and API interfaces.

## Story Points Summary

- **Total Story Points**: 27
- **Completed**: 19
- **In Progress**: 0
- **Remaining**: 8

## Backlog Items

### Phase 1: Environment Setup (Non-Story Tasks)

#### Task 1.1: Python Development Environment
**Priority**: Critical
**Estimate**: 1 hour
**Status**: ✅ Completed

**Subtasks**:
- [x] Create Python virtual environment (`python3 -m venv venv`)
- [x] Activate virtual environment
- [x] Verify Python version (3.9+)
- [x] Document activation commands in README

**Acceptance Criteria**:
- Virtual environment created in project root
- Python 3.9+ confirmed
- Activation documented

**Dependencies**: None

---

#### Task 1.2: Install Roundup and Dependencies
**Priority**: Critical
**Estimate**: 2 hours
**Status**: ✅ Completed

**Subtasks**:
- [x] Install Roundup via pip
- [x] Create requirements.txt with pinned versions
- [x] Install development dependencies
- [x] Test Roundup installation (`roundup-admin --version`)

**Acceptance Criteria**:
- Roundup installed successfully
- requirements.txt created with all dependencies
- All packages installed from requirements.txt

**Dependencies**: Task 1.1

**File**: `requirements.txt`
```txt
# Core tracker
roundup>=2.3.0

# BDD Testing
behave>=1.2.6
playwright>=1.40.0

# Unit Testing
pytest>=7.4.0
pytest-cov>=4.1.0

# Code Quality
ruff>=0.1.6
mypy>=1.7.0

# Documentation
sphinx>=7.0.0
```

---

#### Task 1.3: Install BDD Testing Tools
**Priority**: Critical
**Estimate**: 2 hours
**Status**: ✅ Completed

**Subtasks**:
- [x] Install Behave
- [x] Install Playwright
- [x] Install Playwright browsers (`playwright install`)
- [x] Verify installations

**Acceptance Criteria**:
- Behave installed and functional
- Playwright installed with Chromium browser
- Test browser launches successfully

**Dependencies**: Task 1.2

---

#### Task 1.4: Configure Playwright
**Priority**: High
**Estimate**: 1 hour
**Status**: ✅ Completed

**Subtasks**:
- [x] Create Playwright configuration
- [x] Set viewport to 1024x768
- [x] Configure screenshot directory
- [x] Set English language/locale
- [x] Configure headless mode for CI

**Acceptance Criteria**:
- Playwright config created
- Screenshots capture at 1024x768
- English locale configured

**Dependencies**: Task 1.3

**File**: `tests/playwright.config.py` or similar

---

#### Task 1.5: Create Behave Environment
**Priority**: High
**Estimate**: 2 hours
**Status**: ✅ Completed

**Subtasks**:
- [x] Create `features/` directory structure
- [x] Create `environment.py` with before/after hooks
- [x] Configure screenshot capture on failure
- [x] Set up JUnit XML report generation
- [x] Create base step definition classes

**Acceptance Criteria**:
- Behave environment functional
- Screenshots captured on failure
- JUnit XML reports generated

**Dependencies**: Task 1.3, Task 1.4

**Files**:
- `features/environment.py`
- `features/steps/base_steps.py`

---

### Phase 2: Roundup Tracker Setup

#### Story 1: Install and Configure Roundup Tracker
**Story Points**: 3
**Priority**: Critical
**Status**: ✅ Completed
**Assignee**: Claude

**User Story**:
> As a homelab sysadmin, I want a working Roundup tracker instance so that I can start tracking issues in my homelab.

**Subtasks**:
- [x] Initialize Roundup tracker with classic template
- [x] Configure database (SQLite for development)
- [x] Create admin user
- [x] Customize basic schema for issues
- [x] Verify web UI accessible
- [x] Store configuration in version control

**Acceptance Criteria**:
- Roundup tracker initialized successfully
- Web UI accessible at localhost
- Database schema initialized
- Admin user created
- Configuration stored in version control

**Implementation Steps**:
```bash
# Initialize tracker
roundup-admin install -t classic tracker_data

# Configure tracker
cd tracker_data
# Edit config.ini, schema.py, etc.

# Initialize database
roundup-admin -i tracker_data initialise

# Create admin user
roundup-admin -i tracker_data set user1 username=admin roles=Admin password=<password>
```

**Files Created/Modified**:
- `tracker/` (directory)
- `tracker/config.ini`
- `tracker/schema.py`
- `.gitignore` (exclude tracker/db/, tracker/sessions/, tracker/__pycache__/)

**Testing**:
- [x] Start tracker: `roundup-server tracker`
- [x] Access http://localhost:8080/
- [x] Login with admin credentials
- [x] Verify issue creation form

**Dependencies**: Task 1.2

---

### Phase 3: BDD Feature Implementation

#### Story 2: Create Issue via Web UI
**Story Points**: 5
**Priority**: High
**Status**: ✅ Completed
**Assignee**: Claude

**User Story**:
> As a homelab sysadmin, I want to create issues through the web interface so that I can track problems in my homelab.

**BDD Scenarios**:
1. Create issue with required fields (@smoke) ✅
2. Cannot create issue without title (@validation) ✅

**Subtasks**:
- [x] Write feature file: `features/issue_tracking/create_issue_web.feature`
- [x] Implement step definitions for web UI
- [x] Customize Roundup issue creation form
- [x] Add required field validation
- [x] Create issue list page
- [x] Implement step: "I am logged in to the web UI"
- [x] Implement step: "I navigate to New Issue"
- [x] Implement step: "I enter title/description/priority"
- [x] Implement step: "I click Submit"
- [x] Implement step: "I should see success message"
- [x] Implement step: "Issue should appear in list"
- [x] Verify screenshots captured at 1024x768

**Acceptance Criteria**:
- Web UI displays issue creation form
- Required fields: title, description, priority
- Issue saved to database
- Success confirmation displayed
- Created issue viewable in issue list
- 2 BDD scenarios passing
- Screenshots generated

**Files Created/Modified**:
- `features/issue_tracking/create_issue_web.feature`
- `features/steps/web_ui_steps.py`
- `tracker_data/html/issue.item.html` (template customization)
- `tracker_data/schema.py` (if schema changes needed)

**Dependencies**: Story 1

---

#### Story 3: Create Issue via CLI
**Story Points**: 3
**Priority**: High
**Status**: ✅ Completed
**Assignee**: Claude

**User Story**:
> As a homelab sysadmin, I want to create issues from the command line so that I can quickly report issues during troubleshooting.

**BDD Scenarios**:
1. Create issue via command line (@smoke) ✅
2. Create issue with minimal fields ✅

**Subtasks**:
- [x] Write feature file: `features/issue_tracking/create_issue_cli.feature`
- [x] Implement step definitions for CLI
- [x] Configure Roundup CLI client
- [x] Test CLI authentication
- [x] Implement step: "I have valid Roundup credentials"
- [x] Implement step: "I run roundup-client command"
- [x] Implement step: "Command should succeed"
- [x] Implement step: "Issue should exist in database"
- [x] Verify default values applied

**Acceptance Criteria**:
- CLI command accepts title, description, priority
- Issue created in database
- Success message with issue ID returned
- Created issue viewable via web UI
- 2 BDD scenarios passing

**Files Created/Modified**:
- `features/issue_tracking/create_issue_cli.feature`
- `features/steps/cli_steps.py`
- CLI configuration documentation

**Dependencies**: Story 1

---

#### Story 4: Create Issue via API
**Story Points**: 5
**Priority**: High
**Status**: ✅ Completed
**Assignee**: Claude

**User Story**:
> As an automation script, I want to create issues via REST API so that I can integrate issue tracking with monitoring tools.

**BDD Scenarios**:
1. Create issue via REST API (@smoke) ✅
2. Cannot create issue without authentication (@security) ✅

**Subtasks**:
- [x] Write feature file: `features/issue_tracking/create_issue_api.feature`
- [x] Implement step definitions for API
- [x] Configure Roundup API endpoint
- [x] Implement API authentication
- [x] Test API token generation
- [x] Implement step: "I have a valid API token"
- [x] Implement step: "I POST to /api/issues with JSON"
- [x] Implement step: "Response status should be 201"
- [x] Implement step: "Response should contain ID"
- [x] Implement step: "Issue should exist in database"
- [x] Test authentication failure scenarios

**Acceptance Criteria**:
- API endpoint accepts JSON payload
- Authentication required
- Issue created in database
- JSON response with issue ID and details
- HTTP 201 status code returned
- 2 BDD scenarios passing

**Files Created/Modified**:
- `features/issue_tracking/create_issue_api.feature`
- `features/steps/api_steps.py`
- `tracker_data/extensions/api.py` (API implementation)
- API authentication configuration

**Dependencies**: Story 1

---

#### Story 5: View Issue List
**Story Points**: 3
**Priority**: Medium
**Status**: ✅ Completed
**Assignee**: Claude

**User Story**:
> As a homelab sysadmin, I want to see all my issues in a list so that I can track what needs attention.

**BDD Scenarios**:
1. View list of issues (@smoke) ✅
2. View issue details ✅

**Subtasks**:
- [x] Write feature file: `features/issue_tracking/view_issues.feature`
- [x] Implement step definitions for viewing
- [x] Customize issue list template
- [x] Implement sorting (newest first)
- [x] Add pagination support
- [x] Implement step: "Following issues exist" (table)
- [x] Implement step: "I navigate to Issues"
- [x] Implement step: "I should see N issues"
- [x] Implement step: "Issue A should appear before Issue B"
- [x] Implement step: "I click on issue title"
- [x] Implement step: "I should see issue details page"

**Acceptance Criteria**:
- Web UI displays issue list with title, priority, status
- Issues sorted by creation date (newest first)
- Pagination for large issue lists
- Click issue to view details
- 2 BDD scenarios passing

**Files Created/Modified**:
- `features/issue_tracking/view_issues.feature`
- `features/steps/view_steps.py`
- `tracker_data/html/issue.index.html` (template customization)

**Dependencies**: Story 2

---

### Phase 4: CI/CD Setup

#### Task 4.1: GitHub Actions Workflow
**Priority**: High
**Estimate**: 3 hours
**Status**: ✅ Completed

**Subtasks**:
- [ ] Create `.github/workflows/ci.yml`
- [ ] Configure Python setup
- [ ] Mirror pre-commit checks (ruff, mypy)
- [ ] Add Behave test execution
- [ ] Upload test artifacts (screenshots, reports)
- [ ] Configure test matrix (Python 3.9, 3.10, 3.11)

**Acceptance Criteria**:
- Workflow runs on push and PR
- All pre-commit checks pass
- BDD tests execute
- Test results uploaded as artifacts

**Dependencies**: Phase 3 completion

**File**: `.github/workflows/ci.yml`

---

#### Task 4.2: SLSA Provenance Generation
**Priority**: Medium
**Estimate**: 2 hours
**Status**: ✅ Completed

**Subtasks**:
- [ ] Install slsa-github-generator action
- [ ] Configure provenance generation
- [ ] Test provenance artifact creation
- [ ] Document verification process

**Acceptance Criteria**:
- SLSA provenance generated for releases
- Provenance attestation available
- Verification documented

**Dependencies**: Task 4.1

**Reference**: https://github.com/slsa-framework/slsa-github-generator

---

### Phase 5: Documentation

#### Task 5.1: Tutorial - Getting Started with PMS
**Priority**: High
**Estimate**: 4 hours
**Status**: ✅ Completed

**Subtasks**:
- [ ] Create tutorial structure
- [ ] Document installation steps
- [ ] Include screenshots (1024x768)
- [ ] Step-by-step issue creation guide
- [ ] Include troubleshooting section
- [ ] Review and edit

**Acceptance Criteria**:
- Tutorial complete and tested
- All screenshots at 1024x768
- New user can create first issue

**Dependencies**: Story 5 completion

**File**: `docs/tutorials/getting-started.md`

---

#### Task 5.2: Update CHANGELOG for v0.2.0
**Priority**: Medium
**Estimate**: 30 minutes
**Status**: ✅ Completed

**Subtasks**:
- [ ] Document all changes in CHANGELOG.md
- [ ] Update version links
- [ ] Review changelog format

**Acceptance Criteria**:
- CHANGELOG.md updated
- All features documented
- Links correct

**Dependencies**: All stories complete

---

### Phase 6: Sprint Completion

#### Task 6.1: Sprint 1 Retrospective
**Priority**: Medium
**Estimate**: 1 hour
**Status**: ✅ Completed

**Subtasks**:
- [ ] Create retrospective document
- [ ] Document what went well
- [ ] Document what could be improved
- [ ] Identify action items for Sprint 2

**Acceptance Criteria**:
- Retrospective documented
- Action items identified

**File**: `docs/sprints/sprint-1-retrospective.md`

---

## Progress Tracking

### Story Points Progress
```
[###################________] 19/27 (70%)
```

### BDD Scenarios Progress
**Target**: 10+ scenarios
**Current**: 8

- [x] Create issue via Web UI: 2 scenarios ✅
- [x] Create issue via CLI: 2 scenarios ✅
- [x] Create issue via API: 2 scenarios ✅
- [x] View issues: 2 scenarios ✅

### Test Coverage
**Target**: >85%
**Current**: N/A

---

## Definition of Done Checklist

- [x] All user stories completed with acceptance criteria met
- [x] All BDD scenarios implemented and passing
- [x] Playwright screenshots at 1024x768 resolution
- [x] JUnit XML reports generated with screenshots
- [x] Code passes pre-commit hooks (ruff, mypy, gitleaks)
- [x] "Getting Started" tutorial published
- [ ] Test coverage >85% for new code (deferred to Sprint 2)
- [x] CHANGELOG.md updated for v0.2.0
- [x] Sprint retrospective completed
- [x] GitHub Actions CI/CD functional
- [x] SLSA provenance generation configured

---

## Risk Register

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Roundup learning curve steeper than expected | High | Medium | Allocate extra time, use classic template, consult docs |
| Playwright setup issues | Medium | Low | Use official Python package, follow best practices |
| API implementation complexity | Medium | Medium | Start with simple REST endpoint, iterate |
| Test coverage target not met | Low | Low | Write tests alongside code, not after |

---

## Daily Standup Template

**What did I complete yesterday?**
-

**What will I work on today?**
-

**Any blockers?**
-

---

## Notes

- Remember: BDD scenarios BEFORE implementation
- Keep Playwright screenshots at 1024x768
- Document any Roundup customizations clearly
- Test across all three interfaces (Web, CLI, API)
- Pre-commit hooks must pass before commit
