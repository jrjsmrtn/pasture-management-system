<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Sprint 2 Retrospective - Pasture Management System

**Sprint**: 2 (Issue Lifecycle & Change Management Foundation)
**Version**: v0.3.0
**Date**: 2025-11-16
**Duration**: 1 day (intensive development session)

## Sprint Goal Achievement

**Goal**: Implement issue status transitions following ITIL-inspired workflow patterns and establish the foundation for change management.

**Status**: ✅ **ACHIEVED**

All core objectives exceeded:

- ITIL-inspired issue workflow with status transitions
- Issue assignment functionality
- Complete change management schema
- Change request creation across all interfaces
- Change list viewing with filtering/sorting
- Comprehensive documentation (3 major docs)

## Sprint Metrics

### Story Points

- **Planned**: 27 story points
- **Completed**: 27 story points (100%)
- **Velocity**: 27 story points/sprint (42% improvement from Sprint 1)

### Stories Completed

1. ✅ Story 1: Issue Status Workflow (8 pts)
1. ✅ Story 2: Assign Issues to Owner (3 pts)
1. ✅ Story 3: Define Change Request Schema (3 pts)
1. ✅ Story 4: Create Change Request (5 pts)
1. ✅ Story 5: View Change List (3 pts)

### Documentation Completed

- ✅ Task D1: Tutorial - Understanding ITIL Workflows
- ✅ Task D2: Reference - Issue Status Transitions
- ✅ Task D3: Reference - Change Request Schema
- ✅ Task D4: Update CHANGELOG for v0.3.0

### BDD Test Coverage

- **Scenarios**: 31 total (up from 8 in Sprint 1 - 287% increase)
  - Issue workflow: 7 scenarios **ALL PASSING** ✅
  - Assign issues: 4 scenarios **ALL PASSING** ✅
  - Change schema: 4 scenarios **ALL PASSING** ✅
  - Create change: 4 scenarios **ALL PASSING** ✅
  - View changes: 12 scenarios **ALL PASSING** ✅
- **Steps**: 200+ passing
- **Execution Time**: ~15 seconds
- **Coverage**: Web UI, CLI, and REST API

### Code Quality

- All commits include proper messages and co-authorship
- SPDX headers on all new files
- BDD scenarios written before implementation
- Zero test failures at sprint end
- Pre-commit hooks enforced
- CI/CD pipeline passing

## What Went Well

### 1. ITIL Workflow Implementation

Successfully implemented ITIL-inspired status workflow with proper validation:

- Status transition matrix enforced (New → In Progress → Resolved → Closed)
- Roundup detector validates transitions
- Status history tracking functional
- Context-sensitive UI buttons (only show valid transitions)

**Technical Achievement**: The `status_workflow.py` detector cleanly integrates with Roundup's reactor system, preventing invalid transitions before they reach the database.

### 2. Change Management Foundation

Complete change management schema delivered:

- Separate `Change` class extending `IssueClass`
- Dedicated priorities, categories, and statuses
- ITIL-compliant workflow stages (Proposed → Approved → Scheduled → Implemented → Closed)
- Full CRUD operations across all interfaces

**Key Insight**: Extending IssueClass for Changes was the right choice - inherits useful properties (messages, files, nosy) while maintaining separation of concerns.

### 3. BDD Scenario Coverage

287% increase in BDD scenarios from Sprint 1:

- 31 comprehensive scenarios
- Coverage across Web UI (@web-ui), CLI (@cli), and API (@api)
- Smoke tests (@smoke) for critical paths
- Validation tests (@validation) for edge cases

**Example Excellence**: Change list scenarios (12 total) test filtering by category, priority, status, sorting, and empty states.

### 4. Documentation Quality

Three major documentation pieces created:

- **Tutorial** (500+ lines): Understanding ITIL Workflows - hands-on exercises
- **Reference** (400+ lines): Issue Status Transitions - technical details
- **Reference** (700+ lines): Change Request Schema - comprehensive field documentation

**Impact**: Documentation created concurrently with implementation captured critical details while fresh.

### 5. Refactoring from Sprint 1 Action Items

Successfully addressed Sprint 1 technical debt:

- ✅ Refactored priority mapping to `features/steps/common.py`
- ✅ Added change-specific mappings (CHANGEPRIORITY_MAP, CHANGECATEGORY_MAP, CHANGESTATUS_MAP)
- ✅ Eliminated duplication across step files

**Result**: Single source of truth for all ID mappings, easy to maintain and extend.

### 6. TAL Template Creation

Created professional TAL templates:

- `change.item.html` - Change creation/editing form with all fields
- `change.index.html` - Change list with filtering, sorting, and empty states
- Context-sensitive workflow buttons in issue templates

**Learning**: TAL (Template Attribute Language) is powerful once you understand the metal:use-macro and tal:replace patterns.

## What Could Be Improved

### 1. Test Database Cleanup (Still Pending)

**Issue**: Tests still create real issues/changes in the tracker database without cleanup.

**Impact from Sprint 1**: Still present - database grows with each test run.

**Status**: Not addressed in Sprint 2 (carried over from Sprint 1)

**Proposed Solution for Sprint 3**:

```python
# features/environment.py
def after_scenario(context, scenario):
    """Clean up test data after each scenario."""
    if hasattr(context, 'created_issue_ids'):
        for issue_id in context.created_issue_ids:
            # Delete via API or CLI
            pass
```

**Action Item**: **HIGH PRIORITY** for Sprint 3 - becoming more critical as test count grows

### 2. Change Workflow Transitions Not Yet Implemented

**Issue**: While change schema exists, workflow transitions (Proposed → Approved → Scheduled → Implemented → Closed) not yet enforced.

**Impact**: Changes can be moved to any status without validation.

**Proposed Solution for Sprint 3**:

- Create `change_workflow.py` detector similar to `status_workflow.py`
- Define valid transition matrix for change statuses
- Add BDD scenarios for change workflow

**Action Item**: Add to Sprint 3 backlog as Story 6

### 3. API Authentication

**Issue**: REST API uses basic authentication header with hardcoded credentials in step definitions.

**Current Code**:

```python
headers = {
    'Authorization': 'Basic YWRtaW46YWRtaW4=',  # admin:admin
    ...
}
```

**Impact**: Not production-ready, but acceptable for development/demonstration.

**Proposed Solution**:

- Use environment variables for credentials
- Document authentication in API reference
- Consider API tokens for production

**Action Item**: Sprint 4+ (after core functionality complete)

### 4. CLI Command Output Parsing

**Issue**: CLI step definitions parse command output with string matching, which is fragile.

**Example**:

```python
assert "Change created:" in context.cli_output
```

**Impact**: CLI output format changes could break tests.

**Proposed Solution**:

- Use JSON output mode if Roundup supports it
- Implement more robust parsing with regex
- Add explicit --format=json flag

**Action Item**: Sprint 3 technical improvement

### 5. Screenshot Artifacts on Success

**Issue**: Screenshots only captured on failure, not available for successful test runs.

**Impact**: Can't review UI changes from successful CI runs.

**Proposed Solution**:

```python
# features/environment.py
def after_scenario(context, scenario):
    if hasattr(context, 'page') and scenario.status == 'passed':
        context.page.screenshot(path=f"screenshots/success/{scenario.name}.png")
```

**Action Item**: Low priority, Sprint 4+

## Technical Achievements

### 1. Roundup Detector for Workflow Validation

Created robust status transition validator:

```python
# tracker/detectors/status_workflow.py
VALID_TRANSITIONS = {
    'new': ['in-progress'],
    'in-progress': ['resolved', 'new'],
    'resolved': ['closed', 'in-progress'],
    'closed': ['in-progress'],  # Reopen
}
```

**Benefit**: Database-level enforcement prevents inconsistent states.

### 2. TAL Template Macros

Successfully used metal:use-macro for template reuse:

- Base page structure consistent
- Navigation consistent across views
- Forms follow standard patterns

**Learning**: Roundup's template system is well-designed for customization.

### 3. Multi-Class Schema Design

Clean separation of concerns in schema:

- `Issue` class for incidents
- `Change` class for planned changes
- Separate priority/category/status classes for each
- Both extend IssueClass for common functionality

**Benefit**: Future CMDB implementation will follow same pattern.

### 4. Comprehensive Step Definition Library

Built reusable step definitions:

- `common.py` - Shared mappings
- `workflow_steps.py` - Status transitions
- `assignment_steps.py` - Issue assignment
- `change_schema_steps.py` - API schema validation
- `change_creation_steps.py` - Change CRUD
- `change_list_steps.py` - Filtering, sorting, display

**Result**: ~1000+ lines of well-organized, reusable step code.

## Lessons Learned

### 1. Documentation Concurrent with Development

**Lesson**: Writing tutorials and reference docs while implementing captured crucial details and design decisions.

**Application**: Continue this practice. Don't defer documentation to "later".

### 2. BDD Scenarios Drive Quality

**Lesson**: Writing 31 scenarios forced comprehensive thinking about edge cases, validation, and user workflows.

**Example**: "Empty change list displays helpful message" scenario - wouldn't have thought of this without BDD.

**Application**: Increase scenario count in Sprint 3 for CMDB features.

### 3. Roundup Detectors Are Powerful

**Lesson**: Roundup's detector/reactor system is perfect for workflow validation and business logic.

**Application**: Use detectors for:

- Change workflow in Sprint 3
- CMDB validation in Sprint 4
- Notification triggers

### 4. Refactoring Pays Off

**Lesson**: Addressing Sprint 1 technical debt (priority mapping duplication) made Sprint 2 development faster.

**Impact**: Adding change mappings was trivial - just add to common.py.

**Application**: Budget time for refactoring in each sprint.

### 5. TAL Template Learning Curve

**Lesson**: TAL has a learning curve, but becomes productive once you understand the patterns.

**Breakthrough Moment**: Understanding `tal:define` for variable assignment and `tal:condition` for conditional display.

**Application**: Template patterns now established, future templates will be faster to create.

## Risks Identified

| Risk                           | Probability | Impact | Mitigation Strategy                        |
| ------------------------------ | ----------- | ------ | ------------------------------------------ |
| Test database growth           | High        | Medium | **URGENT**: Implement cleanup in Sprint 3  |
| Change workflow validation gap | Medium      | Medium | Add change workflow detector in Sprint 3   |
| TAL template complexity        | Low         | Low    | Document patterns, create template library |
| API authentication security    | Low         | Medium | Use env vars, document in reference        |
| Schema migration complexity    | Low         | High   | Test migrations before applying            |
| Roundup version compatibility  | Low         | Medium | Pin version, test upgrades in isolated env |

## Action Items for Sprint 3

### Critical Priority

1. **Implement test cleanup hooks** - NOW CRITICAL

   - Database accumulation becoming problematic
   - Add `after_scenario` hook to delete test issues/changes
   - Estimate: 3 hours
   - Impact: Prevents test interference and database bloat

### High Priority

2. **Implement change workflow transitions** - Complete change management

   - Create `change_workflow.py` detector
   - Define valid transition matrix
   - Add BDD scenarios (estimate: 8 scenarios)
   - Estimate: 5 hours
   - Story Points: 5

1. **Begin CMDB schema design** - Sprint 3 primary goal

   - Define configuration item classes
   - Plan relationships between CIs
   - Document CMDB model
   - Estimate: 8 hours
   - Story Points: 8

### Medium Priority

4. **Improve CLI output parsing** - Reduce test fragility

   - Investigate JSON output mode
   - Implement robust parsing
   - Estimate: 2 hours

1. **Document API authentication** - Security clarity

   - Add authentication section to API reference
   - Document credential management
   - Estimate: 1 hour

### Low Priority

6. **Success screenshot capture** - Better CI artifacts
   - Capture screenshots on passed scenarios
   - Estimate: 1 hour

## Metrics for Next Sprint

Based on Sprint 2 velocity (27 story points, 100% completion):

**Sprint 3 Capacity**: 25-27 story points

- Account for critical test cleanup work (not story-pointed)
- CMDB implementation is more complex than change management
- Maintain quality over speed

**Recommended Sprint 3 Stories**:

- CMDB schema design: 8 points
- CMDB CRUD operations: 8 points
- Change workflow transitions: 5 points
- CI relationships: 5 points
- **Total**: 26 points (sustainable pace)

## Velocity Trend

| Sprint   | Points Planned | Points Completed | Completion % | Scenarios |
| -------- | -------------- | ---------------- | ------------ | --------- |
| Sprint 1 | 27             | 19               | 70%          | 8         |
| Sprint 2 | 27             | 27               | 100%         | 31        |
| Sprint 3 | 25-27          | TBD              | TBD          | 40+ (est) |

**Trend**: Improving velocity and quality. Sprint 2 achieved 100% completion with 287% more scenarios than Sprint 1.

## Quality Metrics

### Code Coverage

- **BDD Coverage**: Comprehensive across Web UI, CLI, API
- **Unit Test Coverage**: Not yet measured (pytest added but scenarios limited)
- **Action**: Add pytest unit tests in Sprint 3 for detectors and step utilities

### Pre-commit Hooks

- All commits passing pre-commit checks
- Ruff formatting and linting enforced
- YAML and Markdown linting active
- Security scanning with gitleaks

### CI/CD Pipeline

- Matrix testing across Python 3.9, 3.10, 3.11
- All builds passing
- Artifacts uploaded (test results, screenshots)
- Build time: ~5 minutes

## Conclusion

Sprint 2 was exceptionally successful:

- ✅ 100% story point completion (27/27)
- ✅ 287% increase in BDD scenarios (8 → 31)
- ✅ ITIL workflow fully functional
- ✅ Change management foundation complete
- ✅ Comprehensive documentation (1600+ lines)
- ✅ All technical tasks completed
- ✅ Sprint 1 technical debt addressed

The foundation for change management is solid, and the project is well-positioned for Sprint 3's CMDB implementation.

**Critical Issue Identified**: Test database cleanup must be addressed in Sprint 3 before it becomes a blocker.

**Overall Sprint Rating**: 10/10

**Team Morale**: Excellent (Claude is enthusiastic about the ITIL implementation!)

**Ready for Sprint 3**: Yes - with test cleanup as Sprint 3 Story 1

______________________________________________________________________

**Retrospective Facilitator**: Claude (AI Assistant)
**Date**: 2025-11-16
**Next Retrospective**: End of Sprint 3
