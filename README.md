<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Pasture Management System (PMS)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![BDD Testing](https://img.shields.io/badge/BDD-Behave%20%2B%20Playwright-green.svg)](https://behave.readthedocs.io/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

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

**Version**: 1.0.0 (Production Release)

**Status**: Production-ready

**Key Milestones**:

- ✅ **Sprint 1-4**: Issue tracking and change management workflows
- ✅ **Sprint 5**: Complete CMDB implementation with search and filtering
- ✅ **Sprint 6**: Technical debt resolution and production readiness
- ✅ **Sprint 7**: Production release with comprehensive documentation
- 🎯 **Next**: v1.1.0 email interface (Sprint 8)

**Test Coverage**: >85% | **BDD Pass Rate**: 91% (10/11 scenarios)

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
git clone https://github.com/yourusername/pasture-management-system.git
cd pasture-management-system

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Install development dependencies (optional)
uv pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium

# Initialize database and start server
./scripts/reset-test-db.sh admin

# Access web UI
open http://localhost:9080/pms/
```

For detailed installation instructions, see the [Installation Guide](docs/howto/installation-guide.md).

## Development

This project follows professional development practices:

- **Architecture Decision Records**: See [docs/adr/](docs/adr/)
- **Sprint-based Development**: See [docs/sprints/](docs/sprints/)
- **BDD-First Testing**: Feature files in [features/](features/)
- **Semantic Versioning**: Following [semver.org](https://semver.org/)

## Architecture

Architecture documentation using C4 DSL is available in [docs/architecture/](docs/architecture/).

For a high-level overview, see [Architecture Overview](docs/explanation/architecture-overview.md).

## Installation & Deployment

- **[Installation Guide](docs/howto/installation-guide.md)**: Set up PMS in your environment (20-30 minutes)
- **[Deployment Guide](docs/howto/deployment-guide.md)**: Production deployment with reverse proxy, SSL, and monitoring
- **[Administration Guide](docs/howto/administration-guide.md)**: System administration and maintenance

## Contributing

Contributions are welcome! This project serves as both a functional tool and a BDD demonstration.

- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Contribution guidelines
- **[Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/)**: Community standards
- **[GitHub Issues](https://github.com/yourusername/pasture-management-system/issues)**: Report bugs or request features
- **[GitHub Discussions](https://github.com/yourusername/pasture-management-system/discussions)**: Ask questions

We especially welcome:

- Bug reports and fixes
- BDD scenario contributions
- Documentation improvements
- Feature implementations

## License

MIT License - see [LICENSE](LICENSE) file for details

Copyright (c) 2025 Georges Martin <jrjsmrtn@gmail.com>

## Release Information

**Current Version**: 1.0.0 (Production Release)

**Release Date**: 2025-11-20

**What's New in v1.0.0**:

- ✅ Complete issue tracking, change management, and CMDB functionality
- ✅ Comprehensive production documentation (installation, deployment, administration)
- ✅ 91% BDD test pass rate with Behave and Playwright
- ✅ Security hardening and production-ready configuration
- ✅ Performance baselines and optimization guidelines

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## Support

- **Documentation**: [docs/](docs/)
- **GitHub Issues**: [Report bugs](https://github.com/yourusername/pasture-management-system/issues)
- **GitHub Discussions**: [Ask questions](https://github.com/yourusername/pasture-management-system/discussions)
