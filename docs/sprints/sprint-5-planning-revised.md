<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Sprint 5 Plan (REVISED) - Pasture Management System

**Sprint Duration**: 2 weeks
**Sprint Goal**: Implement CMDB foundation and test infrastructure improvements
**Target Version**: v0.6.0
**Start Date**: TBD
**End Date**: TBD

## Context and Rationale

### Why This Sprint Plan Changed

**Original Sprint 5 Plan**: Reporting & Dashboards (39 story points)

**Sprint 4 Reality Check**:

- Created 125 BDD scenarios for CMDB integration
- Only 6 scenarios currently passing (5%)
- 119 scenarios define unimplemented features
- Critical test infrastructure gaps discovered

**Revised Sprint 5 Focus**: **Implementation Phase**

Rationale: Must implement CMDB features before building reports about them. Sprint 4 created a comprehensive specification (BDD scenarios) - Sprint 5 executes that specification.

**Original Sprint 5 Content**: Moved to Sprint 6+ (after CMDB implementation)

## Sprint Objective

Implement the CMDB foundation specified in Sprint 4's BDD scenarios, establish robust test infrastructure, and bring the scenario pass rate from 5% to 50%+. Focus on delivering functional Configuration Item management with proper environment validation and test automation.

## Primary Goals

1. **Implement CMDB Schema**: Configuration Item classes and relationships
1. **Build Core CMDB Features**: CI creation, relationships, search
1. **Establish Test Infrastructure**: Environment validation, smoke tests
1. **Increase Scenario Coverage**: From 6 passing to 60+ passing scenarios

## User Stories (Implementation Focus)

### Epic: CMDB Implementation

#### Story 1: Implement CI Schema in Roundup

**As a** developer
**I want** to implement the CI schema in Roundup
**So that** configuration items can be stored and managed

**Acceptance Criteria**:

- CI class created in Roundup schema
- CI types: Server, Network Device, Storage, Software, Service, VM
- Required fields: name, type, status, criticality, description
- Optional fields: IP address, hostname, location, owner, notes
- Status values: Active, Maintenance, Retired, Decommissioned
- Criticality values: Low, Medium, High, Critical

**Implementation Tasks**:

- [ ] Update `tracker/schema.py` with CI class definition
- [ ] Add CI type multilink
- [ ] Add CI status and criticality enums
- [ ] Create initial data for CI types
- [ ] Update database schema
- [ ] Test schema migration

**Story Points**: 5

______________________________________________________________________

#### Story 2: Implement CI Creation (Web UI, CLI, API)

**As a** homelab sysadmin
**I want** to create configuration items via all interfaces
**So that** I can document my infrastructure

**Acceptance Criteria**:

- Web UI form for CI creation
- CLI command for CI creation
- REST API endpoint for CI creation
- Form validation for required fields
- Success confirmation messages
- BDD scenarios passing for CI creation

**Implementation Tasks**:

- [ ] Create `tracker/html/ci.item.html` template
- [ ] Implement CI creation form
- [ ] Add form validation
- [ ] Implement CLI CI creation
- [ ] Implement REST API CI endpoint
- [ ] Update step definitions for CI creation

**BDD Scenarios Target**: 12 scenarios passing

**Story Points**: 8

______________________________________________________________________

#### Story 3: Implement CI Relationships and Dependencies

**As a** homelab sysadmin
**I want** to document dependencies between CIs
**So that** I can understand impact of changes

**Acceptance Criteria**:

- Relationship types: depends_on, hosts, connects_to, runs_on
- Bi-directional relationship tracking
- Impact analysis queries
- Web UI for managing relationships
- API support for relationship CRUD

**Implementation Tasks**:

- [ ] Add relationship multilinks to CI schema
- [ ] Create relationship detectors
- [ ] Implement Web UI relationship management
- [ ] Add API endpoints for relationships
- [ ] Create impact analysis queries

**BDD Scenarios Target**: 10 scenarios passing

**Story Points**: 8

______________________________________________________________________

#### Story 4: Implement CI-Issue-Change Integration

**As a** homelab sysadmin
**I want** to link CIs to issues and changes
**So that** I can track what's affected by problems and changes

**Acceptance Criteria**:

- Link issues to one or more CIs
- Link changes to one or more CIs
- View related issues from CI details
- View related changes from CI details
- View affected CIs from issue/change details

**Implementation Tasks**:

- [ ] Add CI multilink to Issue class
- [ ] Add CI multilink to Change class
- [ ] Update issue templates to show CIs
- [ ] Update change templates to show CIs
- [ ] Implement linking UI
- [ ] Update API endpoints

**BDD Scenarios Target**: 15 scenarios passing

**Story Points**: 5

______________________________________________________________________

#### Story 5: Implement CI Search and Filtering

**As a** homelab sysadmin
**I want** to search and filter configuration items
**So that** I can quickly find infrastructure components

**Acceptance Criteria**:

- Filter by CI type
- Filter by status
- Filter by criticality
- Search by name, hostname, IP address
- Sort by name, criticality, created date
- Empty state messaging

**Implementation Tasks**:

- [ ] Create `tracker/html/ci.index.html` template
- [ ] Implement search functionality
- [ ] Add filter dropdowns
- [ ] Implement sorting
- [ ] Style CI list view
- [ ] Add pagination

**BDD Scenarios Target**: 12 scenarios passing

**Story Points**: 5

______________________________________________________________________

### Epic: Test Infrastructure Improvements

#### Story 6: Environment Validation Framework

**As a** developer
**I want** automated environment validation
**So that** configuration issues are caught immediately

**Acceptance Criteria**:

- `before_all()` hook validates environment
- Checks tracker URL accessibility
- Validates configuration consistency
- Verifies required schema elements
- Clear error messages for misconfigurations
- Fast-fail on validation errors

**Implementation Tasks**:

- [ ] Implement `features/environment.py` validation
- [ ] Add tracker accessibility check
- [ ] Add configuration consistency checks
- [ ] Add schema validation
- [ ] Create validation error messages
- [ ] Document validation patterns

**Story Points**: 3

______________________________________________________________________

#### Story 7: Smoke Test Suite

**As a** developer
**I want** a fast smoke test suite
**So that** I can validate basic functionality quickly

**Acceptance Criteria**:

- Smoke tests run in \<30 seconds
- Cover: tracker access, login, basic CRUD
- Tagged with `@smoke`
- Run before full test suite
- Documented execution strategy

**Implementation Tasks**:

- [ ] Identify critical smoke scenarios
- [ ] Tag scenarios with `@smoke`
- [ ] Create smoke test script
- [ ] Add to pre-commit hooks
- [ ] Document smoke test strategy

**Story Points**: 2

______________________________________________________________________

## Technical Tasks

### Schema Implementation

- [ ] Update Roundup schema with CI class
- [ ] Add CI types, statuses, criticality
- [ ] Implement relationship multilinks
- [ ] Create database migration
- [ ] Test schema changes

### Web UI Development

- [ ] Create CI creation form template
- [ ] Create CI list view template
- [ ] Create CI detail view template
- [ ] Implement relationship management UI
- [ ] Add search and filter controls

### CLI Implementation

- [ ] Add CI creation commands
- [ ] Add CI list commands
- [ ] Add relationship management commands
- [ ] Test CLI functionality

### API Development

- [ ] Implement REST endpoints for CI CRUD
- [ ] Add relationship endpoints
- [ ] Add search and filter endpoints
- [ ] Test API functionality

### Test Infrastructure

- [ ] Implement environment validation
- [ ] Create smoke test suite
- [ ] Optimize test execution
- [ ] Update step definitions

### Documentation

- [ ] Tutorial: "Building Your Homelab CMDB"
- [ ] How-to: "Documenting Infrastructure Dependencies"
- [ ] Reference: "CMDB Schema and Attributes"
- [ ] Reference: "CI Relationship Types"
- [ ] Explanation: "Why Configuration Management Matters"

## Action Items from Sprint 4 Retrospective

Integrating specific action items identified in Sprint 4:

### Immediate Actions (Sprint 5)

1. ✅ **Create environment validation guide**

   - Implemented in Story 6
   - Document `before_all()` validation pattern

1. ✅ **Create BDD scenario pattern guide**

   - Document background patterns for Web/CLI/API
   - Create scenario templates

1. ✅ **Create smoke test strategy**

   - Implemented in Story 7
   - Define `@smoke` tagged scenarios

### Process Improvements (Sprint 5)

4. ✅ **Add configuration validation**

   - Implemented in Story 6
   - Implement `before_all()` validation

1. ✅ **Create configuration change checklist**

   - Document all configuration files
   - Establish update procedure

1. 🔄 **Optimize test execution** (defer partial)

   - Research parallel execution (Sprint 6)
   - Investigate test result caching (Sprint 6)
   - Document optimization strategy (Sprint 5)

### Documentation Updates (Sprint 5)

7. ✅ **Update CLAUDE.md with configuration patterns**

   - Add environment validation section
   - Document testing best practices

1. ✅ **Create troubleshooting guide**

   - Document common test failures
   - List debugging strategies

## Definition of Done

- [ ] All 7 user stories completed with acceptance criteria met
- [ ] 60+ BDD scenarios passing (up from 6)
- [ ] CMDB schema implemented in Roundup
- [ ] CI creation, search, and relationships functional
- [ ] Environment validation automated
- [ ] Smoke test suite operational
- [ ] Code passes pre-commit hooks
- [ ] Documentation completed (5 documents)
- [ ] Test coverage >85%
- [ ] Screenshots at 1024x768 for all CMDB views
- [ ] CHANGELOG.md updated for v0.6.0
- [ ] Sprint retrospective completed

## Sprint Backlog

| Task                                       | Story Points | Status      |
| ------------------------------------------ | ------------ | ----------- |
| Story 1: Implement CI Schema               | 5            | Not Started |
| Story 2: Implement CI Creation             | 8            | Not Started |
| Story 3: Implement CI Relationships        | 8            | Not Started |
| Story 4: Implement CI-Issue-Change Links   | 5            | Not Started |
| Story 5: Implement CI Search and Filtering | 5            | Not Started |
| Story 6: Environment Validation Framework  | 3            | Not Started |
| Story 7: Smoke Test Suite                  | 2            | Not Started |
| Documentation Tasks                        | 5            | Not Started |

**Total Story Points**: 41

## Risks and Dependencies

### Risks

- **Schema Migration Complexity**: Roundup schema changes can be tricky
  - *Mitigation*: Test migrations on copy of tracker, document rollback
- **Scenario Pass Rate**: Target 60+ may be ambitious
  - *Mitigation*: Prioritize high-value scenarios, accept 50+ as success
- **Test Execution Time**: More passing scenarios = longer test runs
  - *Mitigation*: Implement smoke tests, document optimization for Sprint 6

### Dependencies

- Sprint 4 BDD scenarios completed ✅
- Roundup tracker functional ✅
- Test infrastructure improvements from Sprint 4 ✅

## Success Metrics

- [ ] Scenario pass rate: 5% → 50%+ (6 → 60+ passing)
- [ ] CMDB functional with all CRUD operations
- [ ] Environment validation catching configuration issues
- [ ] Smoke tests running in \<30 seconds
- [ ] Test execution documented and optimized
- [ ] Sprint goal achieved: CMDB foundation operational

## Velocity Planning

### Sprint History

- Sprint 1: 19 points (learning curve)
- Sprint 2: 27 points (found rhythm)
- Sprint 3: 33 points (peak productivity)
- Sprint 4: Specification focus (125 BDD scenarios)

### Sprint 5 Target

**Planned**: 41 story points
**Realistic**: 35-38 points (accounting for implementation complexity)
**Minimum Viable**: 31 points (Stories 1, 2, 4, 5, 6, 7)

**Rationale**: Implementation sprints typically have lower velocity than specification sprints. Target is ambitious but achievable given clear BDD scenarios defining requirements.

## Looking Ahead

### Sprint 6 Possibilities

With CMDB foundation complete (Sprint 5), Sprint 6 could focus on:

**Option A: Complete CMDB Features**

- Advanced CI features (versioning, change history)
- CI templates and cloning
- Bulk operations
- Import/export

**Option B: Reporting & Dashboards**

- Resume original Sprint 5 plan
- Issue, change, and CMDB reports
- Custom report builder
- Scheduled reports

**Option C: Change Management Completion**

- Implement remaining change workflow scenarios
- Approval workflows
- Risk assessment
- Implementation tracking

**Decision Point**: End of Sprint 5 retrospective

## Notes

### Why 41 Story Points?

This is higher than typical velocity (27-33) because:

1. **Clear Specifications**: 125 BDD scenarios eliminate ambiguity
1. **Implementation Focus**: Less discovery, more execution
1. **Technical Debt Payoff**: Infrastructure improvements enable faster work
1. **Motivated Team**: Clear path from 5% to 50%+ passing scenarios

### Scenario Pass Rate Goal

**Current**: 6/125 passing (5%)
**Target**: 60/125 passing (48%)
**Stretch**: 75/125 passing (60%)

This represents implementing:

- Story 1: ~0 new passing (schema only)
- Story 2: ~12 new passing (CI creation)
- Story 3: ~10 new passing (CI relationships)
- Story 4: ~15 new passing (CI-Issue-Change links)
- Story 5: ~12 new passing (CI search)
- Story 6-7: ~5 new passing (smoke tests)
- Ancillary: ~6 new passing (existing scenarios fixed by schema)

**Total**: ~60 new passing scenarios

### Test Infrastructure Investment

Stories 6-7 (5 points) are infrastructure investment that will:

- Reduce debugging time in future sprints
- Catch configuration issues immediately
- Enable faster test feedback loops
- Improve developer productivity

ROI expected by Sprint 6.

______________________________________________________________________

**Sprint Plan Status**: Ready for execution
**Next Step**: Sprint 5 kickoff and Story 1 implementation
