<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Pasture Management System - AI Assistant Instructions

## Project Overview

The Pasture Management System (PMS) is a dual-objective project:

1. **Functional Tool**: Implement a lightweight ITIL-inspired issue/change/CMDB management system for Homelab Sysadmins, built on Roundup Issue Tracker toolkit
1. **BDD Demonstration**: Demonstrate to Python developers and BDD test writers the usefulness of BDD features, Gherkin, Behave, Playwright testing stack

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

- During development: 0.x.0 versions (minor level bumps per sprint)
- Bump minor version after each sprint completion
- Main branch is the dogfooding/development environment
- Version 1.0.0 will mark production-ready release

### Testing Strategy

- **BDD**: Behave for Gherkin scenarios (primary demonstration objective)
- **TDD**: pytest for unit tests and implementation details
- **Integration**: Test web UI, CLI, and API interfaces
- Coverage target: >85%
- **BDD Best Practices**: See [BDD Testing Best Practices](docs/reference/bdd-testing-best-practices.md) for Behave fixtures, Playwright locators, and test isolation patterns

### Documentation Framework

Following [Diátaxis](https://diataxis.fr/):

- **Tutorials**: BDD feature-based learning guides
- **How-to**: Task-specific solutions
- **Reference**: Technical documentation
- **Explanation**: Architecture and ITIL concepts

## Technology Stack

**Core Platform**:

- Python 3.9+
- Roundup Issue Tracker Toolkit 2.5.0+
  - See [Roundup Development Best Practices](docs/reference/roundup-development-practices.md) for comprehensive development guidance
  - Official documentation: https://www.roundup-tracker.org/docs.html

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

### Roundup Server Management

```bash
# Quick Reset (Recommended) - One command to rule them all
./scripts/reset-test-db.sh                    # Reset DB + restart server (default password: admin)
./scripts/reset-test-db.sh mysecret           # Use custom admin password
./scripts/reset-test-db.sh admin --no-server  # Reset DB only, skip server restart

# Manual Database initialization (for reference)
cd tracker
rm -rf db/*
uv run roundup-admin -i . initialise admin   # admin password provided on command line
cd ..

# Start the Roundup server (foreground - for testing/debugging)
uv run roundup-server -p 9080 pms=tracker

# Start in background (for BDD tests)
uv run roundup-server -p 9080 pms=tracker > /dev/null 2>&1 &

# Stop all Roundup servers
pkill -f "roundup-server"

# Verify server is running
curl -s http://localhost:9080/pms/ | grep -q "Roundup" && echo "Server is running" || echo "Server is not running"

# IMPORTANT: Server Management Best Practices
# 1. Use ./scripts/reset-test-db.sh for complete database resets
# 2. Always use pkill to stop before starting a new instance
# 3. Wait 2 seconds after pkill before starting new server
# 4. Detectors are loaded on server startup - restart after detector changes
# 5. Template changes are cached - restart server to see template updates
# 6. For BDD testing: delete and reinitialize database for clean state

# Complete restart sequence (manual - use reset-test-db.sh instead)
pkill -f "roundup-server" && sleep 2 && uv run roundup-server -p 9080 pms=tracker > /dev/null 2>&1 &

# Troubleshooting: Database corruption (e.g., "table otks already exists")
# This happens when database schema version tracking is out of sync
# Solution: Use the reset script
./scripts/reset-test-db.sh
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

# Generate reports with screenshots
behave --format json --outfile reports/behave-report.json
behave --junit --junit-directory reports/

# Note: Playwright screenshots are captured at 1024x768 resolution
# Web UI is English only
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
1. Implement step definitions (initially failing)
1. Use TDD to implement functionality
1. Verify BDD scenario passes
1. Update documentation as needed
1. Bump version and update CHANGELOG when features complete

### Quality Gates

- All code must pass pre-commit hooks (local validation)
- GitHub Actions CI/CD must pass (mirrors pre-commit checks + extended validation)
- BDD scenarios must pass before completion
- Test coverage must be >85%
- Documentation must be updated for new features
- ADRs required for significant decisions

### CI/CD Strategy

- **Pre-commit hooks**: Fast local validation (\<30s)
- **GitHub Actions**: Extended validation on push/PR
- **Consistency**: Same tools and versions in both environments
- **Principle**: "What passes locally will pass in CI"

### Version Management

- Use semantic versioning (currently 0.1.0)
- Increment minor version for each completed sprint
- Update CHANGELOG.md with each version bump
- Tag releases with `v0.x.0` format

## Sprint Organization

Sprint planning and tracking is maintained in `docs/sprints/`:

- Sprint planning documents define goals and user stories
- Sprint retrospectives capture lessons learned
- Tutorials based on BDD features and sprint deliverables

### Story and Sprint Completion

When completing stories or sprints, follow the procedures documented in:

- **[ADR-0002: Sprint and Story Completion Procedures](docs/adr/0002-adopt-development-best-practices.md#story-completion-procedure)**

**Quick Checklist for Stories**:

- Verify acceptance criteria and BDD scenarios pass
- Update `docs/sprints/sprint-N-backlog.md` status to ✅ Complete
- Commit with format: `feat: implement [description] (Sprint N, Story M)`

**Quick Checklist for Sprints**:

- Create/update sprint backlog (`sprint-N-backlog.md`)
- Write sprint retrospective (`sprint-N-retrospective.md`)
- Update CHANGELOG.md with `## [0.x.0] - YYYY-MM-DD` section
- Update `docs/sprints/README.md` current status
- Bump version (0.x.0 format, x increments per sprint)
- Commit with format: `chore: complete Sprint N wrap-up (v0.x.0)`
- Tag release: `git tag v0.x.0`

See ADR-0002 for complete procedures, document structures, and quality checklists.

## Current Focus

**Version 0.6.0** - Sprint 5 complete:

**Completed Sprints**:

- ✅ Sprint 1 (v0.2.0): Basic issue tracking with Roundup tracker
- ✅ Sprint 2 (v0.3.0): Issue lifecycle and change management foundation
- ✅ Sprint 3 (v0.4.0): Complete change management workflows
- ✅ Sprint 4 (v0.5.0): CMDB BDD specification
- ✅ Sprint 5 (v0.6.0): CMDB implementation (31/41 points, 76%)

**Sprint 5 Results**:

- Core CMDB functionality production-ready:
  - CI schema with 6 types, 7 statuses, 5 criticality levels
  - CI creation workflows (Web UI, CLI, API)
  - CI relationships and circular dependency detection
  - CI-Issue-Change integration
  - CI search, filtering, and CSV export
- Template validation automation (pre-push hooks)
- Comprehensive backlog and retrospective documentation
- Stories 6-7 deferred to Sprint 6 (10 points)

**Next Steps**:

- Sprint 6 planning: Complete deferred stories and begin production polish
- Stories 6-7: Advanced search/sort backends and reporting dashboards
- Address technical debt (BDD test integration, test parallelization)
- Performance optimization and UI/UX polish
- Target: v1.0.0 production release
