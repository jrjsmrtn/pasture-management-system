<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Architecture Overview

**Audience**: Developers, contributors, and technical stakeholders

**Purpose**: High-level overview of PMS system architecture, design decisions, and component interactions

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Diagram](#architecture-diagram)
- [Component Overview](#component-overview)
- [Technology Stack](#technology-stack)
- [Design Patterns](#design-patterns)
- [Database Schema](#database-schema)
- [Integration Points](#integration-points)
- [Deployment Architecture](#deployment-architecture)
- [Architecture Decision Records](#architecture-decision-records)

## System Overview

The Pasture Management System (PMS) is a dual-objective project:

1. **Functional Tool**: Lightweight ITIL-inspired issue/change/CMDB management system for Homelab Sysadmins
1. **BDD Demonstration**: Showcase modern BDD testing patterns with Python, Gherkin, Behave, and Playwright

### Key Characteristics

- **Scale**: Homelab-focused (5-10 concurrent users)
- **Deployment**: Self-hosted, single-server architecture
- **Interfaces**: Web UI, CLI, and API for comprehensive BDD testing demonstration
- **Foundation**: Built on Roundup Issue Tracker Toolkit
- **Database**: SQLite (suitable for homelab scale)
- **Testing**: BDD-first development with Behave and Playwright

## Architecture Diagram

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                           Users                                 │
│     (Homelab Sysadmins, Team Members, BDD Learners)            │
└────────────┬────────────────┬───────────────┬──────────────────┘
             │                │               │
      ┌──────▼──────┐  ┌─────▼─────┐  ┌──────▼──────┐
      │   Web UI    │  │    CLI    │  │     API     │
      │ (Playwright)│  │  (Behave) │  │  (Behave)   │
      └──────┬──────┘  └─────┬─────┘  └──────┬──────┘
             │                │               │
             └────────────────┴───────────────┘
                              │
                    ┌─────────▼────────────┐
                    │  Roundup Tracker     │
                    │  ┌─────────────────┐ │
                    │  │  Customizations │ │
                    │  │  - Detectors    │ │
                    │  │  - Templates    │ │
                    │  │  - Extensions   │ │
                    │  │  - Schema       │ │
                    │  └─────────────────┘ │
                    └───────────┬──────────┘
                                │
                    ┌───────────▼──────────┐
                    │    SQLite Database   │
                    │  ┌─────────────────┐ │
                    │  │  - Issues       │ │
                    │  │  - Changes      │ │
                    │  │  - CIs (CMDB)   │ │
                    │  │  - Users        │ │
                    │  │  - Relationships│ │
                    │  └─────────────────┘ │
                    └──────────────────────┘
```

### Component Interaction Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      Request Flow                               │
└─────────────────────────────────────────────────────────────────┘

User Request (Web/CLI/API)
         │
         ▼
   Roundup Server
         │
         ├──► Detector (before/after hooks)
         │
         ├──► Template (HTML rendering)
         │
         ├──► Extension (helper functions)
         │
         ├──► Schema (data model)
         │
         ▼
   Database Operations (SQLite)
         │
         ▼
   Response (HTML/JSON/CLI output)
```

## Component Overview

### 1. Roundup Issue Tracker

**Purpose**: Core platform providing issue tracking foundation

**Responsibilities**:

- HTTP server for web UI and API
- Database abstraction layer
- User authentication and authorization
- Email integration (future: v1.1.0)
- Session management

**Location**: Installed as Python package (`roundup>=2.5.0`)

**Configuration**: `tracker/config.ini`

### 2. Customizations Layer

PMS extends Roundup with ITIL-inspired customizations.

#### 2.1 Schema (`tracker/schema.py`)

**Purpose**: Define data model for issues, changes, CIs, and relationships

**Key Classes**:

- `issue`: Issue tracking with lifecycle states
- `change`: Change request management with risk assessment
- `ci`: Configuration Items (CMDB)
- `ci_relationship`: CI dependencies and relationships
- `user`: User accounts and permissions

**Pattern**: Roundup class-based schema with properties and links

#### 2.2 Detectors (`tracker/detectors/`)

**Purpose**: Event-driven business logic (hooks)

**Key Detectors**:

- `issue_auditor.py`: Issue lifecycle validation
- `change_auditor.py`: Change approval workflows
- `nosyreaction.py`: Notification logic (future: email)

**Pattern**: Reactor pattern - detectors register for events (create, set, retire)

#### 2.3 Templates (`tracker/html/`)

**Purpose**: Web UI HTML templates

**Technology**: TAL (Template Attribute Language) via Zope's zopetal engine

**Key Templates**:

- `issue.item.html`: Issue detail page
- `change.item.html`: Change request detail page
- `ci.index.html`: CMDB dashboard with statistics
- `page.html`: Base layout template

**Pattern**: Template inheritance with macros

#### 2.4 Extensions (`tracker/extensions/`)

**Purpose**: Reusable helper functions for templates

**Key Extensions**:

- `template_helpers.py`: Sort and filter functions for CMDB
  - `sort_ci_ids()`: Sort CIs by name/type/status/criticality
  - `filter_ci_ids_by_search()`: Text search across CI fields

**Pattern**: Pure functions returning processed data

### 3. Database Layer

**Technology**: SQLite (via Roundup's anydbm backend)

**Location**: `tracker/db/`

**Files**:

- Individual `.db` files per class (e.g., `issue.db`, `change.db`, `ci.db`)
- `_ids.db`: ID sequence tracking
- `_words.db`: Full-text search index

**Schema**: Defined in `tracker/schema.py`, managed by Roundup

### 4. Testing Infrastructure

#### 4.1 BDD Tests (`features/`)

**Framework**: Behave (Gherkin scenarios)

**Structure**:

- `features/issue_tracking/`: Issue management scenarios
- `features/change_mgmt/`: Change request scenarios
- `features/cmdb/`: CMDB scenarios
- `features/steps/`: Step definitions (web_ui, cli, api)

**Tools**:

- **Playwright**: Browser automation for web UI
- **subprocess**: CLI command execution
- **requests**: API testing

#### 4.2 Unit Tests (`tests/`)

**Framework**: pytest

**Coverage**:

- Template helper unit tests
- Utility function tests
- Integration tests (planned)

### 5. Supporting Tools

#### 5.1 Scripts (`scripts/`)

**Key Scripts**:

- `reset-test-db.sh`: One-command database reset and server restart
- `backup-pms.sh`: Automated backup (production)
- `vacuum-db.sh`: Database optimization (production)

#### 5.2 Pre-commit Hooks

**Tools**:

- `ruff`: Python formatting and linting
- `mypy`: Type checking
- `mdformat`: Markdown formatting
- `yamllint`: YAML validation
- `gitleaks`: Secret detection

## Technology Stack

### Core Platform

| Component                | Technology      | Version         | Rationale                                      |
| ------------------------ | --------------- | --------------- | ---------------------------------------------- |
| **Programming Language** | Python          | 3.9+            | BDD ecosystem alignment, Roundup compatibility |
| **Issue Tracker**        | Roundup Toolkit | 2.5.0+          | Customizable, multi-interface, mature          |
| **Database**             | SQLite          | (Python stdlib) | Lightweight, homelab-appropriate               |
| **Web Server**           | Roundup Server  | (included)      | Built-in HTTP server                           |

### BDD/Testing Stack

| Component              | Technology | Version | Purpose                    |
| ---------------------- | ---------- | ------- | -------------------------- |
| **BDD Framework**      | Behave     | 1.2.6+  | Gherkin scenario execution |
| **Browser Automation** | Playwright | 1.40.0+ | Modern web UI testing      |
| **Unit Testing**       | pytest     | 8.3.0+  | Implementation testing     |
| **HTTP Testing**       | requests   | 2.31.0+ | API testing                |

### Code Quality

| Component            | Technology | Version | Purpose                        |
| -------------------- | ---------- | ------- | ------------------------------ |
| **Formatter/Linter** | ruff       | 0.14.5  | Fast Python formatting/linting |
| **Type Checker**     | mypy       | 1.11.2+ | Static type checking           |
| **Pre-commit**       | pre-commit | 3.6.0+  | Automated quality checks       |

### Documentation

| Component         | Technology           | Purpose                  |
| ----------------- | -------------------- | ------------------------ |
| **Markdown**      | CommonMark           | All documentation        |
| **Architecture**  | C4 DSL (Structurizr) | Architecture diagrams    |
| **Presentations** | Marpit               | BDD demonstration slides |

**Rationale**: See [ADR-0003: Use Python with Roundup Issue Tracker](../adr/0003-use-python-with-roundup-issue-tracker.md)

## Design Patterns

### 1. Reactor Pattern (Detectors)

**Purpose**: Event-driven business logic without coupling

**Implementation**: Roundup detectors register for database events

**Example**:

```python
def init(db):
    db.issue.react('create', new_issue_notification)
    db.issue.react('set', status_change_validation)
```

**Benefits**:

- Separation of concerns
- Extensible without modifying core
- Testable in isolation

### 2. Template View Pattern

**Purpose**: Separate presentation from logic

**Implementation**: TAL templates with helper functions

**Example**:

```html
<tal:block tal:repeat="ci sorted_cis">
  <tr tal:define="ci_id ci">
    <td tal:content="ci/name">CI Name</td>
  </tr>
</tal:block>
```

**Benefits**:

- Clear separation of presentation and data
- Reusable template fragments via macros
- Testable helper functions

### 3. Data Access Object (DAO) Pattern

**Purpose**: Abstract database operations

**Implementation**: Roundup's built-in class-based database access

**Example**:

```python
# Read
issue = db.issue.get('42', 'title')

# Create
issue_id = db.issue.create(title="New issue", status="open")

# Update
db.issue.set('42', status="resolved")
```

**Benefits**:

- Database-agnostic code
- Transaction management
- Type-safe access

### 4. Page Object Pattern (BDD Testing)

**Purpose**: Encapsulate page interactions for maintainability

**Implementation**: Playwright page object approach

**Example**:

```python
class IssuePage:
    def __init__(self, page):
        self.page = page

    def navigate_to(self, issue_id):
        self.page.goto(f"/pms/issue{issue_id}")

    def get_status(self):
        return self.page.locator('[data-test="status"]').text_content()
```

**Benefits**:

- Reusable page interactions
- Maintainable test code
- Reduced duplication

### 5. Fixture Pattern (BDD Testing)

**Purpose**: Setup and teardown with automatic cleanup

**Implementation**: Behave's `use_fixture()` pattern

**Example**:

```python
@fixture
def browser_context(context):
    context.browser = playwright.chromium.launch()
    yield context.browser
    context.browser.close()  # Automatic cleanup
```

**Benefits**:

- Guaranteed cleanup
- Isolated test state
- Composable fixtures

For comprehensive BDD patterns, see [BDD Testing Best Practices](../reference/bdd-testing-best-practices.md).

## Database Schema

### Core Classes

#### 1. Issue

**Purpose**: Track problems, incidents, and tasks

**Key Properties**:

- `title`: Issue summary
- `status`: Open, in-progress, resolved, closed
- `priority`: Low, normal, high, critical
- `assignedto`: User responsible
- `description`: Detailed description

**Relationships**:

- Links to `change` (related changes)
- Links to `ci` (affected configuration items)

#### 2. Change

**Purpose**: Manage change requests with approval workflow

**Key Properties**:

- `title`: Change summary
- `status`: Draft, submitted, approved, rejected, implemented
- `risk_level`: Low, medium, high
- `impact_assessment`: Description of potential impact
- `rollback_plan`: Procedure if change fails

**Relationships**:

- Links to `issue` (related issues)
- Links to `ci` (affected CIs)

#### 3. CI (Configuration Item)

**Purpose**: CMDB - track infrastructure components

**Key Properties**:

- `name`: CI identifier
- `ci_type`: Server, network, storage, application, database
- `status`: Active, inactive, maintenance, decommissioned
- `criticality`: Low, medium, high, critical
- `location`: Physical or logical location
- `ip_address`: Network address
- `description`: Detailed information

**Relationships**:

- Links to `ci_relationship` (dependencies)
- Links to `issue` (related issues)
- Links to `change` (related changes)

#### 4. CI Relationship

**Purpose**: Model dependencies between configuration items

**Key Properties**:

- `source_ci`: Source CI
- `target_ci`: Target CI
- `relationship_type`: Depends on, hosts, connects to, backup of

#### 5. User

**Purpose**: User accounts and authentication

**Key Properties**:

- `username`: Unique identifier
- `realname`: Display name
- `roles`: Admin, User
- `email`: Contact address

### Schema Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    Issue    │───────│   Change    │───────│     CI      │
│             │       │             │       │             │
│ - title     │       │ - title     │       │ - name      │
│ - status    │       │ - status    │       │ - ci_type   │
│ - priority  │       │ - risk_level│       │ - status    │
│ - assignedto│       │ - impact    │       │ - criticality│
└──────┬──────┘       └─────────────┘       └──────┬──────┘
       │                                            │
       │                                            │
       │              ┌─────────────┐              │
       └──────────────│     User    │──────────────┘
                      │             │
                      │ - username  │
                      │ - realname  │
                      │ - roles     │
                      └─────────────┘

        ┌─────────────────────┐
        │  CI Relationship    │
        │                     │
        │ - source_ci    ────────┐
        │ - target_ci    ────────┤
        │ - relationship_type    │
        └─────────────────────┬──┘
                              │
                     (Models CI dependencies)
```

## Integration Points

### 1. Web UI

**Technology**: Roundup web interface (HTTP)

**Port**: 9080 (default)

**URL Pattern**: `http://localhost:9080/pms/{class}{id}`

**Authentication**: Cookie-based sessions

**Testing**: Playwright browser automation

### 2. CLI

**Tool**: `roundup-admin` command

**Usage**: Database administration, bulk operations

**Example**: `roundup-admin -i tracker list issue`

**Testing**: Subprocess execution in BDD scenarios

### 3. API

**Technology**: Roundup XML-RPC API (future: REST)

**Endpoint**: `/xmlrpc` (under tracker URL)

**Authentication**: HTTP Basic or API tokens

**Testing**: `requests` library in BDD scenarios

### 4. Email (Future - v1.1.0)

**Tool**: `roundup-mailgw` gateway

**Protocol**: SMTP, IMAP

**Use Cases**:

- Create issues via email
- Reply to notifications
- Email-to-ticket integration

**Testing**: Greenmail or Python SMTP testing (planned)

## Deployment Architecture

### Development

```
┌────────────────────────────────────────┐
│  Development Machine (localhost)      │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │  Roundup Server (foreground)     │ │
│  │  Port: 9080                      │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │  SQLite Database (tracker/db/)   │ │
│  │  Reset frequently for testing    │ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘
```

### Production (Single Server)

```
┌────────────────────────────────────────────────────┐
│  Production Server                                 │
│                                                    │
│  ┌──────────────────────────────────────────────┐ │
│  │  Reverse Proxy (nginx/Apache)                │ │
│  │  - HTTPS/SSL termination                     │ │
│  │  - Port 443 → 9080                          │ │
│  └────────────────┬─────────────────────────────┘ │
│                   │                               │
│  ┌────────────────▼─────────────────────────────┐ │
│  │  Roundup Server (systemd service)           │ │
│  │  - Port 9080 (localhost only)               │ │
│  │  - Auto-restart on failure                  │ │
│  └────────────────┬─────────────────────────────┘ │
│                   │                               │
│  ┌────────────────▼─────────────────────────────┐ │
│  │  SQLite Database                             │ │
│  │  - WAL mode enabled                         │ │
│  │  - Daily backups                            │ │
│  └──────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────┘
```

For detailed deployment patterns, see [Deployment Guide](../howto/deployment-guide.md).

## Architecture Decision Records

All significant architectural decisions are documented as ADRs:

### Core Decisions

- **[ADR-0001](../adr/0001-record-architecture-decisions.md)**: Record architecture decisions

  - Rationale: Document decision history for future maintainers
  - Status: Accepted

- **[ADR-0002](../adr/0002-adopt-development-best-practices.md)**: Adopt development best practices

  - Rationale: BDD-first, semantic versioning, Diátaxis documentation
  - Status: Accepted

- **[ADR-0003](../adr/0003-use-python-with-roundup-issue-tracker.md)**: Use Python with Roundup Issue Tracker

  - Rationale: Python BDD ecosystem, Roundup customizability, homelab scale
  - Status: Accepted

- **[ADR-0004](../adr/0004-adopt-mit-license-and-slsa-level-1.md)**: Adopt MIT License and SLSA Level 1

  - Rationale: Open source, supply chain security
  - Status: Accepted

### ADR Index

For the complete list of architectural decisions, see the [ADR directory](../adr/).

## Related Documentation

### Architecture

- **[ADRs](../adr/)**: Architectural Decision Records
- **[C4 Models](../architecture/)**: Architecture diagrams (DSL)

### Development

- **[Roundup Development Practices](../reference/roundup-development-practices.md)**: Roundup-specific development patterns
- **[BDD Testing Best Practices](../reference/bdd-testing-best-practices.md)**: Comprehensive BDD testing guide
- **[CONTRIBUTING.md](../../CONTRIBUTING.md)**: Contribution guidelines

### Operations

- **[Installation Guide](../howto/installation-guide.md)**: Setup procedures
- **[Deployment Guide](../howto/deployment-guide.md)**: Production deployment
- **[Administration Guide](../howto/administration-guide.md)**: System administration

______________________________________________________________________

**Document Version**: 1.0.0
**Last Updated**: 2025-11-20
**Maintained By**: PMS Team
