<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Changelog

All notable changes to the Pasture Management System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-11-15

### Added
- **Roundup Tracker Integration**: Complete issue tracking system with Web UI, CLI, and REST API
  - Roundup 2.4.0 with classic template
  - SQLite database backend
  - Admin user authentication
- **Web UI Issue Creation**: Create and view issues through responsive web interface
  - Issue creation form with title and priority fields
  - Issue list view with sorting
  - Issue detail view
  - Form validation (required title field)
- **CLI Issue Creation**: Command-line issue management via roundup-admin
  - Create issues with `roundup-admin create issue` command
  - Priority mapping (critical, urgent, bug, feature, wish)
  - Database verification commands
- **REST API Issue Creation**: Full REST API for automation and integration
  - POST endpoint: `/rest/data/issue`
  - HTTP Basic Authentication
  - CSRF protection with required headers
  - JSON request/response format
  - Proper HTTP status codes (200/201 for success, 403 for unauthorized)
- **BDD Test Suite**: Comprehensive behavior-driven testing with 8 scenarios
  - Behave framework integration
  - Playwright for Web UI testing (headless mode, 1024x768 viewport)
  - 56 BDD steps covering all interfaces
  - Screenshot capture on test failure
  - JUnit XML test reporting
  - Test tags: @smoke (6), @validation (1), @security (1)
- **CI/CD Pipeline**: GitHub Actions workflows for quality and releases
  - Continuous Integration workflow with matrix testing (Python 3.9, 3.10, 3.11)
  - Lint job: ruff check/format, mypy type checking
  - Test job: BDD scenario execution with artifact uploads
  - Security job: gitleaks secret scanning
  - Release workflow with SLSA Level 3 provenance generation
  - Automated GitHub releases with build artifacts
- **Documentation**: Complete getting started guide
  - Tutorial: "Getting Started with PMS" with step-by-step instructions
  - Installation guide for all platforms
  - Usage examples for Web UI, CLI, and REST API
  - Troubleshooting section
  - Priority reference table
  - Development workflow documentation
- **Sprint 1 Artifacts**: Complete planning and tracking documentation
  - Sprint 1 backlog with 27 story points (19 completed, 70%)
  - 5 user stories implemented and tested
  - Progress tracking and metrics

### Changed
- Project version bumped to 0.2.0 (first minor release)
- Development environment now includes Roundup tracker

### Technical Details
- **Testing**: 8 BDD scenarios, 56 steps, all passing
- **Coverage**: Web UI (Playwright), CLI (subprocess), API (requests)
- **Interfaces**: 3 complete interfaces for issue management
- **Story Points**: 19/27 completed (70% of Sprint 1)
- **Test Execution**: < 10 seconds for full suite

## [0.1.3] - 2025-11-15

### Added
- MIT License (LICENSE file)
- ADR-0004: Adopt MIT License and SLSA Level 1
- SPDX headers to all source and documentation files
- Copyright and license information in README.md
- SLSA Level 1 compliance plan

### Changed
- All documentation files now include SPDX-FileCopyrightText and SPDX-License-Identifier headers

## [0.1.2] - 2025-11-15

### Added
- CI/CD and Quality Automation section in ADR-0002
- Pre-commit hooks strategy documentation
- GitHub Actions CI/CD strategy
- Consistency principles between local and CI environments
- CI/CD validation criteria

### Changed
- CLAUDE.md quality gates to include GitHub Actions requirement
- Enhanced development workflow with CI/CD best practices

## [0.1.1] - 2025-11-15

### Added
- Complete 6-sprint development plan (v0.2.0 → v1.0.0)
- Sprint planning documents for all 6 sprints (206 story points total)
- Sprint overview README with metrics and timeline
- Documentation roadmap following Diátaxis framework
- Marpit presentation schedule
- BDD demonstration materials plan
- Web UI configuration (English only, 1024x768 screenshots)

### Changed
- Semantic versioning strategy to use minor version bumps per sprint (0.x.0)
- CLAUDE.md to reflect version management approach

## [0.1.0] - 2025-11-15

### Added
- Initial project structure and foundation
- Architecture Decision Records (ADR-0001, ADR-0002, ADR-0003)
- Diátaxis documentation framework structure
- Python development configuration (.gitignore, .editorconfig)
- Multi-stage pre-commit hooks (fast pre-commit, comprehensive pre-push)
- Project README with dual objectives outlined
- Documentation README following Diátaxis framework
- Directory structure for features, docs, and sprints

[Unreleased]: https://github.com/jrjsmrtn/pasture-management-system/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/jrjsmrtn/pasture-management-system/compare/v0.1.3...v0.2.0
[0.1.3]: https://github.com/jrjsmrtn/pasture-management-system/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/jrjsmrtn/pasture-management-system/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/jrjsmrtn/pasture-management-system/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/jrjsmrtn/pasture-management-system/releases/tag/v0.1.0
