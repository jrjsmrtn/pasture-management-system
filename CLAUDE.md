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

### Updating Project Progress Documentation

When completing stories or sprints, update project progress documentation to maintain accurate context for AI collaboration.

#### When to Update

1. **After completing each story**:

   - Update story status in `docs/sprints/sprint-N-backlog.md`
   - Commit story completion

1. **After completing each sprint**:

   - Update all sprint completion files (see sequence below)
   - Update CLAUDE.md "Current Focus" section
   - Bump version and tag release

1. **When starting a new sprint**:

   - Update CLAUDE.md "Current Focus" section with new sprint plan
   - Update `docs/sprints/README.md` current status

#### Files to Update (Sprint Completion Sequence)

Update files in this order for consistency:

1. **`docs/sprints/sprint-N-backlog.md`** - Mark all stories complete with final points
1. **`docs/sprints/sprint-N-retrospective.md`** - Create retrospective document
1. **`CHANGELOG.md`** - Add `## [0.x.0] - YYYY-MM-DD` section with changes
1. **`docs/sprints/README.md`** - Update "Current Status" and version progression
1. **`CLAUDE.md`** - Update "Current Focus" section (see procedure below)
1. **Version files** - Bump version in `pyproject.toml`, `__init__.py`, etc.
1. **Git tag** - Tag release with `git tag v0.x.0`

#### CLAUDE.md "Current Focus" Section Update Procedure

The "Current Focus" section provides AI assistants with current project context. Update it when completing sprints:

**Step 1: Update Section Header**

```markdown
**Version 0.X.0** - Sprint N (Sprint Name):
```

**Step 2: Move Completed Sprint to "Completed Sprints" List**

Add the just-completed sprint to the list with achievements summary:

```markdown
- ✅ Sprint N (v0.X.0): Sprint name (XX/XX points, XX%)
  - Key achievement 1
  - Key achievement 2
  - Key achievement 3
```

**Step 3: Update Current Sprint Plan**

For the NEW sprint, show priorities and point breakdown:

```markdown
**Sprint N+1 Plan** (vX.X.0 Goal - XX-XX points, X days):

**Critical Priority** (XX points):
- Story 1: Description (X points)
- Story 2: Description (X points)

**High Priority** (XX points):
- Story 3: Description (X points)

**Stretch Goals** (XX points):
- Story 4: Description (X points)
```

**Step 4: Update "Next Steps" Section**

Provide immediate next actions:

```markdown
**Next Steps**:

- Begin Sprint N+1 with [first story/task]
- Target: vX.X.0 [release goal] (XX-XX points, X days)
```

#### Example "Current Focus" Section

```markdown
## Current Focus

**Version 0.7.0** - Sprint 7 (Production Release):

**Completed Sprints**:

- ✅ Sprint 1 (v0.2.0): Basic issue tracking with Roundup tracker
- ✅ Sprint 2 (v0.3.0): Issue lifecycle and change management foundation
- ✅ Sprint 6 (v0.7.0): Technical debt resolution & production readiness (30/30 points, 100%)
  - BDD test integration fixed - 91% pass rate
  - Database management automation
  - Core Diátaxis documentation (5 new docs)
  - Test parallelization - 83% improvement

**Sprint 7 Plan** (v1.0.0 Production Release - 26-38 points, 5 days):

**Critical Priority** (16 points):
- Story 1: Installation & deployment guides (5 points)
- Story 2: Security audit & hardening (8 points)

**High Priority** (10 points):
- Story 3: Performance baseline (5 points)

**Next Steps**:

- Begin Sprint 7 with installation & deployment documentation
- Target: v1.0.0 production release (26-38 points, 5 days)
```

#### Quick Reference: Files That Reference Current Sprint/Version

When updating versions, check these files for consistency:

- `CLAUDE.md` - "Current Focus" section
- `docs/sprints/README.md` - "Current Status" section
- `CHANGELOG.md` - Latest version entry
- `pyproject.toml` - `version = "0.x.0"` (line 9)
- `README.md` - Version badges/references (if present)

## Current Focus

**Version 0.7.0** - Sprint 7 (Production Release):

**Completed Sprints**:

- ✅ Sprint 1 (v0.2.0): Basic issue tracking with Roundup tracker
- ✅ Sprint 2 (v0.3.0): Issue lifecycle and change management foundation
- ✅ Sprint 3 (v0.4.0): Complete change management workflows
- ✅ Sprint 4 (v0.5.0): CMDB BDD specification
- ✅ Sprint 5 (v0.6.0): CMDB implementation (31/41 points, 76%)
- ✅ Sprint 6 (v0.7.0): Technical debt resolution & production readiness (30/30 points, 100%)
  - BDD test integration fixed - 91% pass rate (10/11 scenarios)
  - Database management automation - one-command reset script
  - CI search/sort/filter complete with BDD coverage
  - CMDB dashboard with visual statistics
  - Core Diátaxis documentation (5 new docs, 2,850 lines)
  - Test parallelization - 83% performance improvement
  - Technical debt reduced by 85% (21-34 points → 3-5 points)

**Sprint 7 Plan** (v1.0.0 Production Release - 26-38 points, 5 days):

**Critical Priority** (16 points):

- Story 1: Installation & deployment guides (5 points)
- Story 2: Security audit & hardening (8 points)
- Story 3: CONTRIBUTING.md & release documentation (3 points)

**High Priority** (10 points):

- Story 4: CSV export BDD test fix (2 points)
- Story 5: Performance baseline & optimization (5 points)
- Story 6: SLSA provenance implementation (3 points)

**Stretch Goals** (12 points):

- Story 7: BDD demonstration materials (5 points)
- Story 8: UI/UX polish (5 points)
- Story 9: Template helper integration tests (2 points)

**Next Steps**:

- Begin Sprint 7 with installation & deployment documentation
- Target: v1.0.0 production release (26-38 points, 5 days)
