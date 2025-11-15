# ADR-0002: Adopt Development Best Practices

Date: 2025-11-15

## Status

Accepted

## Context

The Pasture Management System has dual objectives:
1. Implement a lightweight ITIL-inspired issue/change/CMDB management system for Homelab Sysadmins on Roundup Issue Tracker
2. Demonstrate to Python developers and BDD test writers the usefulness of BDD features, Gherkin, Behave, Playwright testing stack

This project serves as both a functional tool and an educational reference implementation. We need established practices for code quality, testing strategy, version management, documentation, and sprint-based development.

## Decision

We will adopt comprehensive development best practices emphasizing BDD as a core demonstration objective.

### Test-Driven Development (TDD) and Behavior-Driven Development (BDD)

**BDD-First Approach**: This project prioritizes BDD as both a development methodology and a teaching tool.

#### Behavior-Driven Development (BDD)
- **Feature Files**: Write Gherkin scenarios before implementation
- **Living Documentation**: BDD features serve as tutorials and examples
- **Tools**: Behave (Python) for feature testing, Playwright for web UI automation
- **JUnit XML Reports**: Generate test reports with screenshots for CI/CD
- **Collaboration**: Bridge business requirements and technical implementation

#### Test-Driven Development (TDD)
- **Red-Green-Refactor cycle**: For implementation details
- **Unit Tests**: Comprehensive coverage for Roundup customizations
- **Integration Tests**: Validate tracker web UI, CLI, and API

#### Testing Strategy
**This project uses BDD extensively because:**
- Primary objective is demonstrating BDD/Gherkin/Behave/Playwright to Python developers
- User-facing features (issue tracking, change management, CMDB)
- Multiple stakeholder types (sysadmins, developers, BDD learners)
- Tutorials will be based on BDD features and sprints
- Complex business logic (ITIL-inspired workflows)

### Semantic Versioning Strategy

**Initial Development**: 0.x.0 on main branch (dogfooding environment)
- **0.1.0**: Project foundation and structure
- **0.2.0+**: Incremental feature development (minor version bump per sprint)
- **1.0.0**: Production-ready with complete ITIL functionality

**Production Releases**: Following semantic versioning
- **1.0.0**: Production-ready homelab sysadmin tool
- **1.x.y**: Backward-compatible additions and fixes
- **2.0.0**: Breaking changes (if needed)

### Git Workflow

**Branch Strategy**:
- **main**: Initial development branch (0.1.x versions)
- Development environment is the dogfooding environment
- During development, patch level increases only (0.1.*)
- Bump patch level after successful implementation and testing

### Change Documentation (Keep a Changelog)

**Format**: Follow [keepachangelog.com](https://keepachangelog.com/) format
- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerabilities

### Architecture as Code (C4 DSL)

**Approach**: Use C4 DSL for architecture documentation and validation
- **System Context**: PMS in homelab ecosystem
- **Container View**: Roundup tracker, customizations, integrations
- **Component View**: ITIL modules (issue, change, CMDB)
- **Code View**: Key abstractions and patterns

**Validation Process**:
```bash
# Validate C4 DSL files
podman run --rm -v "$(pwd)/docs/architecture:/usr/local/structurizr" \
  structurizr/cli validate -workspace workspace.dsl

# Visualize architecture
podman run --rm -p 8080:8080 \
  -v "$(pwd)/docs/architecture:/usr/local/structurizr" structurizr/lite
# Then: open http://localhost:8080
```

### Sprint-Based Development Lifecycle

**Approach**: Agile-inspired 2-week sprints

- **Sprint Duration**: 2 weeks with clear deliverables
- **Sprint Planning**: Define goals, user stories, acceptance criteria
- **Sprint Documentation**: Stored in `docs/sprints/`
- **Sprint Review**: Demonstrate functionality, validate requirements
- **Sprint Retrospective**: Continuous improvement

### Documentation Framework (Diátaxis)

**Framework**: Follow [Diátaxis](https://diataxis.fr/) framework

**Four Documentation Types**:

1. **Tutorials** (Learning-oriented): BDD features serve as getting started guides
2. **How-to Guides** (Problem-oriented): Specific task solutions
3. **Reference** (Information-oriented): Roundup API, tracker configuration
4. **Explanation** (Understanding-oriented): ITIL concepts, architecture rationale

**Structure**:
```
docs/
├── tutorials/          # Learning-oriented (BDD-based)
├── howto/             # Problem-oriented
├── reference/         # Information-oriented
├── explanation/       # Understanding-oriented
├── adr/              # Architecture decisions
├── architecture/     # C4 DSL models
└── sprints/          # Sprint planning and tracking
features/
├── issue_tracking/   # Issue management BDD scenarios
├── change_mgmt/      # Change management BDD scenarios
├── cmdb/            # CMDB BDD scenarios
└── step_definitions/ # Behave step implementations
```

### Presentations Framework (Marpit)

**Approach**: Use Marpit for markdown-based presentations
- Presentation source in markdown format
- Topics: BDD introduction, Gherkin syntax, Behave usage, Playwright integration
- Stored alongside documentation for easy maintenance

## Consequences

**Positive:**

- Code Quality: BDD-TDD integration ensures reliable functionality
- Educational Value: Project demonstrates best practices for Python/BDD developers
- Clear Evolution: Semantic versioning provides predictable progression
- Living Documentation: BDD features document system behavior
- Architecture Visibility: C4 DSL provides clear system understanding
- Comprehensive Documentation: Diátaxis serves all user types
- Dogfooding: Development environment is production-like
- Professional Standards: Industry best practices increase adoption

**Negative:**

- Development Overhead: Comprehensive BDD requires more initial effort
- Tool Dependencies: Roundup, Behave, Playwright, Marpit
- Maintenance Commitment: Documentation and tests need ongoing updates
- Learning Curve: Team must understand ITIL, BDD, and Roundup

## Implementation Plan

### Phase 1: Core Practices (Sprint 1)
- Set up Python development environment
- Configure Roundup tracker instance
- Initialize CHANGELOG.md
- Create initial C4 DSL architecture model
- Establish BDD test infrastructure (Behave, Playwright)

### Phase 2: Documentation Framework (Sprint 1-2)
- Establish Diátaxis documentation structure
- Create initial tutorial content based on BDD features
- Set up sprint documentation
- Create initial Marpit presentations

### Phase 3: Process Integration (Ongoing)
- Integrate practices into development workflow
- Document contribution guidelines
- Set up automated validation (pre-commit hooks, CI/CD)

## Validation Criteria

These practices will be validated through:

1. **BDD Coverage**: All user-facing features have Gherkin scenarios
2. **Test Coverage**: Maintain >85% test coverage through TDD
3. **Version Compliance**: Semantic versioning followed in all releases
4. **Change Documentation**: All releases documented in changelog
5. **Architecture Currency**: C4 DSL models updated with implementation
6. **Documentation Completeness**: All four Diátaxis types populated

## Related Decisions

- ADR-0001: Record architecture decisions
- ADR-0003: Use Python with Roundup Issue Tracker toolkit (to be created)
