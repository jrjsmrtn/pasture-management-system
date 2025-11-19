<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Sprint Planning - Pasture Management System

This directory contains sprint planning and tracking documents for the Pasture Management System development.

## Sprint Overview

The PMS development follows a 6-sprint roadmap (12 weeks total) to deliver a production-ready v1.0.0 release:

### Sprint 1: Foundation & Basic Issue Tracking (v0.2.0)

**Duration**: 2 weeks
**Goal**: Set up Roundup tracker with basic issue tracking and first BDD scenarios

**Key Deliverables**:

- Roundup tracker installation and configuration
- Basic issue CRUD operations (Web UI, CLI, API)
- BDD infrastructure (Behave, Playwright at 1024x768)
- First tutorial: "Getting Started with PMS"

**Story Points**: 27

[📄 Sprint 1 Planning](sprint-1-planning.md)

______________________________________________________________________

### Sprint 2: Issue Lifecycle & Change Management Foundation (v0.3.0)

**Duration**: 2 weeks
**Goal**: Implement issue workflow and introduce change management

**Key Deliverables**:

- Issue status transitions (New → In Progress → Resolved → Closed)
- Issue assignment to users
- Change request schema and creation
- Tutorial: "Understanding ITIL Workflows"

**Story Points**: 27

[📄 Sprint 2 Planning](sprint-2-planning.md)

______________________________________________________________________

### Sprint 3: Change Management Workflows (v0.4.0)

**Duration**: 2 weeks
**Goal**: Complete change management with approval workflows

**Key Deliverables**:

- Change approval workflow (Request → Assessment → Approval → Implementation → Completion)
- Change-to-issue relationships
- Risk assessment and scheduling
- Marpit presentation: "BDD Testing in Practice"

**Story Points**: 33

[📄 Sprint 3 Planning](sprint-3-planning.md)

______________________________________________________________________

### Sprint 4: CMDB Foundation (v0.5.0)

**Duration**: 2 weeks
**Goal**: Implement Configuration Management Database

**Key Deliverables**:

- CI schema (Server, Network Device, Storage, Software, Service, VM)
- CI relationships and dependencies
- CI-Issue-Change integration
- Tutorial: "Building Your Homelab CMDB"

**Story Points**: 33

[📄 Sprint 4 Planning](sprint-4-planning.md)

______________________________________________________________________

### Sprint 5: CMDB Implementation & Test Infrastructure (v0.6.0) ✅

**Duration**: 2 weeks
**Status**: COMPLETE (31/41 story points, 76%)
**Goal**: Implement CMDB foundation and establish test infrastructure

> **⚠️ REVISED 2025-11-16**: Original plan (Reporting & Dashboards) deferred to Sprint 6+

**Key Deliverables**:

- ✅ CMDB schema implementation in Roundup
- ✅ CI creation, relationships, and dependencies (Web UI, CLI, API)
- ✅ CI-Issue-Change integration
- ✅ CI search and filtering
- ✅ CSV export functionality
- ✅ Template validation automation
- 🔄 Environment validation framework (partially complete)
- 🔄 Stories 6-7 deferred to Sprint 6 (10 points)

**Story Points**: 31/41 completed

[📄 Sprint 5 Planning (Revised)](sprint-5-planning-revised.md) | [📊 Sprint 5 Backlog](sprint-5-backlog.md) | [🔄 Sprint 5 Retrospective](sprint-5-retrospective.md)

______________________________________________________________________

### Sprint 6: Polish & Production Release (v1.0.0) 🔄

**Duration**: 2 weeks
**Status**: In Progress (Day 3 - 16/30 points, 53%)
**Goal**: Complete deferred stories and begin production readiness

**Key Deliverables**:

- ✅ Technical debt resolution (BDD test integration - 8 points)
- ✅ Database management automation (3 points)
- ✅ Complete Sprint 5 deferred Story 6: Search/Sort (5 points)
- 🔄 Story 7: Advanced Dashboard (5 points) - pending
- 🔄 Core Diátaxis documentation (5 points) - pending
- 🔄 Test parallelization (4 points) - pending

**Story Points**: 30 (16 completed, 14 remaining)

[📄 Sprint 6 Planning](sprint-6-planning.md) | [📊 Sprint 6 Backlog](sprint-6-backlog.md)

______________________________________________________________________

### Sprint 7: Email Interface & Four-Interface BDD Testing (v1.1.0)

**Duration**: 2 weeks
**Goal**: Implement email interface and complete four-interface BDD testing architecture

**Key Deliverables**:

- Email-based issue creation and updates
- Email notification system
- Greenmail/Python SMTP testing infrastructure
- Email step definition library
- **Four-interface BDD testing** (Web UI + CLI + REST API + Email)
- Cross-interface BDD scenarios
- Email security and anti-spam measures
- Four-interface testing documentation

**Story Points**: 39

[📄 Sprint 7 Planning](sprint-7-planning.md)

______________________________________________________________________

## Development Metrics

### Total Effort

- **Duration**: 14 weeks (7 sprints × 2 weeks)
- **Total Story Points**: 245 (206 for v1.0.0 + 39 for v1.1.0)
- **v1.0.0 Target**: Sprint 6 (production release)
- **v1.1.0 Target**: Sprint 7 (email interface + four-interface BDD testing)

### Quality Targets

- **Test Coverage**: >85% throughout development
- **BDD Scenarios**: 40+ scenarios by v1.0.0, 65+ by v1.1.0 (with email interface)
- **Four-Interface Testing**: Web UI + CLI + REST API + Email (complete by v1.1.0)
- **Screenshot Resolution**: 1024x768 (English only)
- **Documentation**: Complete Diátaxis framework

### Version Progression

```
v0.1.0  → Foundation
v0.2.0  → Sprint 1 (Basic Issue Tracking)
v0.3.0  → Sprint 2 (Issue Lifecycle + Change Foundation)
v0.4.0  → Sprint 3 (Change Workflows)
v0.5.0  → Sprint 4 (CMDB BDD Specification)
v0.6.0  → Sprint 5 (CMDB Implementation) ← current
v1.0.0  → Sprint 6 (Production Release)
v1.1.0  → Sprint 7 (Email Interface + Four-Interface BDD)
```

## Sprint Process

Each sprint follows this structure:

### Planning Phase

- Review previous sprint retrospective
- Define sprint goal and user stories
- Estimate story points
- Identify risks and dependencies
- Create sprint backlog

### Execution Phase

- Daily progress tracking
- BDD scenarios written before implementation
- Code reviews via pre-commit hooks
- Continuous integration testing
- Documentation updates

### Review Phase

- Demo completed features
- Validate against acceptance criteria
- Review BDD scenario coverage
- Update CHANGELOG.md
- Tag version release

### Retrospective Phase

- What went well
- What could be improved
- Action items for next sprint
- Update best practices

## BDD Testing Strategy

Each sprint includes comprehensive BDD scenarios across multiple interfaces:

### Testing Interfaces

- **Web UI**: Playwright browser automation (1024x768)
- **CLI**: Command-line interface testing (`roundup-admin`)
- **REST API**: REST/XML-RPC API testing
- **Email**: Email gateway testing (`roundup-mailgw`) - Sprint 7+

### Four-Interface Testing (Sprint 7+)

Sprint 7 completes the **four-interface BDD testing architecture**, demonstrating:

- Same functionality tested across all four interfaces
- Cross-interface scenarios (e.g., create via email, verify via web/CLI/API)
- Notification testing across all interfaces
- Email testing with Greenmail or Python SMTP server

### Scenario Coverage Goals

- Sprint 1: 10+ scenarios (Web, CLI, API)
- Sprint 2: 15+ scenarios (Web, CLI, API)
- Sprint 3: 20+ scenarios (Web, CLI, API)
- Sprint 4: 25+ scenarios (Web, CLI, API)
- Sprint 5: 30+ scenarios (Web, CLI, API)
- Sprint 6: 40+ scenarios (Web, CLI, API)
- Sprint 7: 65+ scenarios (Web, CLI, API, Email) - **Four-interface testing complete**

## Documentation Timeline

Following the Diátaxis framework:

### Tutorials (Learning-oriented)

- Sprint 1: "Getting Started with PMS"
- Sprint 2: "Understanding ITIL Workflows"
- Sprint 4: "Building Your Homelab CMDB"
- Sprint 5: "Understanding Your Homelab Metrics"
- Sprint 6: "Writing Your First BDD Feature"

### How-to Guides (Problem-oriented)

- Sprint 2: "Managing Issue Lifecycle"
- Sprint 3: "Submitting a Change Request", "Assessing Change Risk"
- Sprint 4: "Documenting Infrastructure Dependencies"
- Sprint 5: "Generating Reports", "Creating Custom Reports", "Scheduling Automated Reports"
- Sprint 6: "Debugging BDD Scenarios"

### Reference (Information-oriented)

- Sprint 1: "Issue Schema"
- Sprint 2: "Issue Status Transitions", "Change Request Schema"
- Sprint 3: "Change Workflow States"
- Sprint 4: "CMDB Schema and Attributes", "CI Relationship Types"
- Sprint 5: "Available Metrics and KPIs"
- Sprint 6: "API Documentation", "Complete Step Definition Library"

### Explanation (Understanding-oriented)

- Sprint 2: "Why Change Management Matters"
- Sprint 3: "ITIL Change Management Principles"
- Sprint 4: "Why Configuration Management Matters"
- Sprint 6: "Architecture Overview", "Design Decisions"

## Marpit Presentations

BDD demonstration presentations created throughout sprints:

1. **Sprint 3**: "BDD Testing in Practice"
1. **Sprint 6**:
   - "Introduction to BDD"
   - "Writing Effective Gherkin Scenarios"
   - "Behave and Playwright Integration"
   - "BDD Testing Best Practices"
1. **Sprint 7**:
   - "Four-Interface BDD Testing with Roundup"
   - "Email Testing with Greenmail and Behave"

## Current Status

**Current Version**: v0.6.0 (Sprint 5 Complete)
**Current Sprint**: Sprint 6 - Complete Deferred Stories & Production Readiness (Day 3)
**Next Sprint**: Sprint 7 - Email Interface & Four-Interface BDD Testing
**Targets**: v1.0.0 (Sprint 6), v1.1.0 (Sprint 7)

**Sprint 6 Progress** (Day 3):

- 16/30 story points completed (53%)
- ✅ BDD test integration fixed - Playwright selector issues resolved
- ✅ Database management automation - one-command reset script
- ✅ CI search/sort/filter complete - 10/11 BDD scenarios passing
- 🔄 Remaining: Dashboard (5pts), Documentation (5pts), Test parallelization (4pts)
- Target: Complete remaining 14 points for v1.0.0 release

## Sprint Documents

Each sprint directory contains:

- `sprint-N-planning.md`: Sprint goals, user stories, and backlog
- `sprint-N-retrospective.md`: Lessons learned and improvements (created at sprint end)

## Related Documentation

- [Architecture Decisions](../adr/): ADRs documenting key decisions
- [Documentation Framework](../README.md): Diátaxis documentation structure
- [CHANGELOG.md](../../CHANGELOG.md): Version history
- [CLAUDE.md](../../CLAUDE.md): AI-assisted development context

______________________________________________________________________

**Note**: This is a living plan. Sprint scope and timelines may adjust based on actual progress and discovered complexity. The focus remains on delivering quality BDD demonstration value alongside functional ITIL-inspired capabilities.
