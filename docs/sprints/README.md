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

---

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

---

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

---

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

---

### Sprint 5: Reporting & Dashboards (v0.6.0)
**Duration**: 2 weeks
**Goal**: Add reporting and analytics capabilities

**Key Deliverables**:
- Issue statistics dashboard
- Change management reports
- CMDB health reports
- Custom report builder
- Scheduled/email reports

**Story Points**: 39

[📄 Sprint 5 Planning](sprint-5-planning.md)

---

### Sprint 6: Polish & Production Release (v1.0.0)
**Duration**: 2 weeks
**Goal**: Prepare for production release

**Key Deliverables**:
- Performance optimization
- UI/UX polish and accessibility
- Security hardening
- Complete Diátaxis documentation
- BDD demonstration materials (4 Marpit presentations)
- Deployment packaging (scripts, containers)

**Story Points**: 47

[📄 Sprint 6 Planning](sprint-6-planning.md)

---

## Development Metrics

### Total Effort
- **Duration**: 12 weeks (6 sprints × 2 weeks)
- **Total Story Points**: 206
- **Target**: v1.0.0 production release

### Quality Targets
- **Test Coverage**: >85% throughout development
- **BDD Scenarios**: 40+ scenarios by v1.0.0
- **Screenshot Resolution**: 1024x768 (English only)
- **Documentation**: Complete Diátaxis framework

### Version Progression
```
v0.1.0  → Foundation (current)
v0.2.0  → Sprint 1 (Basic Issue Tracking)
v0.3.0  → Sprint 2 (Issue Lifecycle + Change Foundation)
v0.4.0  → Sprint 3 (Change Workflows)
v0.5.0  → Sprint 4 (CMDB)
v0.6.0  → Sprint 5 (Reporting)
v1.0.0  → Sprint 6 (Production Release)
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

Each sprint includes comprehensive BDD scenarios across all three interfaces:

### Testing Interfaces
- **Web UI**: Playwright browser automation (1024x768)
- **CLI**: Command-line interface testing
- **API**: REST/XML-RPC API testing

### Scenario Coverage Goals
- Sprint 1: 10+ scenarios
- Sprint 2: 15+ scenarios
- Sprint 3: 20+ scenarios
- Sprint 4: 25+ scenarios
- Sprint 5: 30+ scenarios
- Sprint 6: 40+ scenarios (total)

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
2. **Sprint 6**:
   - "Introduction to BDD"
   - "Writing Effective Gherkin Scenarios"
   - "Behave and Playwright Integration"
   - "BDD Testing Best Practices"

## Current Status

**Current Version**: v0.1.0 (Foundation)
**Next Sprint**: Sprint 1 - Foundation & Basic Issue Tracking
**Target**: v0.2.0

## Sprint Documents

Each sprint directory contains:
- `sprint-N-planning.md`: Sprint goals, user stories, and backlog
- `sprint-N-retrospective.md`: Lessons learned and improvements (created at sprint end)

## Related Documentation

- [Architecture Decisions](../adr/): ADRs documenting key decisions
- [Documentation Framework](../README.md): Diátaxis documentation structure
- [CHANGELOG.md](../../CHANGELOG.md): Version history
- [CLAUDE.md](../../CLAUDE.md): AI-assisted development context

---

**Note**: This is a living plan. Sprint scope and timelines may adjust based on actual progress and discovered complexity. The focus remains on delivering quality BDD demonstration value alongside functional ITIL-inspired capabilities.
