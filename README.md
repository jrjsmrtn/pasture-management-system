<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Pasture Management System (PMS)

A lightweight ITIL-inspired issue/change/CMDB management system for Homelab Sysadmins, built on the Roundup Issue Tracker toolkit.

## Dual Project Objectives

1. **Functional Tool**: Implement a practical issue tracking and change management system for homelab environments
1. **BDD Demonstration**: Showcase the power of Behavior-Driven Development (BDD) with Python, Gherkin, Behave, and Playwright testing

## Key Features

- **ITIL-Inspired Workflows**: Issue tracking, change management, and CMDB
- **Multiple Interfaces**: Web UI, CLI, and API for maximum flexibility
- **Homelab Scale**: Lightweight and self-hosted for privacy and control
- **BDD-First Development**: Comprehensive Gherkin scenarios demonstrating modern testing practices
- **Educational Resource**: Real-world examples of BDD testing across web, CLI, and API interfaces

## Project Status

**Version**: 0.6.0 (Sprint 5 Complete - CMDB Implementation)

**Current Sprint**: Sprint 6 - Technical Debt Resolution and Production Readiness

**Key Milestones**:

- ✅ **Sprint 1-4**: Issue tracking and change management workflows
- ✅ **Sprint 5**: Complete CMDB implementation with search and filtering
- 🔄 **Sprint 6** (In Progress): BDD test infrastructure improvements and bug fixes
- 🎯 **Target**: v1.0.0 production release

**Test Coverage**: >85% | **BDD Pass Rate**: 58% (7/12 scenarios in ci_search)

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and [docs/sprints/](docs/sprints/) for sprint progress.

## Documentation

Comprehensive documentation following the [Diátaxis](https://diataxis.fr/) framework:

- **[Tutorials](docs/tutorials/)**: Step-by-step guides for getting started
- **[How-to Guides](docs/howto/)**: Task-oriented recipes
- **[Reference](docs/reference/)**: Technical reference material
- **[Explanation](docs/explanation/)**: Conceptual understanding

See [docs/README.md](docs/README.md) for complete documentation index.

## Technology Stack

- **Python 3.9+**: Core development language
- **Roundup Issue Tracker Toolkit**: Customizable issue tracking foundation
- **Behave**: Python BDD framework for Gherkin scenarios
- **Playwright**: Modern browser automation for web UI testing
- **pytest**: Unit and integration testing

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd pasture-management-system

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (when available)
pip install -r requirements.txt

# See documentation for detailed setup
```

## Development

This project follows professional development practices:

- **Architecture Decision Records**: See [docs/adr/](docs/adr/)
- **Sprint-based Development**: See [docs/sprints/](docs/sprints/)
- **BDD-First Testing**: Feature files in [features/](features/)
- **Semantic Versioning**: Following [semver.org](https://semver.org/)

## Architecture

Architecture documentation using C4 DSL is available in [docs/architecture/](docs/architecture/).

For a high-level overview, see [Architecture Explanation](docs/explanation/architecture-overview.md).

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details

Copyright (c) 2025 Georges Martin <jrjsmrtn@gmail.com>

## Contact

[To be determined]
