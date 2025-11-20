<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Contributing to Pasture Management System

Thank you for your interest in contributing to the Pasture Management System (PMS)! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [How to Contribute](#how-to-contribute)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Pull Request Process](#pull-request-process)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)
- [Commit Message Conventions](#commit-message-conventions)
- [License](#license)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

### Project Overview

PMS has dual objectives:

1. **Functional Tool**: Lightweight ITIL-inspired issue/change/CMDB management system for Homelab Sysadmins
1. **BDD Demonstration**: Showcase modern BDD testing with Python, Gherkin, Behave, and Playwright

### Key Resources

- **[Installation Guide](docs/howto/installation-guide.md)**: Set up development environment
- **[Architecture Overview](docs/explanation/architecture-overview.md)**: System architecture and design
- **[ADRs](docs/adr/)**: Architectural Decision Records
- **[BDD Testing Best Practices](docs/reference/bdd-testing-best-practices.md)**: BDD development guide
- **[Roundup Development Practices](docs/reference/roundup-development-practices.md)**: Roundup-specific guidance

## Development Environment Setup

### Prerequisites

- **Python 3.9+**
- **uv** (recommended) or **pip** for package management
- **Git** for version control
- **Playwright** browsers for testing

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/pasture-management-system.git
cd pasture-management-system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Install development dependencies
uv pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium

# Install pre-commit hooks
pre-commit install
pre-commit install --hook-type pre-push

# Initialize database and start server
./scripts/reset-test-db.sh admin

# Verify installation
curl -s http://localhost:9080/pms/ | grep -q "Roundup" && echo "Success!"
```

For detailed instructions, see the [Installation Guide](docs/howto/installation-guide.md).

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **Bug Reports**: Identify and report issues
- **Feature Requests**: Suggest new functionality
- **Bug Fixes**: Submit fixes for identified issues
- **New Features**: Implement new capabilities
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage
- **BDD Examples**: Contribute Gherkin scenarios demonstrating BDD patterns

### Contribution Workflow

1. **Fork the repository** on GitHub
1. **Clone your fork** locally
1. **Create a feature branch**: `git checkout -b feature/my-feature`
1. **Make your changes** following our guidelines
1. **Add tests** for your changes (BDD scenarios and/or unit tests)
1. **Run tests locally** to ensure they pass
1. **Commit your changes** following our commit conventions
1. **Push to your fork**: `git push origin feature/my-feature`
1. **Create a Pull Request** from your fork to our `main` branch

## Reporting Bugs

### Before Reporting

1. **Check existing issues** to avoid duplicates
1. **Verify it's a bug** and not expected behavior
1. **Test with the latest version** to see if it's already fixed

### How to Report

Use our [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md) and include:

- **Clear title**: Concise description of the issue
- **Environment**: OS, Python version, PMS version
- **Steps to reproduce**: Detailed steps to trigger the bug
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Screenshots**: If applicable
- **Logs**: Relevant error messages or logs

**Example**:

```
Title: Database corruption on concurrent writes

Environment:
- OS: Ubuntu 22.04
- Python: 3.11.2
- PMS Version: 0.7.0

Steps to reproduce:
1. Start PMS server
2. Create two issues simultaneously from different browsers
3. Observe database error

Expected: Both issues created successfully
Actual: Database locked error on second issue

Logs:
database is locked (tracker/db/issue.db)
```

## Suggesting Features

### Before Suggesting

1. **Check existing feature requests** to avoid duplicates
1. **Review the roadmap** (docs/sprints/) to see if it's planned
1. **Consider scope**: Does this align with PMS objectives?

### How to Suggest

Use our [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md) and include:

- **Clear title**: Concise feature description
- **User story**: "As a [role], I want [feature] so that [benefit]"
- **Problem statement**: What problem does this solve?
- **Proposed solution**: How should it work?
- **Alternatives considered**: Other approaches you've thought about
- **ITIL alignment**: How does this relate to ITIL practices? (if applicable)
- **BDD scenario**: Sample Gherkin scenario demonstrating the feature

**Example**:

```
Title: Add email notifications for issue assignments

User Story:
As a sysadmin, I want email notifications when issues are assigned to me
so that I can respond quickly without constantly checking the web UI.

Problem:
Currently, users must manually check for new assignments, leading to
delayed responses and missed SLA targets.

Proposed Solution:
Implement Roundup's email gateway integration to send notifications on
issue assignment, with configurable notification preferences.

BDD Scenario:
Given I am a user with email notifications enabled
When an issue is assigned to me
Then I should receive an email notification
And the email should contain issue details and a link
```

## Pull Request Process

### Before Submitting

1. **Update from main**: Rebase your branch on latest main
1. **Run all tests**: Ensure BDD scenarios and unit tests pass
1. **Run pre-commit hooks**: `pre-commit run --all-files`
1. **Update documentation**: If you've changed APIs or added features
1. **Add BDD scenarios**: For new user-facing features
1. **Update CHANGELOG.md**: Add entry under "Unreleased" section

### PR Requirements

- ✅ **All tests pass** (BDD + unit tests)
- ✅ **Pre-commit hooks pass** (ruff, mypy, mdformat, etc.)
- ✅ **Code coverage maintained** (>85%)
- ✅ **Documentation updated** (if applicable)
- ✅ **BDD scenarios added** (for new features)
- ✅ **Conventional commit messages** (see below)
- ✅ **No merge conflicts** with main branch

### PR Description

Use our [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md) and include:

- **Summary**: What does this PR do?
- **Related Issues**: Link to issue(s) this PR addresses
- **Type of Change**: Bug fix, feature, documentation, etc.
- **Testing**: How was this tested?
- **BDD Scenarios**: New or updated scenarios (if applicable)
- **Breaking Changes**: Any backward-incompatible changes?
- **Checklist**: Confirm all requirements met

### Review Process

1. **Automated checks**: CI/CD must pass (GitHub Actions)
1. **Code review**: At least one maintainer approval required
1. **Testing**: Reviewers may test locally
1. **Discussion**: Address reviewer feedback
1. **Approval**: Maintainer approves and merges

## Code Style Guidelines

We use automated tools to enforce code style.

### Python Code Style

**Tools**:

- **ruff**: Formatting and linting (replaces black, isort, flake8)
- **mypy**: Type checking

**Rules**:

- **Line length**: 100 characters
- **Formatting**: ruff format (PEP 8 compliant)
- **Linting**: ruff check (E, W, F, I, N, UP rule sets)
- **Type hints**: Encouraged but not required (mypy configured for gradual typing)
- **Docstrings**: Required for public APIs (Google style)
- **Imports**: Sorted by ruff (isort-compatible)

**Running locally**:

```bash
# Format code
ruff format .

# Check linting
ruff check .

# Auto-fix issues
ruff check --fix .

# Type checking
mypy .
```

### Roundup Code

**Special Considerations**:

- Roundup detector templates and schema are excluded from linting
- Follow existing Roundup patterns for detectors and extensions
- See [Roundup Development Practices](docs/reference/roundup-development-practices.md)

### Configuration Files

- **YAML**: Validated with yamllint
- **Markdown**: Formatted with mdformat
- **TOML**: Consistent formatting in pyproject.toml

## Testing Requirements

### BDD Testing (Primary)

**This project emphasizes BDD as a core objective.**

#### When to Write BDD Scenarios

BDD scenarios are required for:

- ✅ **User-facing features** (web UI, CLI, API)
- ✅ **Workflows** (issue lifecycle, change management)
- ✅ **Business logic** (ITIL processes, approvals)
- ✅ **Multi-step interactions** (create issue → assign → resolve)

#### BDD Best Practices

- **Write scenarios before implementation** (BDD-first approach)
- **Use Given-When-Then format** consistently
- **One scenario per user goal** (not implementation detail)
- **Use Background** for common setup
- **Tag appropriately**: `@web-ui`, `@cli`, `@api`, `@smoke`, `@slow`
- **Test across interfaces**: Web UI (Playwright), CLI, and API

**Example BDD Scenario**:

```gherkin
Feature: Issue Assignment
  As a team lead
  I want to assign issues to team members
  So that work is distributed effectively

  @web-ui @smoke
  Scenario: Assign issue to user via web UI
    Given I am logged in as admin
    And an issue "Server down" exists
    When I navigate to the issue
    And I assign it to user "jsmith"
    Then the issue should show assignee "John Smith"
    And user "jsmith" should see the issue in their queue
```

For comprehensive BDD guidance, see [BDD Testing Best Practices](docs/reference/bdd-testing-best-practices.md).

### Unit Testing (Implementation Details)

Use pytest for:

- ✅ **Template helpers** (pure functions, data transformations)
- ✅ **Utilities** (parsing, formatting, validation)
- ✅ **Edge cases** (boundary conditions, error handling)
- ✅ **Non-user-facing logic** (internal APIs, data structures)

**Example Unit Test**:

```python
def test_sort_ci_ids_ascending():
    """Test sorting CI IDs in ascending order."""
    ci_ids = [mock_ci("zebra"), mock_ci("alpha"), mock_ci("beta")]
    result = sort_ci_ids(ci_ids, "name", "asc")
    assert [ci.name for ci in result] == ["alpha", "beta", "zebra"]
```

### Running Tests

```bash
# Run all BDD scenarios
behave

# Run specific tags
behave --tags=@smoke        # Smoke tests only
behave --tags=@web-ui       # Web UI tests only
behave --tags="@smoke and @web-ui"  # Combined

# Run with parallel execution
behave --processes 4 --parallel-element scenario

# Generate reports
behave --junit --junit-directory reports/

# Run unit tests
pytest

# Run with coverage
pytest --cov=features/steps --cov-report=html

# Run specific test
pytest tests/test_template_helpers.py::test_sort_ci_ids
```

### Coverage Requirements

- **Overall coverage**: >85%
- **New features**: 100% coverage for new code
- **BDD scenarios**: All user-facing features must have scenarios

## Documentation Standards

We follow the [Diátaxis](https://diataxis.fr/) documentation framework.

### Documentation Types

1. **Tutorials** (`docs/tutorials/`): Learning-oriented, step-by-step guides
1. **How-to Guides** (`docs/howto/`): Task-oriented, problem-solving recipes
1. **Reference** (`docs/reference/`): Information-oriented, technical specifications
1. **Explanation** (`docs/explanation/`): Understanding-oriented, conceptual discussion

### Writing Guidelines

- **Clear titles**: Descriptive, specific titles
- **Target audience**: Specify who the document is for
- **Purpose statement**: One sentence explaining the document's goal
- **Estimated time**: For tutorials and how-to guides
- **Cross-references**: Link to related documentation
- **Examples**: Include practical examples
- **SPDX headers**: All files include license headers
- **Markdown formatting**: Use mdformat for consistent formatting

### Documentation Checklist

- [ ] Correct Diátaxis category
- [ ] SPDX license header
- [ ] Clear audience and purpose
- [ ] Cross-references to related docs
- [ ] Practical examples
- [ ] Tested procedures (for tutorials and how-tos)
- [ ] mdformat compliant

## Commit Message Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/) for clear, semantic commit history.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **test**: Test additions or modifications
- **refactor**: Code refactoring (no functional changes)
- **perf**: Performance improvements
- **chore**: Build process, dependencies, tooling
- **ci**: CI/CD configuration changes

### Scope (Optional)

- **web-ui**: Web interface changes
- **cli**: Command-line interface
- **api**: API changes
- **cmdb**: CMDB-specific changes
- **bdd**: BDD testing changes

### Subject

- **Imperative mood**: "add" not "added" or "adds"
- **Lowercase**: Start with lowercase
- **No period**: Don't end with a period
- **50 characters max**: Keep it concise

### Body (Optional)

- **Explain what and why**, not how
- **Wrap at 72 characters**
- **Reference issues**: "Fixes #123", "Closes #456"

### Footer

For project contributions, include:

```
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Examples

**Feature commit**:

```
feat(cmdb): add CI relationship visualization

Implement graph-based visualization of CI relationships using D3.js.
Displays parent-child and dependency relationships with interactive
navigation.

Closes #234
```

**Bug fix commit**:

```
fix(web-ui): resolve database locking on concurrent issue creation

SQLite database was locking under concurrent writes. Enabled WAL mode
and adjusted retry logic to handle busy conditions gracefully.

Fixes #567
```

**Documentation commit**:

```
docs: create installation and deployment guides

Add comprehensive production deployment documentation:
- Installation guide with three installation methods
- Deployment guide with reverse proxy and SSL setup
- Administration guide with maintenance procedures

Total: 1,850 lines of production-ready documentation
```

## License

By contributing to PMS, you agree that your contributions will be licensed under the [MIT License](LICENSE).

All source files must include SPDX license headers:

```
<!--
SPDX-FileCopyrightText: 2025 Your Name <your.email@example.com>
SPDX-License-Identifier: MIT
-->
```

## Questions?

- **GitHub Discussions**: [Ask questions](https://github.com/yourusername/pasture-management-system/discussions)
- **GitHub Issues**: [Report bugs or request features](https://github.com/yourusername/pasture-management-system/issues)
- **Documentation**: [Browse our docs](docs/)

______________________________________________________________________

**Thank you for contributing to the Pasture Management System!**

We appreciate your time and effort in making PMS better for the homelab community and advancing BDD education for Python developers.
