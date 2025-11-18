<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# ADR-0002: Adopt Development Best Practices

Date: 2025-11-15

## Status

Accepted

## Context

The Pasture Management System has dual objectives:

1. Implement a lightweight ITIL-inspired issue/change/CMDB management system for Homelab Sysadmins on Roundup Issue Tracker
1. Demonstrate to Python developers and BDD test writers the usefulness of BDD features, Gherkin, Behave, Playwright testing stack

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

#### Behave Best Practices

Following official Behave documentation patterns for test infrastructure:

**Fixtures and Test Isolation**:

- **Use `use_fixture()` pattern**: Provides automatic cleanup via generator functions with `yield`
- **Generator pattern for fixtures**: Separate setup (before yield) and cleanup (after yield)
- **Cleanup is guaranteed**: Runs even on test failures
- **Fixture execution order**: Test run → Feature → Scenario (cleanup in reverse order)

**Test Isolation Strategy**:

- **Clean state per scenario**: Each scenario starts with fresh database and environment
- **Proper separation**: Fixtures for technical infrastructure (DB, server, browser), Background for business context (test data, preconditions)
- **Screenshot cleanup**: Clean screenshots directory before each scenario to prevent accumulation
- **Environment hooks**: `before_scenario()` for setup, `after_scenario()` for optional tasks (fixtures handle cleanup)

**Background Usage**:

- **Keep it brief**: Recommended ~4 lines maximum for readability
- **Business-focused**: Background is for business context users need to understand, not technical setup
- **Descriptive language**: Use vivid, story-like descriptions rather than technical details
- **Runs after hooks**: Background steps execute after `before_scenario()` but before scenario steps

**Practical Implementation**:

```python
# features/environment.py

from behave import fixture, use_fixture

@fixture
def clean_database(context):
    """Setup database - generator pattern ensures cleanup."""
    # Setup
    cleanup_database()
    initialize_fresh_database()

    yield context  # Scenario runs here

    # Cleanup (guaranteed to run)
    stop_server()
    cleanup_database()

def before_scenario(context, scenario):
    """Use fixtures for automatic cleanup."""
    use_fixture(clean_database, context)  # Registers cleanup automatically
    context.test_data = {}
```

**Key Benefits**:

- Eliminates manual cleanup code scattered across test files
- Cleanup happens in correct order (reverse of setup)
- Test failures don't leave dirty state
- Clear separation between infrastructure and business logic

#### Playwright Best Practices for BDD Testing

**Reference:** [Playwright Python Documentation](https://playwright.dev/python/docs/intro)

This project uses Playwright for web UI automation in BDD scenarios. Following Playwright's official best practices ensures resilient, maintainable tests.

**Core Philosophy**: Playwright tests perform actions and assert expectations, with automatic waiting eliminating manual timeouts.

**Locator Strategy (Priority Order)**:

Playwright recommends user-facing locators that reflect how users perceive interfaces:

1. **Role-based locators** (best) - `page.get_by_role("button", name="Submit")`
1. **Text locators** - `page.get_by_text("Configuration Items")`
1. **Label locators** - `page.get_by_label("Name")`
1. **Placeholder/Alt/Title** - `page.get_by_placeholder("Search...")`
1. **Test ID locators** - `page.get_by_test_id("ci-list")` when user-facing options fail
1. **CSS/XPath** (last resort) - Brittle and fragile

**Anti-Pattern to Avoid**:

```python
# ❌ AVOID - Complex, brittle selectors
page.locator("#tsf > div:nth-child(2) > div.A8SBwf > div.RNNXgb...")

# ✅ PREFER - User-facing locators
page.get_by_role("searchbox", name="Search")
```

**Auto-Waiting Behavior**:

Playwright automatically waits for actionability checks before performing actions. **Do not use manual waits** unless absolutely necessary:

```python
# ❌ AVOID - Explicit waits
context.page.wait_for_timeout(500)  # Manual wait

# ✅ PREFER - Rely on auto-waiting
context.page.click('button[type="submit"]')  # Waits automatically
```

**Current Pattern** (our codebase uses some manual waits - consider reviewing):

- `features/steps/ci_search_steps.py` uses `wait_for_timeout(500)` after searches
- Evaluate if these are necessary or if Playwright's auto-waiting is sufficient

**Web-First Assertions with expect()**:

Use Playwright's `expect()` API for resilient assertions that retry until conditions are met:

```python
from playwright.sync_api import expect

# Web-first assertions (retry until timeout)
expect(page).to_have_title(re.compile("Roundup"))
expect(page.locator("table.list tbody tr")).to_have_count(5)
expect(page.get_by_role("alert")).to_be_visible()
expect(page.get_by_text("CI created")).to_contain_text("successfully")
```

**Current Pattern** (our codebase uses assert statements - consider migrating):

```python
# Current approach
assert actual_count == count, f"Expected {count} CIs"

# Recommended approach with web-first assertions
expect(page.locator("table.list tbody tr")).to_have_count(count)
```

**Test Isolation via Browser Context**:

Each Behave scenario should receive a fresh browser context for isolation. Our implementation follows this pattern:

```python
# features/environment.py
@fixture
def browser_context(context):
    """Create isolated browser context per scenario."""
    context.context = context.browser.new_context(**get_context_options())
    context.page = context.context.new_page()

    yield context.context

    # Cleanup
    context.page.close()
    context.context.close()
```

**Benefits**:

- Each scenario starts with clean cookies, local storage, and session
- Tests don't interfere with each other
- Similar to opening a new incognito window

**Locator Filtering and Chaining**:

Use filtering and chaining to narrow down elements:

```python
# Filter by text content
page.get_by_role("listitem").filter(has_text="Active").get_by_role("button").click()

# Chain locators for scoped searches
dialog = page.get_by_test_id("settings-dialog")
dialog.locator("input[name='name']").fill("web-server-01")
```

**Strictness Principle**:

Operations fail if multiple elements match. Use `.first`, `.last`, or `.nth()` only when necessary:

```python
# ❌ AVOID - Fragile when DOM changes
page.locator("button").first.click()

# ✅ PREFER - Specific selector
page.get_by_role("button", name="Submit").click()
```

**Screenshot and Debugging**:

Our implementation captures screenshots on test failures (configured in `features/environment.py`):

```python
def after_step(context, step):
    if step.status == "failed":
        screenshot_path = SCREENSHOT_DIR / f"{context.scenario_name}_{step.name}_FAILED.png"
        context.page.screenshot(path=str(screenshot_path), full_page=False)
```

**Best Practice**: Use viewport screenshots (`full_page=False`) for faster capture and smaller files.

**Debugging Tips**:

- Set `HEADLESS=false` environment variable to see browser UI
- Use `page.pause()` to inspect page state interactively
- Enable slow motion: `browser.launch(slow_mo=1000)` to observe actions
- Check console logs: `page.on("console", lambda msg: print(msg.text))`

**Performance Considerations**:

Our configuration uses reduced timeouts for small databases (configured in `tests/config/playwright_config.py`):

```python
TIMEOUTS = {
    "default": 10000,      # 10 seconds (reduced from 30s)
    "navigation": 5000,    # 5 seconds for page loads
    "action": 3000,        # 3 seconds for actions
}
```

**Integration with Behave**:

Our implementation integrates Playwright with Behave fixtures:

1. **Session-scoped browser**: Shared across scenarios (`before_all()`)
1. **Scenario-scoped context**: Fresh context per scenario (`before_scenario()`)
1. **Automatic cleanup**: Context/page closed via fixture pattern
1. **Tag-based activation**: Browser setup only for `@web-ui` scenarios

**BDD Step Definition Best Practices**:

```python
# features/steps/ci_steps.py
from playwright.sync_api import expect

@when('I navigate to the CI creation page')
def step_navigate_to_ci_creation(context):
    # Good: Clear, user-focused action
    context.page.goto(f"{context.base_url}/ci?@template=item")

@then('I should see {count:d} CIs in the results')
def step_verify_ci_count(context, count):
    # Consider migrating to web-first assertions
    ci_rows = context.page.locator("table.list tbody tr")
    expect(ci_rows).to_have_count(count)
```

**Migration Recommendations**:

1. **Review manual waits**: Evaluate `wait_for_timeout()` calls - many can be removed
1. **Adopt web-first assertions**: Migrate from `assert` to `expect()` for retrying behavior
1. **Improve locators**: Replace CSS selectors with role-based or text-based locators where possible
1. **Reduce timeouts**: Current 30s default is generous; 10s may be sufficient for small databases

**References**:

- [Playwright Python Docs](https://playwright.dev/python/docs/intro)
- [Locator Best Practices](https://playwright.dev/python/docs/locators)
- [Writing Tests](https://playwright.dev/python/docs/writing-tests)
- Project implementation: `features/environment.py`, `tests/config/playwright_config.py`

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
- During development, patch level increases only (0.1.\*)
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

#### Story Completion Procedure

When a user story is completed, follow these steps:

1. **Verify Acceptance Criteria**

   - All acceptance criteria from the story planning document must be met
   - All BDD scenarios for the story must pass
   - Code passes all quality gates (pre-commit hooks, pre-push hooks)

1. **Update Sprint Backlog**

   - Mark story status as ✅ Complete in `docs/sprints/sprint-N-backlog.md`
   - Update BDD scenario count and status (e.g., "7 scenarios - **ALL PASSING** ✅")
   - Add completion timestamp if relevant
   - Update story points summary (completed/in-progress/remaining)

1. **Commit the Story**

   - Use commit message format: `feat: implement [story description] (Sprint N, Story M)`
   - Example: `feat: implement CI search and filtering (Sprint 4, Story 5)`
   - Ensure commit includes all related code, tests, and documentation

#### Sprint Completion Procedure

When all user stories in a sprint are completed, follow this wrap-up process:

1. **Create/Update Sprint Backlog** (`docs/sprints/sprint-N-backlog.md`)

   - If it doesn't exist, create it following the Sprint Backlog Document Structure below
   - Mark sprint status as: **Status**: ✅ Complete
   - Update story points summary showing all points completed
   - Mark all stories and tasks as ✅ Complete with BDD scenario counts
   - Add actual start/end dates and duration

1. **Create Sprint Retrospective** (`docs/sprints/sprint-N-retrospective.md`)

   - Follow the Sprint Retrospective Document Structure below
   - Include comprehensive analysis of sprint performance
   - Document lessons learned and action items
   - Include retrospective completion date and version released

1. **Update CHANGELOG.md**

   - Add a new version section: `## [0.x.0] - YYYY-MM-DD`
   - Document all features added in the sprint under `### Added`
   - Include comprehensive details:
     - Story descriptions with acceptance criteria highlights
     - BDD scenario counts (total and by story)
     - Documentation deliverables with line counts
     - Technical details (story points, coverage stats, new files)
   - Add any changes under `### Changed`
   - Document fixes under `### Fixed`
   - Include Technical Details subsection summarizing metrics
   - Update version links at bottom of CHANGELOG.md

1. **Update Sprint Overview** (`docs/sprints/README.md`)

   - Update "Current Status" section (bottom of file)
   - Change from current version to new version
   - Update "Next Sprint" to the upcoming sprint
   - Keep the status concise and accurate

1. **Bump Version**

   - Update version number in relevant files (if applicable)
   - Version format: 0.x.0 where x increments per sprint
   - Sprint 1 → v0.2.0, Sprint 2 → v0.3.0, Sprint 3 → v0.4.0, etc.

1. **Create Sprint Wrap-up Commit**

   - Commit message format: `chore: complete Sprint N wrap-up (v0.x.0)`
   - Example: `chore: complete Sprint 3 wrap-up (v0.4.0)`
   - Include all documentation updates in this commit:
     - CHANGELOG.md updates
     - Sprint backlog completion
     - Sprint retrospective
     - docs/sprints/README.md update

1. **Tag Release**

   - Create git tag: `git tag v0.x.0`
   - Push tag: `git push [remote] v0.x.0`
   - Tag message should reference the sprint: "Sprint N Complete: [brief description]"

#### Sprint Backlog Document Structure

Sprint backlog files should follow this structure (see `sprint-1-backlog.md` and `sprint-2-backlog.md` as examples):

- **Header**: Sprint number, target version, status, dates
- **Sprint Goal**: One-sentence goal statement
- **Story Points Summary**: Total/completed/in-progress/remaining
- **Backlog Items**: Organized by epic/story
  - Each story includes: story points, priority, status, user story text
  - Acceptance criteria as checklist
  - BDD scenario count and status
  - Dependencies and technical notes
- **Technical Tasks**: Implementation-level tasks
- **Definition of Done**: Sprint-level checklist

#### Sprint Retrospective Document Structure

Sprint retrospective files should follow this structure (see `sprint-3-retrospective.md` as the gold standard):

- **Header**: Duration, goal, completion date, version
- **Sprint Summary**: Narrative summary with key metrics table
- **Sprint Backlog Completion**: Table showing all stories with points, status, scenarios, LOC
- **What Went Well**: 3-6 successes with evidence and impact
- **What Could Be Improved**: 2-4 challenges with root cause and solutions
- **Key Learnings**: 3-6 lessons learned with evidence
- **Action Items for Next Sprint**: Categorized action items
- **Sprint Highlights**: Most valuable deliverable, best innovation, impressive stats
- **Velocity and Capacity Analysis**: Trends and recommendations
- **Definition of Done Check**: Final checklist status
- **Looking Ahead**: Potential focus areas for next sprint
- **Final Thoughts**: Overall assessment with rating

#### Quality Checklist for Sprint Completion

Before considering a sprint complete, verify:

- [ ] All user stories marked complete in sprint backlog
- [ ] All BDD scenarios passing
- [ ] All documentation deliverables completed
- [ ] Sprint backlog document created/updated
- [ ] Sprint retrospective written
- [ ] CHANGELOG.md updated with new version
- [ ] docs/sprints/README.md current status updated
- [ ] Version bumped appropriately
- [ ] Sprint wrap-up commit created
- [ ] Git tag created for release
- [ ] All commits follow commit message conventions
- [ ] Pre-commit and pre-push hooks pass

#### Commit Message Conventions

- **Story completion**: `feat: implement [story description] (Sprint N, Story M)`
- **Sprint wrap-up**: `chore: complete Sprint N wrap-up (v0.x.0)`
- **Documentation**: `docs: add [document type] for [topic]`
- **Bug fixes**: `fix: [description]`
- **Refactoring**: `refactor: [description]`

### Documentation Framework (Diátaxis)

**Framework**: Follow [Diátaxis](https://diataxis.fr/) framework

**Four Documentation Types**:

1. **Tutorials** (Learning-oriented): BDD features serve as getting started guides
1. **How-to Guides** (Problem-oriented): Specific task solutions
1. **Reference** (Information-oriented): Roundup API, tracker configuration
1. **Explanation** (Understanding-oriented): ITIL concepts, architecture rationale

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

### CI/CD and Quality Automation

**Approach**: Multi-layered quality automation starting with pre-commit hooks, extended to GitHub Actions

#### Pre-commit Hooks (Local Development)

- **Fast feedback**: \<30 seconds execution time
- **Security-first**: Credential detection, secret scanning (gitleaks)
- **Code quality**: ruff formatting and linting
- **Type checking**: mypy (pre-push stage)
- **Multi-stage**: Fast checks on commit, comprehensive on push

#### GitHub Actions CI/CD

- **Consistency**: Mirror pre-commit hook checks for reliability
- **Extended validation**: Full test suite, cross-platform testing
- **Automated reporting**: Test coverage, BDD scenario results with screenshots
- **Security scanning**: Dependency vulnerability checks
- **Build validation**: Ensure deployability

**Consistency Strategy**:

- Pre-commit hooks define the baseline quality gates
- GitHub Actions run identical checks plus extended validation
- Same tool versions in both environments (pinned in configs)
- Failures in either environment block progression
- This ensures "what passes locally will pass in CI"

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
- CI/CD Consistency: Pre-commit and GitHub Actions alignment prevents surprises
- Fast Feedback: Local validation catches issues before push

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
- Configure GitHub Actions workflows mirroring pre-commit checks
- Establish CI/CD pipeline for automated testing and deployment

## Validation Criteria

These practices will be validated through:

1. **BDD Coverage**: All user-facing features have Gherkin scenarios
1. **Test Coverage**: Maintain >85% test coverage through TDD
1. **Version Compliance**: Semantic versioning followed in all releases
1. **Change Documentation**: All releases documented in changelog
1. **Architecture Currency**: C4 DSL models updated with implementation
1. **Documentation Completeness**: All four Diátaxis types populated
1. **CI/CD Consistency**: Pre-commit hooks and GitHub Actions produce identical results
1. **Quality Gate Performance**: Pre-commit checks complete in \<30 seconds

## Related Decisions

- ADR-0001: Record architecture decisions
- ADR-0003: Use Python with Roundup Issue Tracker toolkit (to be created)
