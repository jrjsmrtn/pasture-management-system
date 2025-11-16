<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Changelog

All notable changes to the Pasture Management System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2025-11-16

### Added

- **Change Approval Workflow**: Complete ITIL-inspired change approval process (Story 1)
  - 8 change statuses: Planning, Assessment, Approved, Rejected, Scheduled, Implementing, Completed, Cancelled
  - Status transition validation with enforced workflow rules
  - Approval and rejection with required notes/reasons
  - Status history tracking for full audit trail
  - Context-sensitive workflow buttons in Web UI
  - 11 BDD scenarios covering all workflow transitions (Web UI, CLI, API)
- **Change-Issue Linking**: Bi-directional relationships between changes and issues (Story 2)
  - Link changes to one or more issues
  - View related changes from issue details
  - View related issues from change details
  - Support for multiple issues per change
  - Orphan handling when issues are deleted
  - 8 BDD scenarios for linking workflows
- **Change Risk Assessment**: Document risk and impact before approval (Story 3)
  - Impact assessment field (service impact, affected systems, downtime estimates)
  - Risk assessment field (likelihood, impact, mitigation strategies)
  - Risk levels: Very Low, Low, Medium, High, Very High
  - Validation requires impact/risk before approval
  - High-risk changes require detailed mitigation plans
  - 9 BDD scenarios for risk assessment workflows
- **Change Scheduling**: Schedule changes for maintenance windows (Story 4)
  - Scheduled start and end time fields
  - Scheduled status with calendar integration readiness
  - Rescheduling support with history preservation
  - Time validation (end must be after start)
  - Actual vs. scheduled time tracking
  - 10 BDD scenarios for scheduling workflows
- **Change Implementation Tracking**: Track actual implementation and outcomes (Story 5)
  - Actual start/end time auto-tracking on status transitions
  - Implementation notes field for real-time documentation
  - Implementation outcome tracking (success, success with deviations)
  - Deviation notes for documenting plan variances
  - Rollback tracking with reason and notes
  - 14 BDD scenarios for implementation tracking
- **Comprehensive Documentation**: Complete Diátaxis-compliant documentation (5 points)
  - Tutorial: "Managing Changes in Your Homelab" (329 lines) - 30-minute hands-on walkthrough
  - How-to: "Submitting a Change Request" (331 lines) - Quick reference for all interfaces
  - How-to: "Assessing Change Risk" (430 lines) - Risk/impact assessment framework
  - Reference: "Change Workflow States" (735 lines) - Complete technical specification
  - Explanation: "ITIL Change Management Principles" (945 lines) - Methodology and philosophy
  - Marpit Presentation: "BDD Testing in Practice" (942 lines, 40+ slides) - BDD demonstration
- **BDD Validation**: Pre-push hook to catch ambiguous step definitions
  - `behave --dry-run` validation before push
  - Detects AmbiguousStep errors early
  - Allows undefined steps for incremental development
  - Fast feedback loop (prevents CI failures)

### Changed

- Extended change list step definitions to support scheduling fields
- Centralized common step definitions to avoid ambiguity
- Sprint tracking: 33/33 story points (100% complete)
- Project version bumped to 0.4.0 (Sprint 3 complete)

### Fixed

- Resolved 11 ambiguous step definition conflicts across feature files
- Fixed duplicate step definitions in change workflow, risk, and issue linking modules
- Corrected step definition organization for better maintainability

### Technical Details

- **Story Points**: 33/33 completed (100% of Sprint 3)
- **BDD Scenarios**: 52 scenarios, all passing or dry-run validated
  - Change workflow: 11 scenarios ✅
  - Change-issue links: 8 scenarios ✅
  - Change risk: 9 scenarios ✅
  - Change scheduling: 10 scenarios ✅
  - Change implementation: 14 scenarios ✅
- **Coverage**: Web UI (22 scenarios), CLI (15 scenarios), API (15 scenarios)
- **Step Definitions**: ~1,500 lines of step definitions added
- **Documentation**: 3,712 lines of Diátaxis-compliant documentation
- **New Files**:
  - `features/change_mgmt/change_workflow.feature` - Workflow scenarios
  - `features/change_mgmt/change_issue_links.feature` - Linking scenarios
  - `features/change_mgmt/change_risk.feature` - Risk assessment scenarios
  - `features/change_mgmt/change_scheduling.feature` - Scheduling scenarios
  - `features/change_mgmt/change_implementation.feature` - Implementation scenarios
  - `features/steps/change_workflow_steps.py` - Workflow step definitions (280+ lines)
  - `features/steps/change_issue_link_steps.py` - Linking step definitions (200+ lines)
  - `features/steps/change_risk_steps.py` - Risk step definitions (360+ lines)
  - `features/steps/change_scheduling_steps.py` - Scheduling step definitions (260+ lines)
  - `features/steps/change_implementation_steps.py` - Implementation step definitions (320+ lines)
  - `docs/tutorials/managing-changes-homelab.md` - Change management tutorial
  - `docs/howto/submit-change-request.md` - Change creation guide
  - `docs/howto/assess-change-risk.md` - Risk assessment guide
  - `docs/reference/change-workflow-states.md` - Workflow reference
  - `docs/explanation/itil-change-management-principles.md` - ITIL principles
  - `docs/presentations/bdd-testing-in-practice.md` - BDD presentation
- **ITIL Alignment**: Complete change management workflow following ITIL 4 best practices
- **BDD Demonstration**: Comprehensive showcase of BDD testing with Gherkin, Behave, and Playwright

## [0.3.0] - 2025-11-16

### Added

- **ITIL Workflow Implementation**: Complete issue lifecycle management with status transitions (Story 1)
  - Four statuses: New, In Progress, Resolved, Closed
  - Status transition validation detector enforcing ITIL workflow rules
  - Context-sensitive workflow buttons in Web UI
  - Complete status history tracking with audit trail
  - 7 BDD scenarios covering all interfaces (Web UI, CLI, API)
- **Issue Assignment**: Assign issues to specific users for accountability (Story 2)
  - Assignee field with user dropdown selection
  - Filter and sort issues by assignee
  - "Unassigned" filter for finding work
  - 4 BDD scenarios for assignment workflows
- **Change Management Schema**: Dedicated change request tracking (Story 3)
  - Change class with ITIL-inspired fields (description, justification, impact, risk)
  - Change priorities: Low, Medium, High, Critical
  - Change categories: Software, Hardware, Configuration, Network
  - Change statuses: Planning, Approved, Implementing, Completed, Cancelled
  - Link changes to related issues
  - 4 BDD scenarios for schema validation
- **Change Request Creation**: Create and manage infrastructure changes (Story 4)
  - Web UI form with required fields (title, justification, priority, category)
  - Field validation for data quality
  - CLI and API support for change creation
  - 4 BDD scenarios across all interfaces
- **Change List View**: Browse and filter change requests (Story 5)
  - Change index template with sorting and filtering
  - Filter by status, priority, and category
  - Sort by priority and creation date
  - Empty state messaging and "Create New Change" button
  - 12 BDD scenarios (7 Web UI, 2 CLI, 3 API)
- **Documentation**: Comprehensive tutorials and reference guides
  - Tutorial: "Understanding ITIL Workflows" - Learn issue lifecycle concepts
  - Reference: "Issue Status Transitions" - Complete transition matrix and implementation details
  - Reference: "Change Request Schema" - Full field specifications and examples
- **Enhanced Testing**: Expanded BDD test coverage
  - 31 total BDD scenarios (155% of 20+ target)
  - Coverage across Web UI (Playwright), CLI (roundup-admin), and API (REST)
  - Default login step for simplified test scenarios

### Changed

- Status workflow enforces valid transitions (prevents invalid jumps like New → Closed)
- Issue creation now requires priority field for data quality
- Web UI displays context-sensitive workflow buttons based on current status
- Project version bumped to 0.3.0 (Sprint 2 complete)

### Technical Details

- **Story Points**: 22/27 completed (81% of Sprint 2, 5 points documentation)
- **BDD Scenarios**: 31 scenarios, all passing or dry-run validated
  - Issue workflow: 7 scenarios ✅
  - Assign issues: 4 scenarios ✅
  - Change schema: 4 scenarios ✅
  - Create change: 4 scenarios ✅
  - View changes: 12 scenarios ✅
- **New Files**:
  - `tracker/detectors/status_workflow.py` - Status transition validation
  - `tracker/html/change.item.html` - Change creation form
  - `tracker/html/change.index.html` - Change list view
  - `features/steps/workflow_steps.py` - Issue workflow step definitions
  - `features/steps/assignment_steps.py` - Assignment step definitions
  - `features/steps/change_schema_steps.py` - Change schema step definitions
  - `features/steps/change_creation_steps.py` - Change creation step definitions
  - `features/steps/change_list_steps.py` - Change list step definitions
  - `docs/tutorials/understanding-itil-workflows.md`
  - `docs/reference/status-transitions.md`
  - `docs/reference/change-schema.md`
- **Database Schema**: Extended with change management classes
- **ITIL Alignment**: Issue and change workflows follow ITIL best practices

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

[0.1.0]: https://github.com/jrjsmrtn/pasture-management-system/releases/tag/v0.1.0
[0.1.1]: https://github.com/jrjsmrtn/pasture-management-system/compare/v0.1.0...v0.1.1
[0.1.2]: https://github.com/jrjsmrtn/pasture-management-system/compare/v0.1.1...v0.1.2
[0.1.3]: https://github.com/jrjsmrtn/pasture-management-system/compare/v0.1.2...v0.1.3
[0.2.0]: https://github.com/jrjsmrtn/pasture-management-system/compare/v0.1.3...v0.2.0
[0.3.0]: https://github.com/jrjsmrtn/pasture-management-system/compare/v0.2.0...v0.3.0
[0.4.0]: https://github.com/jrjsmrtn/pasture-management-system/compare/v0.3.0...v0.4.0
[unreleased]: https://github.com/jrjsmrtn/pasture-management-system/compare/v0.4.0...HEAD
