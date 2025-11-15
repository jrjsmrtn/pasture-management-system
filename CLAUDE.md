# Pasture Management System - AI Assistant Instructions

## Project Overview

The Pasture Management System (PMS) is a dual-objective project:

1. **Functional Tool**: Implement a lightweight ITIL-inspired issue/change/CMDB management system for Homelab Sysadmins, built on Roundup Issue Tracker toolkit
2. **BDD Demonstration**: Demonstrate to Python developers and BDD test writers the usefulness of BDD features, Gherkin, Behave, Playwright testing stack

## Architecture Documentation

This project uses Architecture Decision Records (ADRs) to track significant architectural decisions:

- **[ADR-0001](docs/adr/0001-record-architecture-decisions.md)**: Record architecture decisions
- **[ADR-0002](docs/adr/0002-adopt-development-best-practices.md)**: Adopt development best practices
- **[ADR-0003](docs/adr/0003-use-python-with-roundup-issue-tracker.md)**: Use Python with Roundup Issue Tracker Toolkit

See the [docs/adr/](docs/adr/) directory for complete decision history.

## Key Development Practices

### BDD-First Development
- Write Gherkin feature files BEFORE implementation
- Features serve as tutorials and living documentation
- Test across three interfaces: Web UI (Playwright), CLI, API
- Generate JUnit XML reports with screenshots

### Semantic Versioning
- During development: 0.1.x versions (patch level only)
- Bump patch level after successful implementation and testing
- Main branch is the dogfooding/development environment
- Version 1.0.0 will mark production-ready release

### Testing Strategy
- **BDD**: Behave for Gherkin scenarios (primary demonstration objective)
- **TDD**: pytest for unit tests and implementation details
- **Integration**: Test web UI, CLI, and API interfaces
- Coverage target: >85%

### Documentation Framework
Following [Diátaxis](https://diataxis.fr/):
- **Tutorials**: BDD feature-based learning guides
- **How-to**: Task-specific solutions
- **Reference**: Technical documentation
- **Explanation**: Architecture and ITIL concepts

## Technology Stack

**Core Platform**:
- Python 3.9+
- Roundup Issue Tracker Toolkit

**BDD/Testing**:
- Behave (Gherkin scenarios)
- Playwright (web UI automation)
- pytest (unit tests)

**Code Quality**:
- ruff (formatting and linting)
- mypy (type checking)

**Additional**:
- Marpit (markdown presentations)
- C4 DSL (architecture as code)
- Pre-commit hooks (quality automation)

## Development Commands

### Environment Setup
```bash
# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install
pre-commit install --hook-type pre-push
```

### Code Quality
```bash
# Format and lint with ruff
ruff format .
ruff check .
ruff check --fix .

# Type checking
mypy .

# Pre-commit checks
pre-commit run --all-files
```

### BDD Testing
```bash
# Run all BDD scenarios
behave

# Run specific tags
behave --tags=@smoke
behave --tags=@web-ui
behave --tags=@cli
behave --tags=@api

# Generate reports
behave --format json --outfile reports/behave-report.json
behave --junit --junit-directory reports/
```

### Architecture Validation
```bash
# Validate C4 DSL model
podman run --rm -v "$(pwd)/docs/architecture:/usr/local/structurizr" \
  structurizr/cli validate -workspace workspace.dsl

# Visualize architecture
podman run --rm -p 8080:8080 \
  -v "$(pwd)/docs/architecture:/usr/local/structurizr" structurizr/lite
# Then: open http://localhost:8080
```

## Project Structure

```
pasture-management-system/
├── docs/                   # Diátaxis documentation
│   ├── adr/               # Architecture Decision Records
│   ├── tutorials/         # Learning-oriented guides
│   ├── howto/             # Task-oriented guides
│   ├── reference/         # Technical reference
│   ├── explanation/       # Conceptual understanding
│   ├── architecture/      # C4 DSL models
│   └── sprints/           # Sprint planning and tracking
├── features/              # BDD Gherkin scenarios
│   ├── issue_tracking/
│   ├── change_mgmt/
│   ├── cmdb/
│   └── step_definitions/
├── tests/                 # Unit and integration tests
├── tracker_data/          # Roundup tracker instance
├── customizations/        # ITIL workflow customizations
│   ├── schema/
│   ├── detectors/
│   └── templates/
├── .editorconfig          # Consistent formatting
├── .gitignore            # Python + macOS patterns
├── .pre-commit-config.yaml # Quality automation
├── CHANGELOG.md          # Version history
├── CLAUDE.md             # This file
└── README.md             # Project overview
```

## AI-Assisted Development Notes

### Context for AI Collaboration
- ADRs provide decision history and rationale
- Sprint documentation maintains development continuity
- BDD features define expected behavior
- C4 DSL models provide architecture context
- This is both a functional tool AND an educational demonstration

### Development Workflow
1. Write BDD feature file (Gherkin scenario)
2. Implement step definitions (initially failing)
3. Use TDD to implement functionality
4. Verify BDD scenario passes
5. Update documentation as needed
6. Bump version and update CHANGELOG when features complete

### Quality Gates
- All code must pass pre-commit hooks
- BDD scenarios must pass before completion
- Test coverage must be >85%
- Documentation must be updated for new features
- ADRs required for significant decisions

### Version Management
- Use semantic versioning (currently 0.1.x)
- Increment patch version for completed features
- Update CHANGELOG.md with each version bump
- Tag releases with `v0.1.x` format

## Sprint Organization

Sprint planning and tracking is maintained in `docs/sprints/`:
- Sprint planning documents define goals and user stories
- Sprint retrospectives capture lessons learned
- Tutorials based on BDD features and sprint deliverables

## Current Focus

**Version 0.1.0** - Project foundation established with:
- Directory structure
- Foundational ADRs
- Development tooling configuration
- Documentation framework

Next steps will involve setting up Roundup tracker and implementing first ITIL workflows with BDD scenarios.
