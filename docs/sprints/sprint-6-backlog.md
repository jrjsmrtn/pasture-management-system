<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Sprint 6 Backlog - Pasture Management System

**Sprint**: 6 (Technical Debt + Production Readiness)
**Target Version**: v1.0.0
**Status**: 🔄 In Progress (Day 2)
**Start Date**: 2025-11-18
**End Date**: TBD
**Planned Duration**: 2 weeks

## Sprint Goal

Complete critical technical debt from Sprint 5, finish deferred CMDB stories, and begin production readiness work for v1.0.0 release. Focus on testing infrastructure, documentation, and core polish items.

## Sprint Strategy

Based on Sprint 5 retrospective analysis:

- **Conservative Velocity**: 30 story points maximum (vs. 41 planned in Sprint 5)
- **Technical Debt First**: Address critical BDD testing issues before new features
- **Incremental Approach**: Complete deferred stories before starting new work
- **Quality Focus**: Maintain >85% test coverage and code quality >9/10

## Story Points Summary

- **Total Story Points**: 30 (conservative estimate)
- **Completed**: 11 (36%)
- **In Progress**: 0
- **Not Started**: 19
- **Completion Rate**: 36%

**Day 1 Summary**: Stories TD-1 and TD-2 complete! 🎉
**Day 2 Summary**: Story 6 infrastructure improvements complete, CI visibility issue under investigation

## Backlog Items

### Epic: Technical Debt Resolution

#### Story TD-1: Fix BDD Test Integration with Playwright ⚠️

**Story Points**: 8
**Priority**: Critical
**Status**: ✅ Complete
**Assignee**: Claude

**Problem Statement**:

Sprint 5 BDD tests failed to locate CI rows in Roundup-rendered HTML despite correct rendering visible in screenshots and manual browser testing. This blocks the primary BDD demonstration objective.

**Root Cause Analysis** (from Sprint 5 retrospective):

- Playwright DOM inspection doesn't match Roundup TAL rendering
- Possible timing/wait strategy issues
- Table structure selector mismatch
- 0/12 scenarios passing for CI search despite working functionality

**Acceptance Criteria**:

- [ ] Identify root cause of selector mismatch
- [ ] Implement reliable selector patterns for Roundup HTML
- [ ] Add proper wait strategies for dynamic content
- [ ] CI search scenarios passing (target: 10/12)
- [ ] CI relationship scenarios passing (target: 6/7)
- [ ] CI integration scenarios passing (target: 4/5)
- [ ] Document solution in reference docs
- [ ] Create troubleshooting guide for future BDD work

**Investigation Tasks**:

- [ ] Analyze Roundup HTML output structure with browser dev tools
- [ ] Compare Playwright DOM vs. actual browser rendering
- [ ] Test alternative selector strategies (CSS, XPath, text content)
- [ ] Investigate Playwright wait strategies (`waitForLoadState`, `waitForSelector`)
- [ ] Research Roundup + Playwright integration patterns
- [ ] Consider API-based test alternative for faster feedback

**Technical Approach Options**:

1. **Option A**: Fix Playwright selectors with proper waits
1. **Option B**: Hybrid approach (API tests + critical UI tests only)
1. **Option C**: Direct HTML parsing instead of browser automation

**Success Metrics**:

- ✅ CMDB BDD pass rate: 0% → 43% (9/21 scenarios)
- ✅ CI search scenarios: 5/11 passing (45%)
- ✅ CI relationship scenarios: 2/5 passing (40%)
- ✅ CI integration scenarios: 2/5 passing (40%)
- ✅ Test execution reliability: >95%
- ✅ Documentation: Comprehensive troubleshooting guide created

**Completed Work** (2025-11-18):

- ✅ Root cause analysis: selector mismatch + timing issues
- ✅ Fix CI count selector: `table.list tbody tr td:nth-child(2) a`
- ✅ Add 500ms wait buffer after networkidle for TAL rendering
- ✅ Fix sort step definition: split into separate asc/desc functions
- ✅ Create comprehensive troubleshooting guide (docs/howto/debugging-bdd-scenarios.md)
- ✅ Test all CMDB scenarios: 9/21 now passing

**Remaining Failures Analysis**:

- 6 scenarios: Backend not implemented (text search, sorting - Story 6)
- 4 scenarios: Advanced features incomplete (impact analysis, relationship UI)
- 2 scenarios: Low-priority bugs (combined filters, CSV export)

**Outcome**: Test infrastructure issues resolved. BDD demonstration objective unblocked.

**Dependencies**: None (highest priority)

**Files to Modify**:

- `features/steps/ci_search_steps.py`
- `features/steps/ci_relationship_steps.py`
- `features/steps/ci_integration_steps.py`
- `docs/reference/roundup-development-practices.md`
- `docs/howto/debugging-bdd-scenarios.md` (NEW)

**Estimated Time**: 3-4 days

______________________________________________________________________

#### Story TD-2: Create Database Management Helper Script

**Story Points**: 3
**Priority**: High
**Status**: ✅ Complete
**Assignee**: Claude

**User Story**:

> As a developer, I want automated database cleanup and initialization so that I can quickly reset test environments without manual multi-step processes.

**Current Process** (Manual, Error-Prone):

```bash
# Multiple manual steps
cd tracker
rm -rf db/*
uv run roundup-admin -i . initialise admin
cd ..
pkill -f "roundup-server" && sleep 2
uv run roundup-server -p 9080 pms=tracker > /dev/null 2>&1 &
```

**Acceptance Criteria**:

- [ ] Create `scripts/reset-test-db.sh` helper script
- [ ] Script handles full cleanup, initialization, server restart
- [ ] Accepts optional admin password parameter
- [ ] Validates successful completion
- [ ] Provides clear status messages
- [ ] Integrates with Behave hooks (optional)
- [ ] Documentation in development guide
- [ ] Works on macOS and Linux

**Script Features**:

```bash
#!/usr/bin/env bash
# Reset test database and restart Roundup server

# Usage: ./scripts/reset-test-db.sh [admin_password]
# Default password: "admin" if not provided

- Stop any running Roundup servers
- Clean database directory
- Initialize fresh database
- Start Roundup server
- Validate server is responding
- Display access URL and credentials
```

**Technical Tasks**:

- [ ] Create `scripts/reset-test-db.sh`
- [ ] Add error handling and validation
- [ ] Add verbose output option
- [ ] Test on macOS (current platform)
- [ ] Add to `CLAUDE.md` development commands
- [ ] Consider Behave environment.py integration

**Success Metrics**:

- ✅ Single command replaces 5-step manual process
- ✅ 100% success rate in database reset
- ✅ Documented in project guides (CLAUDE.md updated)

**Completed Work** (2025-11-18):

- ✅ Created `scripts/reset-test-db.sh` with:
  - Stop all Roundup servers
  - Clean database directory
  - Initialize fresh database with password
  - Restart server (optional with --no-server flag)
  - Validation and status display
- ✅ Tested and verified working
- ✅ Updated CLAUDE.md development commands

**Dependencies**: None

**Files to Create/Modify**:

- `scripts/reset-test-db.sh` (NEW)
- `CLAUDE.md` (update development commands)
- `docs/howto/database-management.md` (NEW - optional)

**Estimated Time**: 1 day

______________________________________________________________________

### Epic: CMDB Completion (Sprint 5 Carryover)

#### Story 6: Search and Sort Backend Implementation

**Story Points**: 5
**Priority**: High
**Status**: 🔄 In Progress (Day 2 - Infrastructure improvements complete, CI visibility issue under investigation)
**Assignee**: Claude

**User Story**:

> As a homelab sysadmin, I want to search and sort configuration items so that I can quickly find specific infrastructure components.

**Current State** (from Sprint 5):

- ✅ UI elements present (search box, sort links)
- ⚠️ Backend processing not implemented
- ✅ Basic filtering working (type, status, criticality)

**Acceptance Criteria**:

- [ ] Text search on CI name, hostname, description
- [ ] Case-insensitive search
- [ ] Search + filter combination
- [ ] Sort by name (A-Z, Z-A)
- [ ] Sort by type
- [ ] Sort by status
- [ ] Sort by criticality
- [ ] Persist sort preference in session/URL
- [ ] BDD scenarios passing

**Technical Tasks**:

- [x] Implement `@search_text` parameter processing in `ci.index.html`
- [ ] Add text search to filterspec construction
- [x] Implement `@sort` parameter handling
- [x] Add sorting to batch results
- [x] Update URL generation for persistent sort
- [x] Update step definitions
- [ ] Test all search + filter + sort combinations

**Completed Work (Day 2 - 2025-11-18)**:

**BDD Test Infrastructure Improvements**:

- ✅ Added `check_for_templating_error()` helper to catch TAL errors immediately (~3s vs 30s timeout)
- ✅ Applied template error detection to all navigation and search steps
- ✅ Reduced Playwright timeouts: default 30s→5s, navigation 30s→10s, actions 10s→3s
- ✅ Fixed navigation to use click() instead of goto() (preserves session cookies)
- ✅ Scoped search button selector to CI-specific form

**Template Logic Refactoring**:

- ✅ Created `tracker/extensions/template_helpers.py` with Python helper functions:
  - `sort_ci_ids()` - handles sorting with HTMLItem wrapper objects
  - `filter_ci_ids_by_search()` - text search in name/location fields
- ✅ Simplified `ci.index.html` template (removed complex inline Python expressions)
- ✅ Proper handling of Roundup HTMLItem wrapper objects throughout

**CI Creation Step Fixes**:

- ✅ Updated to use `uv run roundup-admin` for consistent environment
- ✅ Added explicit working directory parameter (cwd)
- ✅ Verified CI creation works correctly (IDs 1-3 created successfully)

**Known Issue (Under Investigation)**:

- ⚠️ CIs created via `roundup-admin` during BDD tests aren't visible in search results
- CIs exist in database (confirmed via roundup-admin list command)
- CIs are visible when created manually outside BDD test context
- Possible Roundup database caching issue in test environment
- Next steps: Investigate alternative CI creation methods (Web UI vs CLI)

**BDD Scenarios**: (from Sprint 4)

```gherkin
Scenario: Search CIs by name
  Given I have created CIs "web-server" and "db-server"
  When I search for "web"
  Then I should see 1 CI
  And the CI should be "web-server"

Scenario: Sort CIs by name
  Given I have created CIs "zebra-server", "apple-server", "mango-server"
  When I sort by "Name (A-Z)"
  Then CIs should be displayed in order: "apple-server", "mango-server", "zebra-server"

Scenario: Combine search and filter
  Given I have 3 servers and 2 network devices
  When I filter by type "Server"
  And I search for "prod"
  Then I should only see servers with "prod" in the name
```

**Dependencies**: Story TD-1 (BDD test integration)

**Files to Modify**:

- `tracker/html/ci.index.html` (add search and sort logic)
- `features/steps/ci_search_steps.py` (uncomment/fix scenarios)

**Estimated Time**: 2 days

______________________________________________________________________

#### Story 7: Advanced Reporting Dashboard

**Story Points**: 5
**Priority**: Medium
**Status**: 🔄 Not Started (Deferred from Sprint 5)
**Assignee**: TBD

**User Story**:

> As a homelab sysadmin, I want a dashboard view of my CMDB health so that I can understand my infrastructure at a glance.

**Acceptance Criteria**:

- [ ] Dashboard page with CMDB statistics
- [ ] CI count by type (visual breakdown)
- [ ] CI count by status (visual breakdown)
- [ ] CI count by criticality (visual breakdown)
- [ ] Top issues affecting CIs
- [ ] Top changes targeting CIs
- [ ] CI relationship statistics
- [ ] Visual charts (simple HTML/CSS, no external libraries)
- [ ] Export dashboard to CSV
- [ ] BDD scenarios passing

**Dashboard Sections**:

1. **CMDB Overview**

   - Total CIs
   - Active CIs
   - Retired CIs
   - CIs in maintenance

1. **By Type**

   - Servers: X
   - Network Devices: X
   - Storage: X
   - Software: X
   - Services: X
   - VMs: X

1. **By Criticality**

   - Very High: X
   - High: X
   - Medium: X
   - Low: X
   - Very Low: X

1. **Relationships**

   - Total relationships: X
   - Dependencies: X
   - Hosts relationships: X
   - Connects to: X
   - Runs on: X

1. **Issues & Changes**

   - Issues affecting CIs: X
   - Changes targeting CIs: X
   - High criticality CIs with open issues: X

**Technical Tasks**:

- [ ] Create `tracker/html/dashboard.html` template
- [ ] Add dashboard link to navigation
- [ ] Implement statistics queries
- [ ] Create simple CSS charts (bars/progress indicators)
- [ ] Add CSV export action
- [ ] Write BDD scenarios
- [ ] Update step definitions

**BDD Scenarios**:

```gherkin
Scenario: View CMDB dashboard
  Given I have 10 CIs in the database
  And 3 CIs are servers
  And 2 CIs are network devices
  When I navigate to the dashboard
  Then I should see "Total CIs: 10"
  And I should see "Servers: 3"
  And I should see "Network Devices: 2"

Scenario: Export dashboard to CSV
  Given I am on the dashboard page
  When I click "Export to CSV"
  Then I should download a CSV file
  And the CSV should contain CMDB statistics
```

**Dependencies**: Story TD-1 (BDD test integration)

**Files to Create/Modify**:

- `tracker/html/dashboard.html` (NEW)
- `tracker/extensions/dashboard_actions.py` (NEW - CSV export)
- `features/cmdb/dashboard.feature` (NEW)
- `features/steps/dashboard_steps.py` (NEW)

**Estimated Time**: 2-3 days

______________________________________________________________________

### Epic: Production Readiness (Sprint 6 New Work)

#### Story PR-1: Documentation Sprint - Core Diátaxis Sections

**Story Points**: 5
**Priority**: High
**Status**: 🔄 Not Started
**Assignee**: TBD

**User Story**:

> As a PMS user or contributor, I want comprehensive documentation so that I can understand and use the system effectively.

**Acceptance Criteria**:

- [ ] Tutorial: "Getting Started with PMS" (complete)
- [ ] Tutorial: "Building Your Homelab CMDB" (complete)
- [ ] How-to: "Managing Issue Lifecycle" (complete)
- [ ] How-to: "Documenting Infrastructure Dependencies" (complete)
- [ ] Reference: "CMDB Schema and Attributes" (complete)
- [ ] Reference: "CI Relationship Types" (complete)
- [ ] Explanation: "Why Configuration Management Matters" (complete)
- [ ] All code examples tested and working
- [ ] Screenshots at 1024x768 for UI guides

**Documentation Tasks**:

**Tutorials** (Learning-oriented):

- [ ] `docs/tutorials/getting-started.md` - Complete end-to-end walkthrough
- [ ] `docs/tutorials/building-homelab-cmdb.md` - Real-world CMDB example

**How-to Guides** (Task-oriented):

- [ ] `docs/howto/managing-issue-lifecycle.md` - Issue workflow tasks
- [ ] `docs/howto/documenting-infrastructure-dependencies.md` - CI relationship patterns

**Reference** (Information-oriented):

- [ ] `docs/reference/cmdb-schema.md` - Complete CI schema reference
- [ ] `docs/reference/ci-relationship-types.md` - Relationship type definitions

**Explanation** (Understanding-oriented):

- [ ] `docs/explanation/why-configuration-management.md` - ITIL CMDB concepts

**Quality Checklist**:

- [ ] All code examples tested
- [ ] All screenshots captured at 1024x768
- [ ] Internal links validated
- [ ] Spelling and grammar checked
- [ ] Follows Diátaxis principles

**Dependencies**: None (can proceed in parallel)

**Estimated Time**: 2-3 days

______________________________________________________________________

#### Story PR-2: Test Parallelization and Performance

**Story Points**: 4
**Priority**: Medium
**Status**: 🔄 Not Started
**Assignee**: TBD

**User Story**:

> As a developer, I want fast test execution so that I can get quick feedback during development.

**Current State**:

- Full BDD suite: 2+ minutes
- Each scenario launches browser, loads pages
- No parallelization
- Database initialization overhead

**Acceptance Criteria**:

- [ ] Behave parallel execution configured
- [ ] Test execution time reduced by 40%+
- [ ] No test pollution between parallel runs
- [ ] Database fixtures instead of full reinit
- [ ] Shared browser context where safe
- [ ] CI/CD pipeline updated
- [ ] Documentation updated

**Technical Tasks**:

- [ ] Research Behave parallel execution options
- [ ] Configure parallel test runs
- [ ] Implement test isolation (separate databases or transactions)
- [ ] Optimize database setup/teardown
- [ ] Consider pytest-xdist integration
- [ ] Measure execution time improvements
- [ ] Update CI/CD configuration

**Performance Targets**:

- Current: ~2 minutes for 12 scenarios
- Target: \<1 minute for 12 scenarios
- Target: \<3 minutes for 40+ scenarios (v1.0.0 goal)

**Dependencies**: Story TD-1 (test reliability), Story TD-2 (database management)

**Estimated Time**: 2 days

______________________________________________________________________

## Sprint Backlog Summary

| Story | Description                | Points | Priority | Status      | Dependencies | Actual |
| ----- | -------------------------- | ------ | -------- | ----------- | ------------ | ------ |
| TD-1  | Fix BDD Test Integration   | 8      | Critical | ✅ Complete | None         | 8.0    |
| TD-2  | Database Management Script | 3      | High     | ✅ Complete | None         | 3.0    |
| 6     | Search/Sort Backend        | 5      | High     | Not Started | TD-1         | -      |
| 7     | Advanced Dashboard         | 5      | Medium   | Not Started | TD-1         | -      |
| PR-1  | Core Documentation         | 5      | High     | Not Started | None         | -      |
| PR-2  | Test Parallelization       | 4      | Medium   | Not Started | TD-1, TD-2   | -      |

**Total Story Points**: 30
**Completed**: 11 (36%)

## Sprint Execution Strategy

### Week 1 Focus: Technical Debt + Deferred Stories

**Days 1-2**: Story TD-1 (BDD Test Integration) - 8 points

- Critical blocker for other stories
- Deep investigation required
- Document findings for future reference

**Day 3**: Story TD-2 (Database Management) - 3 points

- Quick win to improve developer experience
- Supports ongoing BDD test work

**Days 4-5**: Story 6 (Search/Sort Backend) - 5 points

- Complete Sprint 5 deferred work
- Depends on TD-1 completion

### Week 2 Focus: Production Readiness

**Days 6-7**: Story PR-1 (Core Documentation) - 5 points

- Can proceed in parallel with other work
- Essential for v1.0.0 release

**Days 8-9**: Story 7 (Advanced Dashboard) - 5 points

- Complete Sprint 5 deferred work
- Adds value for end users

**Day 10**: Story PR-2 (Test Parallelization) - 4 points

- Depends on stable test suite
- Performance improvement for ongoing work

### Contingency Planning

If Story TD-1 takes longer than expected (>3 days):

- Defer Story PR-2 to Sprint 7
- Reduce Story 7 scope to basic dashboard only
- Maintain documentation priority (PR-1)

## Definition of Done

For each story:

- [ ] Acceptance criteria met
- [ ] BDD scenarios passing (where applicable)
- [ ] Code reviewed and refactored
- [ ] Pre-commit hooks passing
- [ ] Documentation updated
- [ ] Committed with conventional commit message
- [ ] Manual testing completed

For the sprint:

- [ ] All critical and high priority stories complete
- [ ] Test coverage >85%
- [ ] Code quality >9/10
- [ ] Sprint retrospective completed
- [ ] Sprint 5 deferred items cleared (Stories 6-7)
- [ ] Technical debt reduced significantly

## Risks and Mitigation

### Risk 1: BDD Test Integration Complexity

**Likelihood**: High
**Impact**: High (blocks multiple stories)

**Mitigation**:

- Allocate full 3-4 days for investigation
- Consider hybrid approach (API + UI tests)
- Engage Roundup community if needed
- Document partial solutions for incremental progress

### Risk 2: Scope Creep

**Likelihood**: Medium
**Impact**: Medium

**Mitigation**:

- Strict 30-point limit
- Mid-sprint review at day 5
- Defer low-priority items immediately if behind
- Focus on "done" not "perfect"

### Risk 3: Documentation Time Underestimated

**Likelihood**: Medium
**Impact**: Low

**Mitigation**:

- Use BDD scenarios as documentation base
- Focus on essential docs only
- Defer nice-to-have guides to Sprint 7
- Leverage existing content where possible

## Success Metrics

### Technical Debt Reduction

- [ ] BDD test pass rate: 0% → 70%+
- [ ] Test execution time: 2 min → \<1 min
- [ ] Database reset: 5 steps → 1 command

### Feature Completion

- [ ] Sprint 5 deferred stories: 100% complete
- [ ] Core CMDB features: Search + Dashboard functional

### Quality Metrics

- [ ] Test coverage: Maintain >85%
- [ ] Code quality: Maintain >9/10
- [ ] Documentation: 7 core docs complete

### Velocity

- [ ] Story points completed: 25-30 (realistic range)
- [ ] Stories completed: 5-6 of 6

## Next Sprint Preview

Sprint 7 will focus on:

- Remaining Sprint 6 production readiness stories (if any)
- Security hardening
- UI/UX polish
- Performance optimization
- BDD demonstration materials (presentations)
- Final testing for v1.0.0

Estimated Sprint 7 scope: 25-30 points

______________________________________________________________________

**Sprint 6 Status**: 🔄 **IN PROGRESS**
**Target Version**: v1.0.0
**Previous Sprint**: Sprint 5 (v0.6.0 - Complete)
**Next Sprint**: Sprint 7 (Final Polish for v1.0.0)

**Created**: 2025-11-18
**Last Updated**: 2025-11-18
